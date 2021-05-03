from dataclasses import dataclass, asdict


@dataclass
class Equipment:
    area: str
    type_: str


# TODO: Keep this?
def stringify(equipment: Equipment) -> str:
    return str(asdict(equipment))
