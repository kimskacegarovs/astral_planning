import time
from utils import timer


class TestTimerDecorator:
    @staticmethod
    @timer(ms_threshold=500)
    def test_function():
        time.sleep(0.6)

    def test_timer_decorator(self, capfd):
        self.test_function()

        captured = capfd.readouterr()
        printed_output = captured.out.strip()

        assert "elapsed:" in printed_output
