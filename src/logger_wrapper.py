import logging
from typing import Any, Callable
import sys

logger = logging.getLogger('TELEGRAM')
formatter = logging.Formatter(
    '%(asctime)s - %(name)s: %(message)s'
)


console_output_handler = logging.StreamHandler(sys.stdout)
console_output_handler.setFormatter(formatter)
logger.addHandler(console_output_handler)

logger.setLevel(logging.DEBUG)

def wrap_logger(func: Callable[[Any], Any]) -> Callable[[Any], Any]:
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger.info(func.__name__)
        return func(*args, **kwargs)
    return wrapper

@wrap_logger
def foo(a: int):
    return a + 1
    
if __name__ == '__main__':
    print(foo(23))