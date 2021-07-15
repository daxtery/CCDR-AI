from typing import Any, Callable, Optional, TypeVar, Dict, List

def dict_to_string(extras: Dict[Any, Any]):
    return " " + '\n'.join(map(lambda pair: f"{str(pair[0])} {str(pair[1])}", extras.items()))


T = TypeVar('T')


def stringuify_value_func_guard_none(value: Optional[T], func: Callable[[T], str]):
    return "" if value is None else " " + func(value)