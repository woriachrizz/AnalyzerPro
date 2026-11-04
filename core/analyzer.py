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

        self.reset_prediction_tracking()

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

        self.track_prediction_result(digit)

    # --------------------------------------------------

    def get_frequency_table(self, window="session"):

        return self.statistics.get_table(window)

    # --------------------------------------------------

    def get_match_stats(self):

        return self.match.get_stats()

    # --------------------------------------------------

    def set_prediction_target(self, kind, target=None, horizon=1):

        self.prediction_kind = kind
        self.prediction_target = target
        self.prediction_horizon = max(1, int(horizon))
        self.prediction_hits = 0
        self.prediction_misses = 0
        self.current_hit_streak = 0
        self.current_miss_streak = 0

    # --------------------------------------------------

    def reset_prediction_tracking(self):

        self.prediction_kind = None
        self.prediction_target = None
        self.prediction_horizon = 1
        self.prediction_hits = 0
        self.prediction_misses = 0
        self.current_hit_streak = 0
        self.current_miss_streak = 0

    # --------------------------------------------------

    def track_prediction_result(self, digit):

        if self.prediction_kind is None:
            return

        if self.prediction_kind == "Odd":
            hit = digit % 2 == 1
        elif self.prediction_kind == "Even":
            hit = digit % 2 == 0
        elif self.prediction_kind == "Match":
            hit = digit == self.prediction_target
        elif self.prediction_kind == "Differs":
            hit = digit != self.prediction_target
        elif self.prediction_kind == "Over":
            hit = digit > self.prediction_target
        elif self.prediction_kind == "Under":
            hit = digit < self.prediction_target
        else:
            return

        if hit:
            self.prediction_hits += 1
            self.current_hit_streak += 1
            self.current_miss_streak = 0
        else:
            self.prediction_misses += 1
            self.current_miss_streak += 1
            self.current_hit_streak = 0

    # --------------------------------------------------

    def get_prediction_stats(self):

        total = self.prediction_hits + self.prediction_misses

        if total == 0:
            hit_percent = 0
            miss_percent = 0
        else:
            hit_percent = round(
                self.prediction_hits / total * 100,
                2
            )

            miss_percent = round(
                self.prediction_misses / total * 100,
                2
            )

        return {
            "kind": self.prediction_kind,
            "target": self.prediction_target,
            "horizon": self.prediction_horizon,
            "hits": self.prediction_hits,
            "misses": self.prediction_misses,
            "total": total,
            "hit_percent": hit_percent,
            "miss_percent": miss_percent,
            "current_hit_streak": self.current_hit_streak,
            "current_miss_streak": self.current_miss_streak,
        }

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
        self.reset_prediction_tracking()

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

    def get_window_digits(self, window="session"):

        digits = list(self.statistics.history)

        if window == "session":
            return digits

        return digits[-int(window):]
    
    # --------------------------------------------------

    def get_parity_stats(self, window="session"):

        digits = self.get_window_digits(window)

        even_count = sum(
            1 for digit in digits
            if digit % 2 == 0
        )

        odd_count = len(digits) - even_count

        total = len(digits)

        if total == 0:
            even_percent = 0
            odd_percent = 0
        else:
            even_percent = round(
                even_count / total * 100,
                2
            )

            odd_percent = round(
                odd_count / total * 100,
                2
            )

        return {
            "even_count": even_count,
            "odd_count": odd_count,
            "even_percent": even_percent,
            "odd_percent": odd_percent
        }

    # --------------------------------------------------

    def get_range_stats(self, window="session"):

        digits = self.get_window_digits(window)

        low_count = sum(
            1 for digit in digits
            if digit <= 4
        )

        high_count = len(digits) - low_count

        total = len(digits)

        if total == 0:
            low_percent = 0
            high_percent = 0
        else:
            low_percent = round(
                low_count / total * 100,
                2
            )

            high_percent = round(
                high_count / total * 100,
                2
            )

        return {
            "low_count": low_count,
            "high_count": high_count,
            "low_percent": low_percent,
            "high_percent": high_percent
        }

    # --------------------------------------------------

    def analyze_prediction(self, kind, target=None, window="session", horizon=1):

        digits = self.get_window_digits(window)
        sample_size = len(digits)

        transitions = [[0] * 10 for _ in range(10)]
        for previous_digit, next_digit in zip(digits, digits[1:]):
            transitions[previous_digit][next_digit] += 1

        current_digit = digits[-1] if digits else None
        transition_contexts = sum(transitions[current_digit]) if current_digit is not None else 0
        if current_digit is None:
            next_digit_probabilities = [0.1] * 10
        else:
            denominator = transition_contexts + 10
            next_digit_probabilities = [
                (transitions[current_digit][digit] + 1) / denominator
                for digit in range(10)
            ]

        if kind == "Odd":
            winning_digits = {digit for digit in range(10) if digit % 2}
            description = "odd digits"
        elif kind == "Even":
            winning_digits = {digit for digit in range(10) if digit % 2 == 0}
            description = "even digits"
        elif kind == "Match":
            if target is None:
                target = max(range(10), key=lambda digit: next_digit_probabilities[digit])
            winning_digits = {target}
            description = f"digit {target} (Match)"
        elif kind == "Differs":
            if target is None:
                target = min(range(10), key=lambda digit: next_digit_probabilities[digit])
            winning_digits = set(range(10)) - {target}
            description = f"digit {max(winning_digits, key=lambda digit: next_digit_probabilities[digit])} (Differs {target})"
        elif kind == "Over":
            if target is None:
                target = 4
            winning_digits = {digit for digit in range(10) if digit > target}
            description = f"digits over {target}"
        elif kind == "Under":
            if target is None:
                target = 5
            winning_digits = {digit for digit in range(10) if digit < target}
            description = f"digits under {target}"
        else:
            raise ValueError(f"Unsupported prediction type: {kind}")

        appearances = sum(digit in winning_digits for digit in digits)
        sample_frequency = appearances / sample_size * 100 if sample_size else 0.0
        baseline = len(winning_digits) * 10
        if current_digit is None or baseline == 0:
            next_tick_probability = baseline / 100
        else:
            next_tick_probability = sum(
                (transitions[current_digit][digit] + 1) / (transition_contexts + 10)
                for digit in winning_digits
            )

        horizon = max(1, int(horizon))
        if current_digit is None:
            horizon_probability = 1 - (1 - baseline / 100) ** horizon
        else:
            no_event_distribution = [0.0] * 10
            no_event_distribution[current_digit] = 1.0
            for _ in range(horizon):
                next_distribution = [0.0] * 10
                for previous_digit, probability in enumerate(no_event_distribution):
                    if probability == 0:
                        continue
                    denominator = sum(transitions[previous_digit]) + 10
                    for next_digit in range(10):
                        if next_digit not in winning_digits:
                            transition_probability = (
                                transitions[previous_digit][next_digit] + 1
                            ) / denominator
                            next_distribution[next_digit] += probability * transition_probability
                no_event_distribution = next_distribution
            horizon_probability = 1 - sum(no_event_distribution)

        frequency = round(next_tick_probability * 100, 2)
        horizon_percent = round(horizon_probability * 100, 2)
        if sample_size == 0:
            status = "NO DATA"
        elif baseline == 0:
            status = "IMPOSSIBLE"
        elif frequency >= baseline + 5:
            status = "HIGH FREQUENCY"
        elif frequency <= baseline - 5:
            status = "LOW FREQUENCY"
        else:
            status = "MEDIUM"
        baseline_deviation = round(abs(frequency - baseline), 2)
        ties = sum(digit == target for digit in digits) if kind in ("Over", "Under") else None
        if baseline == 0:
            recommendation = "No digit can satisfy this barrier. Choose Over 8 or Under 1 instead."
        elif sample_size == 0:
            recommendation = "No ticks collected yet; this shows the neutral baseline estimate."
        elif transition_contexts < 5:
            recommendation = f"Only {transition_contexts} historical transitions start from digit {current_digit}; this estimate is mostly smoothed toward the baseline."
        elif abs(frequency - baseline) < 5:
            recommendation = "Recent transitions show no strong difference from the baseline. Estimates are not guarantees."
        else:
            recommendation = f"Based on transitions from current digit {current_digit}, estimate {frequency:.2f}% for the next tick and {horizon_percent:.2f}% at least once within {horizon} ticks. This is not a guarantee."

        prediction_stats = self.get_prediction_stats()
        predicted_digit = max(winning_digits, key=lambda digit: next_digit_probabilities[digit])
        digit_probability = next_digit_probabilities[predicted_digit]

        return {
            "kind": kind,
            "target": target,
            "description": description,
            "predicted_digit": predicted_digit,
            "digit_probability": round(digit_probability * 100, 2),
            "frequency": frequency,
            "sample_frequency": round(sample_frequency, 2),
            "horizon": horizon,
            "horizon_probability": horizon_percent,
            "current_digit": current_digit,
            "transition_contexts": transition_contexts,
            "transition_hits": sum(transitions[current_digit][digit] for digit in winning_digits) if current_digit is not None else 0,
            "baseline": baseline,
            "appearances": appearances,
            "ties": ties,
            "sample_size": sample_size,
            "baseline_deviation": baseline_deviation,
            "recommendation": recommendation,
            "prediction_hits": prediction_stats["hits"],
            "prediction_misses": prediction_stats["misses"],
            "prediction_total": prediction_stats["total"],
            "prediction_hit_percent": prediction_stats["hit_percent"],
            "prediction_miss_percent": prediction_stats["miss_percent"],
            "status": status,
        }

    # --------------------------------------------------

    def get_prediction_confidence(self, selected, rank, sample_size):

        if sample_size < 25:
            return 15

        expected_percent = 10
        frequency_gap = abs(
            selected["percent"] - expected_percent
        )

        score = min(
            frequency_gap * 4,
            40
        )

        if rank <= 3 or rank >= 8:
            score += 20

        avg_gap = selected["avg_gap"]
        current_gap = selected["gap"]

        if avg_gap > 0 and current_gap >= avg_gap * 2:
            score += 25

        return min(
            int(score),
            100
        )

    # --------------------------------------------------

    def get_prediction_recommendation(self, selected, rank, sample_size):

        if sample_size < 25:
            return "Collect more ticks before trusting this reading."

        avg_gap = selected["avg_gap"]
        current_gap = selected["gap"]

        if selected["percent"] >= 12 and rank <= 3:
            return "Hot digit. Monitor it closely, but avoid chasing."

        if avg_gap > 0 and current_gap >= avg_gap * 2:
            return "Cold gap building. Watch for a possible return."

        if selected["percent"] <= 8 and rank >= 8:
            return "Low frequency. Match signal is weak right now."

        return "Balanced reading. No strong digit signal yet."
