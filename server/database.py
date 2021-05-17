from ccdr.models.equipment import Equipment

toy_equipments = {
    "609964dc33c8033e28f0c1f9": Equipment(area="Desporto", type_="Estádio"),
    "609964dc33c8033e28f0c1fa": Equipment(area="Saúde", type_="Centro Hospitalar"),
    "609964dc33c8033e28f0c1fb": Equipment(area="Educação", type_="Universidade"),
    "609964dc33c8033e28f0c1fc": Equipment(area="Educação", type_="Escola"),
    "609964dc33c8033e28f0c1fd": Equipment(area="Social", type_="Centro de dia"),
    "609964dc33c8033e28f0c1fe": Equipment(area="Cultura", type_="Teatro"),
}


class DatabaseAcessor:

    def get_equipment_by_id(self, _id: str) -> Equipment:
        return toy_equipments[_id]

    def get_all_equipments(self):
        return toy_equipments.items()
