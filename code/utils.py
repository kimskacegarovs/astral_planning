import functools
import time
from django_view_decorator.apps import ViewRegistry
from django.test import RequestFactory
import os


def print_red(text):
    print(f"\033[91m{text}\033[00m")


def print_green(text):
    print(f"\033[92m{text}\033[00m")


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


def get_view_path(view):
    for key, value in ViewRegistry.views.items():
        for k2, v2 in value.items():
            if view == v2[0].view:
                return k2


def make_request_get(view):
    url = get_view_path(view)
    request = RequestFactory().get(url)
    return view(request)


def make_request_post(view, data: dict):
    url = get_view_path(view)
    request = RequestFactory().post(url, data=data)
    return view(request)


def is_pytest() -> bool:
    result = "PYTEST_CURRENT_TEST" in os.environ
    return result
