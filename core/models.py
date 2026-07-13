from dataclasses import dataclass, field
from typing import List


@dataclass
class DigitStatistics:
    """
    Stores statistics for a single digit (0–9).
    """

    digit: int

    # Total number of times the digit has appeared
    count: int = 0

    # Percentage within the selected window
    percentage: float = 0.0

    # Current number of ticks since this digit last appeared
    current_gap: int = 0

    # Largest gap ever recorded
    max_gap: int = 0

    # Sum of all gaps (used to calculate average)
    total_gap: int = 0

    # Number of appearances
    appearances: int = 0

    # Tick index where the digit was last seen
    last_seen_tick: int = -1

    @property
    def average_gap(self):
        if self.appearances <= 1:
            return 0.0

        return round(
            self.total_gap / (self.appearances - 1),
            2
        )


@dataclass
class SessionStatistics:
    """
    Stores session-wide information.
    """

    total_ticks: int = 0

    session_start: float = 0.0

    market: str = "R_25"

    current_quote: float = 0.0

    current_digit: int = -1

    last_digits: List[int] = field(default_factory=list)