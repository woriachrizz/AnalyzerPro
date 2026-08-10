from dataclasses import dataclass


@dataclass
class RangeStats:

    low_count: int = 0
    high_count: int = 0


class RangeEngine:

    def __init__(self):

        self.stats = RangeStats()

    # --------------------------------------------------

    def add_digit(self, digit):

        if digit <= 4:
            self.stats.low_count += 1
        else:
            self.stats.high_count += 1

    # --------------------------------------------------

    def get_stats(self):

        total = (
            self.stats.low_count +
            self.stats.high_count
        )

        if total == 0:

            low_percent = 0
            high_percent = 0

        else:

            low_percent = (
                self.stats.low_count / total
            ) * 100

            high_percent = (
                self.stats.high_count / total
            ) * 100

        return {

            "low_count": self.stats.low_count,
            "high_count": self.stats.high_count,

            "low_percent": low_percent,
            "high_percent": high_percent

        }

    # --------------------------------------------------

    def reset(self):

        self.stats = RangeStats()