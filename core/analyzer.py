from core.statistics import StatisticsEngine
from core.models import SessionStatistics
from core.match_analyzer import MatchAnalyzer
import time


class Analyzer:
    """
    Main controller for Analyzer Pro.
    """

    def __init__(self):

        self.statistics = StatisticsEngine()
        self.match = MatchAnalyzer()

        self.session = SessionStatistics()
        self.session.session_start = time.time()

    # --------------------------------------------------

    def process_tick(self, quote: float, digit: int):

        self.session.total_ticks += 1

        self.session.current_quote = quote
        self.session.current_digit = digit

        self.statistics.add_digit(digit)

        self.match.add_digit(digit)

        self.session.last_digits = self.statistics.last_digits(20)

    # --------------------------------------------------

    def get_frequency_table(self, window="session"):

        return self.statistics.get_table(window)

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

    def get_match_statistics(self):

        return self.match.get_stats()

    # --------------------------------------------------

    def reset(self):

        self.statistics.reset()

        self.match = MatchAnalyzer()

        self.session = SessionStatistics()
        self.session.session_start = time.time()