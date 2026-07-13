from collections import deque
from core.models import DigitStatistics


class StatisticsEngine:
    """
    Maintains statistics for digits 0-9.
    """

    def __init__(self, history_size=10000):

        self.history = deque(maxlen=history_size)

        self.tick_number = 0

        # Create one statistics object for each digit
        self.stats = {
            digit: DigitStatistics(digit)
            for digit in range(10)
        }

    # --------------------------------------------------

    def add_digit(self, digit: int):

        self.tick_number += 1

        # Increase gap for every digit
        for d in self.stats.values():
            d.current_gap += 1

        current = self.stats[digit]

        # Update gap statistics
        if current.last_seen_tick != -1:

            gap = self.tick_number - current.last_seen_tick - 1

            current.total_gap += gap

            if gap > current.max_gap:
                current.max_gap = gap

        current.last_seen_tick = self.tick_number

        current.current_gap = 0

        current.count += 1

        current.appearances += 1

        self.history.append(digit)

    # --------------------------------------------------

    def update_percentages(self, window="session"):

        if window == "session":

            digits = list(self.history)

        else:

            digits = list(self.history)[-window:]

        total = len(digits)

        counts = [0] * 10

        for d in digits:
            counts[d] += 1

        for digit in range(10):

            stat = self.stats[digit]

            if total == 0:

                stat.percentage = 0

            else:

                stat.percentage = round(
                    counts[digit] / total * 100,
                    2
                )

    # --------------------------------------------------

    def get_table(self, window="session"):

        self.update_percentages(window)

        table = []

        if window == "session":
            digits = list(self.history)
        else:
            digits = list(self.history)[-window:]

        counts = [0] * 10

        for d in digits:
            counts[d] += 1

        for digit in range(10):

            stat = self.stats[digit]

            table.append({

                "digit": digit,

                "count": counts[digit],

                "percent": stat.percentage,

                "gap": stat.current_gap,

                "max_gap": stat.max_gap,

                "avg_gap": stat.average_gap

            })

        return table

    # --------------------------------------------------

    def last_digits(self, amount=20):

        return list(self.history)[-amount:]

    # --------------------------------------------------

    def reset(self):

        self.__init__()