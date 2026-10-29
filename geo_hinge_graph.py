# geo_hinge_graph.py
# Continental strategic hinge graph for movement, staging, fallback, and future planning

from collections import deque


class Region:
    def __init__(self, name, pos):
        self.name = name
        self.pos = pos
        self.adj = []


def build_hinge_graph():
    g = {}
    
    g["BERLIN"]      = Region("BERLIN",      (52.5200, 13.4050))
    # ============================================================
    # FRANCE CORE + LEGACY REGIONS
    # ============================================================
    g["PARIS"]       = Region("PARIS",       (48.85, 2.35))
    g["AMIENS"]      = Region("AMIENS",      (49.89, 2.30))
    g["LILLE"]       = Region("LILLE",       (50.63, 3.06))
    g["REIMS"]       = Region("REIMS",       (49.26, 4.03))
    g["METZ"]        = Region("METZ",        (49.12, 6.18))
    g["DIJON"]       = Region("DIJON",       (47.32, 5.04))
    g["BESANCON"]    = Region("BESANCON",    (47.24, 6.02))

    # Legacy France nodes
    g["COMPIEGNE"]   = Region("COMPIEGNE",   (49.42, 2.82))
    g["SOISSONS"]    = Region("SOISSONS",    (49.38, 3.32))
    g["CHALONS"]     = Region("CHALONS",     (48.95, 4.36))
    g["EPERNAY"]     = Region("EPERNAY",     (49.04, 3.95))
    g["CALAIS"]      = Region("CALAIS",      (50.95, 1.85))
    g["DUNKIRK"]     = Region("DUNKIRK",     (51.03, 2.37))
    g["BOULOGNE"]    = Region("BOULOGNE",    (50.72, 1.61))
    g["ROUEN"]       = Region("ROUEN",       (49.44, 1.10))
    g["ORLEANS"]     = Region("ORLEANS",     (47.90, 1.91))
    g["TROYES"]      = Region("TROYES",      (48.30, 4.08))
    g["STRASBOURG"]  = Region("STRASBOURG",  (48.58, 7.75))
    g["MULHOUSE"]    = Region("MULHOUSE",    (47.75, 7.34))

    # ============================================================
    # BELGIUM / NETHERLANDS
    # ============================================================
    g["GHENT"]       = Region("GHENT",       (51.05, 3.72))
    g["ANTWERP"]     = Region("ANTWERP",     (51.22, 4.40))
    g["EINDHOVEN"]   = Region("EINDHOVEN",   (51.44, 5.47))
    g["ARNHEM"]      = Region("ARNHEM",      (51.98, 5.91))

    # ============================================================
    # RHINE / WESTERN GERMANY
    # ============================================================
    g["SAARBRUCKEN"] = Region("SAARBRUCKEN", (49.23, 7.00))
    g["KAISERSLAUTERN"] = Region("KAISERSLAUTERN", (49.44, 7.77))
    g["MANNHEIM"]    = Region("MANNHEIM",    (49.49, 8.47))
    g["HEIDELBERG"]  = Region("HEIDELBERG",  (49.41, 8.71))
    g["FRANKFURT"]   = Region("FRANKFURT",   (50.11, 8.68))
    g["FULDA"]       = Region("FULDA",       (50.55, 9.68))
    g["ERFURT"]      = Region("ERFURT",      (50.98, 11.03))

    # ============================================================
    # GERMANY NORTH / CENTRAL
    # ============================================================
    g["MUNSTER"]     = Region("MUNSTER",     (51.96, 7.63))
    g["OSNABRUCK"]   = Region("OSNABRUCK",   (52.28, 8.05))
    g["BREMEN"]      = Region("BREMEN",      (53.08, 8.80))
    g["HAMBURG"]     = Region("HAMBURG",     (53.55, 10.00))
    g["LUBECK"]      = Region("LUBECK",      (53.87, 10.69))
    g["SCHWERIN"]    = Region("SCHWERIN",    (53.63, 11.41))
    g["ROSTOCK"]     = Region("ROSTOCK",     (54.09, 12.10))
    g["STETTIN"]     = Region("STETTIN",     (53.43, 14.55))
    g["LEIPZIG"]     = Region("LEIPZIG",     (51.34, 12.37))
    g["DRESDEN"]     = Region("DRESDEN",     (51.05, 13.74))
    g["GORLITZ"]     = Region("GORLITZ",     (51.15, 14.99))
    g["WROCLAW"]     = Region("WROCLAW",     (51.11, 17.03))
    g["OPOLE"]       = Region("OPOLE",       (50.67, 17.93))

    # ============================================================
    # GERMANY SOUTH / ALPS
    # ============================================================
    g["MUNICH"]      = Region("MUNICH",      (48.13, 11.58))
    g["LANDSHUT"]    = Region("LANDSHUT",    (48.53, 12.15))
    g["REGENSBURG"]  = Region("REGENSBURG",  (49.02, 12.10))

    # ============================================================
    # SWITZERLAND / ALPINE
    # ============================================================
    g["BALE"]        = Region("BALE",        (47.56, 7.59))
    g["ZURICH"]      = Region("ZURICH",      (47.37, 8.54))
    g["ST_GALLEN"]   = Region("ST_GALLEN",   (47.42, 9.37))
    g["LINDAU"]      = Region("LINDAU",      (47.55, 9.68))

    # ============================================================
    # CZECHIA
    # ============================================================
    g["PILSEN"]      = Region("PILSEN",      (49.75, 13.38))
    g["PRAGUE"]      = Region("PRAGUE",      (50.08, 14.43))
    g["KOLIN"]       = Region("KOLIN",       (50.03, 15.20))
    g["PARDUBICE"]   = Region("PARDUBICE",   (50.04, 15.78))
    g["OLOMOUC"]     = Region("OLOMOUC",     (49.59, 17.25))
    g["OSTRAVA"]     = Region("OSTRAVA",     (49.83, 18.29))

    # ============================================================
    # POLAND
    # ============================================================
    g["POZNAN"]      = Region("POZNAN",      (52.41, 16.93))
    g["BYDGOSZCZ"]   = Region("BYDGOSZCZ",   (53.12, 18.00))
    g["TORUN"]       = Region("TORUN",       (53.01, 18.60))
    g["WARSAW"]      = Region("WARSAW",      (52.23, 21.01))
    g["BIALYSTOK"]   = Region("BIALYSTOK",   (53.13, 23.16))
    g["RADOM"]       = Region("RADOM",       (51.40, 21.16))
    g["SIEDLCE"]     = Region("SIEDLCE",     (52.17, 22.28))
    g["KATOWICE"]    = Region("KATOWICE",    (50.26, 19.02))
    g["CZESTOCHOWA"] = Region("CZESTOCHOWA", (50.81, 19.12))
    g["KRAKOW"]      = Region("KRAKOW",      (50.06, 19.94))
    g["TARNOW"]      = Region("TARNOW",      (50.01, 20.99))
    g["RZESZOW"]     = Region("RZESZOW",     (50.04, 22.00))
    g["LUBLIN"]      = Region("LUBLIN",      (51.25, 22.57))

    # ============================================================
    # BELARUS / RUSSIA WEST
    # ============================================================
    g["BREST"]       = Region("BREST",       (52.10, 23.70))
    g["GRODNO"]      = Region("GRODNO",      (53.68, 23.83))
    g["MINSK"]       = Region("MINSK",       (53.90, 27.56))
    g["BORISOV"]     = Region("BORISOV",     (54.22, 28.50))
    g["ORSHA"]       = Region("ORSHA",       (54.51, 30.43))
    g["SMOLENSK"]    = Region("SMOLENSK",    (54.78, 32.04))
    g["VYAZMA"]      = Region("VYAZMA",      (55.21, 34.30))
    g["MOSCOW"]      = Region("MOSCOW",      (55.75, 37.61))

    # ============================================================
    # UK / SCANDINAVIA / ATLANTIC
    # ============================================================
    g["LONDON"]      = Region("LONDON",      (51.50, -0.12))
    g["EDINBURGH"]   = Region("EDINBURGH",   (55.95, -3.19))
    g["SCOTLAND"]    = Region("SCOTLAND",    (56.50, -4.00))
    g["BERGEN"]      = Region("BERGEN",      (60.39, 5.32))
    g["OSLO"]        = Region("OSLO",        (59.91, 10.75))
    g["TRONDHEIM"]   = Region("TRONDHEIM",   (63.43, 10.39))
    g["NORDKAPP"]    = Region("NORDKAPP",    (71.17, 25.78))
    g["ICELAND"]     = Region("ICELAND",     (64.13, -21.82))
    g["GREENLAND"]   = Region("GREENLAND",   (72.00, -40.00))
    g["AMERICA"]     = Region("AMERICA",     (40.00, -100.00))

    # ============================================================
    # ADJACENCY FUNCTION
    # ============================================================
    def link(a, b):
        g[a].adj.append(g[b])
        g[b].adj.append(g[a])

    # ============================================================
    # LEGACY FRANCE ADJACENCY
    # ============================================================
    link("PARIS", "COMPIEGNE")
    link("COMPIEGNE", "SOISSONS")
    link("SOISSONS", "REIMS")
    link("REIMS", "CHALONS")
    link("CHALONS", "EPERNAY")
    link("EPERNAY", "TROYES")
    link("TROYES", "DIJON")

    link("PARIS", "ROUEN")
    link("ROUEN", "CALAIS")
    link("CALAIS", "DUNKIRK")
    link("CALAIS", "BOULOGNE")

    link("DIJON", "STRASBOURG")
    link("STRASBOURG", "MULHOUSE")
    link("MULHOUSE", "BALE")

    link("PARIS", "ORLEANS")
    link("ORLEANS", "DIJON")

    # ============================================================
    # NORTHERN CORRIDOR
    # ============================================================
    link("PARIS", "AMIENS")
    link("AMIENS", "LILLE")
    link("LILLE", "GHENT")
    link("GHENT", "ANTWERP")
    link("ANTWERP", "EINDHOVEN")
    link("EINDHOVEN", "ARNHEM")
    link("ARNHEM", "MUNSTER")
    link("MUNSTER", "OSNABRUCK")
    link("OSNABRUCK", "BREMEN")
    link("BREMEN", "HAMBURG")
    link("HAMBURG", "LUBECK")
    link("LUBECK", "SCHWERIN")
    link("SCHWERIN", "ROSTOCK")
    link("ROSTOCK", "STETTIN")
    link("STETTIN", "POZNAN")
    link("POZNAN", "BYDGOSZCZ")
    link("BYDGOSZCZ", "TORUN")
    link("TORUN", "WARSAW")
    link("WARSAW", "BIALYSTOK")
    link("BIALYSTOK", "GRODNO")
    link("GRODNO", "MINSK")
    link("MINSK", "BORISOV")
    link("BORISOV", "SMOLENSK")
    link("SMOLENSK", "VYAZMA")
    link("VYAZMA", "MOSCOW")

    # ============================================================
    # CENTRAL CORRIDOR
    # ============================================================
    link("PARIS", "REIMS")
    link("REIMS", "METZ")
    link("METZ", "SAARBRUCKEN")
    link("SAARBRUCKEN", "KAISERSLAUTERN")
    link("KAISERSLAUTERN", "MANNHEIM")
    link("MANNHEIM", "HEIDELBERG")
    link("HEIDELBERG", "FRANKFURT")
    link("FRANKFURT", "FULDA")
    link("FULDA", "ERFURT")
    link("ERFURT", "LEIPZIG")
    link("LEIPZIG", "DRESDEN")
    link("DRESDEN", "GORLITZ")
    link("GORLITZ", "WROCLAW")
    link("WROCLAW", "OPOLE")
    link("OPOLE", "KATOWICE")
    link("KATOWICE", "CZESTOCHOWA")
    link("CZESTOCHOWA", "RADOM")
    link("RADOM", "WARSAW")
    link("WARSAW", "SIEDLCE")
    link("SIEDLCE", "BREST")
    link("BREST", "MINSK")
    link("MINSK", "ORSHA")
    link("ORSHA", "SMOLENSK")
    link("SMOLENSK", "VYAZMA")
    link("VYAZMA", "MOSCOW")

    link("LILLE", "REIMS")
    link("FRANKFURT", "MANNHEIM")
    link("FRANKFURT", "MUNSTER")

    # ============================================================
    # SOUTHERN CORRIDOR
    # ============================================================
    link("PARIS", "DIJON")
    link("DIJON", "BESANCON")
    link("BESANCON", "BALE")
    link("BALE", "ZURICH")
    link("ZURICH", "ST_GALLEN")
    link("ST_GALLEN", "LINDAU")
    link("LINDAU", "MUNICH")
    link("MUNICH", "LANDSHUT")
    link("LANDSHUT", "REGENSBURG")
    link("REGENSBURG", "PILSEN")
    link("PILSEN", "PRAGUE")
    link("PRAGUE", "KOLIN")
    link("KOLIN", "PARDUBICE")
    link("PARDUBICE", "OLOMOUC")
    link("OLOMOUC", "OSTRAVA")
    link("OSTRAVA", "KATOWICE")
    link("KATOWICE", "KRAKOW")
    link("KRAKOW", "TARNOW")
    link("TARNOW", "RZESZOW")
    link("RZESZOW", "LUBLIN")
    link("LUBLIN", "BREST")
    link("BREST", "MINSK")
    link("MINSK", "BORISOV")
    link("BORISOV", "SMOLENSK")
    link("SMOLENSK", "MOSCOW")

    link("MUNICH", "ERFURT")
    link("PRAGUE", "DRESDEN")
    link("BERLIN", "LEIPZIG")
    link("BERLIN", "DRESDEN")
    link("BERLIN", "FRANKFURT")
    link("BERLIN", "HAMBURG")
    # ============================================================
    # UK / SCANDINAVIA / ATLANTIC
    # ============================================================
    link("PARIS", "LONDON")
# === END OF UK / SCANDINAVIA / ATLANTIC ===

    return g


def bfs_path(start, goal):
    if start is None or goal is None:
        return []
    q = deque([(start, [start])])
    visited = set([start])
    while q:
        node, path = q.popleft()
        if node == goal:
            return path
        for nxt in node.adj:
            if nxt not in visited:
                visited.add(nxt)
                q.append((nxt, path + [nxt]))
    return []


def path_distance(a, b):
    path = bfs_path(a, b)
    if not path:
        return None
    return len(path) - 1
