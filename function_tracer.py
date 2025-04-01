import time
import functools
import threading
import json
import os
from collections import defaultdict
from tabulate import tabulate


class FunctionTracer:
    def __init__(self, config_file=None):
        self._enabled = False
        self._lock = threading.Lock()
        self._functions = set()
        self._stats = defaultdict(lambda: {'count': 0, 'total_time': 0.0, 'min_time': float('inf'), 'max_time': 0.0})


        if config_file and os.path.exists(config_file):
            self.load_config(config_file)

    def load_config(self, config_file):
        """loading config from JSON"""
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                if 'functions' in config:
                    # loading certain names
                    self._functions.update(set(config['functions']))
                if 'enabled' in config:
                    self._enabled = config['enabled']
            return True
        except Exception as e:
            print(f"error: {e}")
            return False

    def save_config(self, config_file):
        """into JSON"""
        try:
            config = {
                'functions': list(self._functions),
                'enabled': self._enabled
            }
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=4)
            return True
        except Exception as e:
            print(f"error saving: {e}")
            return False

    def _trace_decorator(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            if not self._enabled or func.__name__ not in self._functions:
                return func(*args, **kwargs)

            start = time.perf_counter()
            result = func(*args, **kwargs)
            duration = time.perf_counter() - start

            with self._lock:
                stat = self._stats[func.__name__]
                stat['count'] += 1
                stat['total_time'] += duration
                stat['min_time'] = min(stat['min_time'], duration)
                stat['max_time'] = max(stat['max_time'], duration)

            return result

        return wrapper

    def track_function(self, func):
        """decorator for time"""
        # adding function for following
        self._functions.add(func.__name__)
        wrapped = self._trace_decorator(func)
        return wrapped

    def enable(self, functions=None):
        """
        enable tracing

        Args:
            functions: list of functions for following. If None, we are using those that we had before
        """
        with self._lock:
            if functions:
                # adding functions
                for func in functions:
                    if callable(func):
                        self._functions.add(func.__name__)
                    else:
                        self._functions.add(func)
            self._enabled = True

    def disable(self):
        """disable tracing"""
        with self._lock:
            self._enabled = False
        return self.get_results()

    def clear(self):
        """turn off statistic"""
        with self._lock:
            self._stats.clear()

    def add_function(self, func):
        """add function for following"""
        with self._lock:
            if callable(func):
                self._functions.add(func.__name__)
            else:
                self._functions.add(func)

    def remove_function(self, func):
        """delete function from following"""
        with self._lock:
            if callable(func):
                self._functions.discard(func.__name__)
            else:
                self._functions.discard(func)

    def get_results(self, reset=False):
        """
        get stats as table

        Args:
            reset: if True, clear stats after getting results

        Returns:
            stats array [name, call, total_time, avg_time, min_time, max_time]
        """
        with self._lock:
            results = [
                [
                    name,
                    data['count'],
                    round(data['total_time'], 6),
                    round(data['total_time'] / data['count'], 6) if data['count'] > 0 else 0,
                    round(data['min_time'], 6) if data['min_time'] != float('inf') else 0,
                    round(data['max_time'], 6)
                ]
                for name, data in self._stats.items()
            ]
            if reset:
                self._stats.clear()
            return results

    def display_results(self, reset=False):
        """
        print results as array

        Args:
            reset: if True, clear stats after printing results
        """
        results = self.get_results(reset)
        if results:
            headers = ["func", "calls", "time (s)", "Average time (s)", "Minimum time (s)", "Maximum time (с)"]
            print(tabulate(results, headers=headers, tablefmt="grid"))
        else:
            print("I dont have data.")

    def is_enabled(self):
        """check if we get data"""
        return self._enabled

    def get_intermediate_results(self):
        """Get intermediate results without disabling tracing"""
        return self.get_results(reset=False)


# creating global example
tracer = FunctionTracer()