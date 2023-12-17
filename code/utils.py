import time


def print_red(text):
    print(f"\033[91m{text}\033[00m")


def print_green(text):
    print(f"\033[92m{text}\033[00m")


class Timer:
    MS_THRESHOLD = 500

    def __init__(self, method: str = None):
        self.method = method if method else "Timer"

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.end_time = time.time()
        self.elapsed_time = self.end_time - self.start_time
        ms_elapsed = round(self.elapsed_time * 1000)
        text = f"{self.method} elapsed: {ms_elapsed} ms"

        if ms_elapsed > self.MS_THRESHOLD:
            print_red(text)
        else:
            print_green(text)
