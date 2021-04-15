from typing import Sequence
from ccdr.models.equipment import Equipment

toy_equipments = {
    "1": Equipment(area="Desporto"),
    "2": Equipment(area="Saúde"),
    "3": Equipment(area="Educação"),
    "4": Equipment(area="Social"),
    "5": Equipment(area="Cultura"),
}


def get_equipment_by_id(_id: str) -> Equipment:
    return toy_equipments[_id]

def get_all_equipments():
    return toy_equipments.items()
