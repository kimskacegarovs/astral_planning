import functools
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


# Always declare with () at the end, even if you don't pass any arguments, i.e. @timer()
def timer(ms_threshold=500):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)  # Call the function
            end_time = time.time()

            elapsed_time = end_time - start_time
            ms_elapsed = round(elapsed_time * 1000)

            method = f"{func.__qualname__}"
            text = f"{method} elapsed: {ms_elapsed} ms"

            if ms_elapsed > ms_threshold:
                print_red(text)  # Print in red color
            else:
                print_green(text)  # Print in green color
            return result

        return wrapper

    return decorator
