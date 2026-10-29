import math
from collections import Counter, defaultdict


class EmergenceOrgan:
    """
    Computes EIX:
        EIX = (1/Z) * ( λ_S * D_KL(P_obs || P_pred)
                       + λ_I * sum_i I(S_i; S_-i)
                       - λ_R * (1/C(n,2)) * sum_{i<j} I(S_i; S_j) )
    """

    def __init__(self,
                 lambda_S=1.0,
                 lambda_I=1.0,
                 lambda_R=1.0):
        self.lambda_S = lambda_S
        self.lambda_I = lambda_I
        self.lambda_R = lambda_R

        # history of system states per tick
        self.system_states = []  # list of dicts: {"lex": [...], "concept": [...], "pressure": [...], "heart": [...]}

    # ----------------------------------------------------------
    # called once per tick with what recursion produced
    # ----------------------------------------------------------
    def observe_tick(self, recursion_layer3, tick_emit, heart_scores):
        """
        recursion_layer3: list of tokens (words + *_concept)
        tick_emit: dict with 'pressure' etc.
        heart_scores: list of floats aligned with recursion_layer3
        """
        lex = []
        concept = []
        for t in recursion_layer3:
            if isinstance(t, str) and t.endswith("_concept"):
                concept.append(t)
            else:
                lex.append(t)

        pressure = tick_emit.get("pressure", 0.0)
        # simple binning for pressure & heart
        def bin_val(x, bins=(0.2, 0.4, 0.6, 0.8)):
            for i, b in enumerate(bins):
                if x < b:
                    return i
            return len(bins)

        pressure_bin = bin_val(pressure)
        heart_bins = [bin_val(h) for h in heart_scores] if heart_scores else []

        self.system_states.append({
            "lex": lex,
            "concept": concept,
            "pressure_bin": pressure_bin,
            "heart_bins": heart_bins,
        })

    # ----------------------------------------------------------
    # helper: empirical distribution over system patterns
    # ----------------------------------------------------------
    def _build_P_obs(self):
        # compress each state to a simple pattern: (lex_count, concept_count, pressure_bin)
        patterns = []
        for s in self.system_states:
            patterns.append((
                len(s["lex"]),
                len(s["concept"]),
                s["pressure_bin"],
            ))
        total = len(patterns)
        c = Counter(patterns)
        return {p: count / total for p, count in c.items()}

    def _build_P_pred(self, P_obs):
        # simple factorized baseline: independent marginals
        # P_pred( (a,b,c) ) = P_lex_count(a) * P_concept_count(b) * P_pressure_bin(c)
        lex_counts = Counter(p[0] for p in P_obs.keys())
        concept_counts = Counter(p[1] for p in P_obs.keys())
        pressure_bins = Counter(p[2] for p in P_obs.keys())
        total = sum(lex_counts.values())

        P_lex = {k: v / total for k, v in lex_counts.items()}
        P_concept = {k: v / total for k, v in concept_counts.items()}
        P_press = {k: v / total for k, v in pressure_bins.items()}

        P_pred = {}
        for (a, b, c) in P_obs.keys():
            P_pred[(a, b, c)] = P_lex.get(a, 1e-9) * P_concept.get(b, 1e-9) * P_press.get(c, 1e-9)
        return P_pred

    def _D_KL(self, P_obs, P_pred):
        kl = 0.0
        for s, p in P_obs.items():
            q = P_pred.get(s, 1e-9)
            kl += p * math.log(p / q + 1e-12)
        return kl

    # ----------------------------------------------------------
    # mutual information helpers
    # ----------------------------------------------------------
    def _empirical_var(self, extractor):
        vals = [extractor(s) for s in self.system_states]
        total = len(vals)
        c = Counter(vals)
        return {v: count / total for v, count in c.items()}

    def _empirical_joint(self, extractorA, extractorB):
        pairs = [(extractorA(s), extractorB(s)) for s in self.system_states]
        total = len(pairs)
        c = Counter(pairs)
        return {p: count / total for p, count in c.items()}

    def _I(self, extractorA, extractorB):
        PA = self._empirical_var(extractorA)
        PB = self._empirical_var(extractorB)
        PAB = self._empirical_joint(extractorA, extractorB)
        mi = 0.0
        for (a, b), pab in PAB.items():
            pa = PA.get(a, 1e-9)
            pb = PB.get(b, 1e-9)
            mi += pab * math.log(pab / (pa * pb + 1e-12) + 1e-12)
        return mi

    # ----------------------------------------------------------
    # main: compute EIX
    # ----------------------------------------------------------
    def compute_EIX(self):
        if len(self.system_states) < 10:
            return 0.0  # need some history

        P_obs = self._build_P_obs()
        P_pred = self._build_P_pred(P_obs)
        D_kl = self._D_KL(P_obs, P_pred)

        # define subsystems S1..S4
        # S1: lex_count
        # S2: concept_count
        # S3: pressure_bin
        # S4: avg_heart_bin
        def S1(s): return len(s["lex"])
        def S2(s): return len(s["concept"])
        def S3(s): return s["pressure_bin"]
        def S4(s): return sum(s["heart_bins"]) / max(len(s["heart_bins"]), 1)

        subs = [S1, S2, S3, S4]
        n = len(subs)

        # integration: sum_i I(S_i; S_-i)
        def S_minus_i(i):
            def extractor(s):
                return tuple(f(s) for j, f in enumerate(subs) if j != i)
            return extractor

        I_integrate = 0.0
        for i, Si in enumerate(subs):
            I_integrate += self._I(Si, S_minus_i(i))

        # redundancy: average pairwise I(S_i; S_j)
        I_pairs = 0.0
        count_pairs = 0
        for i in range(n):
            for j in range(i + 1, n):
                I_pairs += self._I(subs[i], subs[j])
                count_pairs += 1
        I_pairs_avg = I_pairs / max(count_pairs, 1)

        Z = self.lambda_S + self.lambda_I + self.lambda_R
        EIX = (1.0 / Z) * (
            self.lambda_S * D_kl
            + self.lambda_I * I_integrate
            - self.lambda_R * I_pairs_avg
        )
        return EIX
