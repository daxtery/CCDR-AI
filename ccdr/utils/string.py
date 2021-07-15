from typing import Any, Callable, Optional, TypeVar, Dict, List, Tuple


def dict_to_string(extras: Dict[Any, Any]):
    return " " + '\n'.join(map(lambda pair: f"{str(pair[0])} {str(pair[1])}", extras.items()))


def tuple_dict_list_to_string(extras: List[Tuple[Any, Any]]):
    return " " + '\n'.join(map(lambda pair: f"{str(pair[0])} {str(pair[1])}", extras))


T = TypeVar('T')


def stringuify_value_func_guard_none(value: Optional[T], func: Callable[[T], str]):
    return "" if value is None else " " + func(value)
