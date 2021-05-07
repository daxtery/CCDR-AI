from ccdr.models.equipment import Equipment

toy_equipments = {
    "1": Equipment(area="Desporto", type_="Estádio"),
    "2": Equipment(area="Saúde", type_="Centro Hospitalar"),
    "3": Equipment(area="Educação", type_="Universidade"),
    "4": Equipment(area="Educação", type_="Escola"),
    "5": Equipment(area="Social", type_="Centro de dia"),
    "6": Equipment(area="Cultura", type_="Teatro"),
}


class DatabaseAcessor:

    def get_equipment_by_id(self, _id: str) -> Equipment:
        return toy_equipments[_id]

    def get_all_equipments(self):
        return toy_equipments.items()
