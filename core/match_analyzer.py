from dataclasses import dataclass


@dataclass
class MatchStats:
    match_count: int = 0
    differ_count: int = 0

    current_match_streak: int = 0
    current_differ_streak: int = 0

    longest_match_streak: int = 0
    longest_differ_streak: int = 0


class MatchAnalyzer:

    def __init__(self):
        self.previous_digit = None
        self.stats = MatchStats()

    def add_digit(self, digit):

        if self.previous_digit is None:
            self.previous_digit = digit
            return

        if digit == self.previous_digit:

            self.stats.match_count += 1

            self.stats.current_match_streak += 1
            self.stats.current_differ_streak = 0

            self.stats.longest_match_streak = max(
                self.stats.longest_match_streak,
                self.stats.current_match_streak
            )

        else:

            self.stats.differ_count += 1

            self.stats.current_differ_streak += 1
            self.stats.current_match_streak = 0

            self.stats.longest_differ_streak = max(
                self.stats.longest_differ_streak,
                self.stats.current_differ_streak
            )

        self.previous_digit = digit

    def get_stats(self):

        total = self.stats.match_count + self.stats.differ_count

        if total == 0:
            match_percent = 0
            differ_percent = 0
        else:
            match_percent = self.stats.match_count * 100 / total
            differ_percent = self.stats.differ_count * 100 / total

        return {
            "match_count": self.stats.match_count,
            "differ_count": self.stats.differ_count,
            "match_percent": match_percent,
            "differ_percent": differ_percent,
            "current_match_streak": self.stats.current_match_streak,
            "current_differ_streak": self.stats.current_differ_streak,
            "longest_match_streak": self.stats.longest_match_streak,
            "longest_differ_streak": self.stats.longest_differ_streak,
        }