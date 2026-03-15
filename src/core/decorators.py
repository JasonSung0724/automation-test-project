import functools
import time
from collections.abc import Callable
from typing import TypeVar

import allure

from core.logger import logger

T = TypeVar("T")


def retry(max_attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)):
    """Retry decorator for flaky operations."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt}/{max_attempts} failed: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay)
            raise last_exception

        return wrapper

    return decorator


def step(description: str):
    import inspect

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        sig = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            params = {k: v for k, v in bound.arguments.items() if k != "self"}

            try:
                step_name = description.format(**params)
            except (KeyError, IndexError):
                step_name = description

            logger.info(f"Step: {step_name}")
            with allure.step(step_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator
