from dataclasses import dataclass


@dataclass
class ParityStats:

    even_count: int = 0
    odd_count: int = 0


class ParityEngine:

    def __init__(self):

        self.stats = ParityStats()

    # --------------------------------------------------

    def add_digit(self, digit):

        if digit % 2 == 0:
            self.stats.even_count += 1
        else:
            self.stats.odd_count += 1

    # --------------------------------------------------

    def get_stats(self):

        total = (
            self.stats.even_count +
            self.stats.odd_count
        )

        if total == 0:

            even_percent = 0
            odd_percent = 0

        else:

            even_percent = (
                self.stats.even_count / total
            ) * 100

            odd_percent = (
                self.stats.odd_count / total
            ) * 100

        return {

            "even_count": self.stats.even_count,
            "odd_count": self.stats.odd_count,

            "even_percent": even_percent,
            "odd_percent": odd_percent

        }

    # --------------------------------------------------

    def reset(self):

        self.stats = ParityStats()