import random
import string
from pathlib import Path

class MathBlockOrgan:
    """
    Generates mathblocks: sequences of up to 10 symbols drawn from a 27‑letter alphabet + null.
    """

    def __init__(self):
        # 27 letters + null
        self.alphabet = list(string.ascii_lowercase) + ["_"]  # "_" = null

    def make_block(self, length=None):
        """
        Create a mathblock of random length (1–10) unless length is specified.
        """
        if length is None:
            length = random.randint(1, 10)

        return "".join(random.choice(self.alphabet) for _ in range(length))

    def assign(self, lexical_packet):
        """
        Attach a mathblock to a lexical packet.
        """
        block = self.make_block()
        lexical_packet["mathblock"] = block
        return lexical_packet
