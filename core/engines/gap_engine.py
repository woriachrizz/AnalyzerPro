from dataclasses import dataclass


@dataclass
class GapInfo:
    digit: int
    gap: int
    last_seen: int


class GapEngine:

    def __init__(self):

        self.tick_number = -1

        # last tick index where each digit appeared
        self.last_seen = {
            digit: None for digit in range(10)
        }

    # --------------------------------------------------

    def add_digit(self, digit):

        self.tick_number += 1

        self.last_seen[digit] = self.tick_number

    # --------------------------------------------------

    def get_table(self):

        table = []

        for digit in range(10):

            last = self.last_seen[digit]

            if last is None:
                gap = None
            else:
                gap = self.tick_number - last

            table.append({
                "digit": digit,
                "gap": gap,
                "last_seen": last
            })

        return table

    # --------------------------------------------------

    def hottest_digit(self):

        seen = [
            row for row in self.get_table()
            if row["gap"] is not None
        ]

        if not seen:
            return None

        return min(seen, key=lambda x: x["gap"])

    # --------------------------------------------------

    def coldest_digit(self):

        seen = [
            row for row in self.get_table()
            if row["gap"] is not None
        ]

        if not seen:
            return None

        return max(seen, key=lambda x: x["gap"])

    # --------------------------------------------------

    def reset(self):

        self.tick_number = -1

        self.last_seen = {
            digit: None for digit in range(10)
        }