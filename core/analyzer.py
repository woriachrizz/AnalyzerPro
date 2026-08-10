import time

from core.engines.match_engine import MatchEngine
from core.models import SessionStatistics
from core.statistics import StatisticsEngine
from core.engines.gap_engine import GapEngine
from core.engines.parity_engine import ParityEngine
from core.engines.range_engine import RangeEngine


class Analyzer:
    """
    Main controller for Analyzer Pro.

    Responsibilities
    ----------------
    • Receive ticks
    • Update statistics
    • Update match analyzer
    • Maintain session information
    • Provide data for the UI
    """

    def __init__(self):

        self.statistics = StatisticsEngine()
        self.match = MatchEngine()
        self.gap = GapEngine()
        self.parity = ParityEngine()
        self.range = RangeEngine()

        self.session = SessionStatistics()
        self.session.session_start = time.time()

    # --------------------------------------------------

    def process_tick(self, quote: float, digit: int):

        self.session.total_ticks += 1

        self.session.current_quote = quote
        self.session.current_digit = digit

        self.statistics.add_digit(digit)
        self.match.add_digit(digit)
        self.gap.add_digit(digit)
        self.parity.add_digit(digit)
        self.range.add_digit(digit)

        self.session.last_digits = self.statistics.last_digits(20)

    # --------------------------------------------------

    def get_frequency_table(self, window="session"):

        return self.statistics.get_table(window)

    # --------------------------------------------------

    def get_match_stats(self):

        return self.match.get_stats()

    # --------------------------------------------------

    def get_last_digits(self):

        return self.session.last_digits

    # --------------------------------------------------

    def get_current_quote(self):

        return self.session.current_quote

    # --------------------------------------------------

    def get_current_digit(self):

        return self.session.current_digit

    # --------------------------------------------------

    def get_total_ticks(self):

        return self.session.total_ticks

    # --------------------------------------------------

    def get_runtime(self):

        seconds = int(time.time() - self.session.session_start)

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        return f"{hours:02}:{minutes:02}:{secs:02}"

    # --------------------------------------------------

    def reset(self):

        self.statistics.reset()
        self.match.reset()
        self.gap.reset()
        self.parity.reset()
        self.range.reset()

        self.session = SessionStatistics()
        self.session.session_start = time.time()

    # --------------------------------------------------

    def get_gap_table(self):

        return self.gap.get_table()

    # --------------------------------------------------

    def get_hottest_digit(self):

        return self.gap.hottest_digit()

    # --------------------------------------------------

    def get_coldest_digit(self):

        return self.gap.coldest_digit()
    
    # --------------------------------------------------

    def get_parity_stats(self):

     return self.parity.get_stats()

    # --------------------------------------------------

    def get_range_stats(self):

     return self.range.get_stats()