import time
import random
from function_tracer import tracer


# 1 example
@tracer.track_function
def compute():
    """const delay"""
    time.sleep(0.2)
    return "Compute completed"


@tracer.track_function
def fast():
    """short delay"""
    time.sleep(0.05)
    return "Fast operation completed"


@tracer.track_function
def variable_delay():
    """random delay"""
    delay = random.uniform(0.1, 0.3)
    time.sleep(delay)
    return f"Variable delay: {delay:.3f}s"


# Пример 2: saving configs
def save_config_example():
    tracer.save_config("tracer_config.json")
    print("saved in tracer_config.json")


# B
def basic_demo():
    print("\n=== demonstration ===")
    # turning on tracing
    tracer.enable()

    print("doing functions...")
    compute()
    fast()
    compute()

    print("\nresults:")
    tracer.display_results()

    print("\ndisabling...")
    tracer.disable()


def bonus_features_demo():
    print("\n=== BONUS!!! ===")
    tracer.clear()

    # enabling tracing
    tracer.enable([compute, variable_delay])

    print("only compute и variable_delay...")
    compute()
    fast()
    variable_delay()

    print("\nresults without tracing: ")
    tracer.display_results()

    print("\ndynamic fast...")
    tracer.add_function(fast)

    fast()
    compute()

    print("\nsummary:")
    tracer.display_results()

    # exit out of tracing
    tracer.disable()

    # saving configs
    save_config_example()


if __name__ == "__main__":
    basic_demo()
    bonus_features_demo()