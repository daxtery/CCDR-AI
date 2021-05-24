from typing import Any, Iterator, Sequence, Tuple, Dict, cast
from typing_extensions import Protocol
from typing_extensions import TypedDict
from ccdr.models.equipment import Equipment, EquipmentArea, SocialEquipment, SportEquipment, HealthEquipment, CulturalEquipment, EducationEquipment, HospitalHealthEquipment, Escola
from pymongo import database, MongoClient
from bson.objectid import ObjectId

from dataclasses import asdict


class DatabaseAccessor(Protocol):

    def get_equipment_by_id(self, _id: str) -> Equipment:
        ...

    def get_all_equipments(self) -> Iterator[Tuple[str, Equipment]]:
        ...


class InMemoryDatabaseAccessor:

    toy_equipments: Dict[str, Equipment] = {
        "609964dc33c8033e28f0c1f9": SportEquipment(
            type_="Estádio",
            extras={"nome": "Estádio da Luz"},
            iluminado=True,
            tipo_piso="terra batida",
            mobilidade_reduzida_pratica=True,
            mobilidade_reduzida_assistencia=True,
        ),
        "609964dc33c8033e28f0c1fa": HospitalHealthEquipment(
            extras={"nome": "Centro de Saúde de Estremoz"},
            agrupamento_saude="Centro de Saúde Estremoz",
            centro_hospitalar="Hospital do Espírito Santo de Évora",
            valencias=["Radiologia"],
            especialidades=[],
        ),
        "609964dc33c8033e28f0c1fb": EducationEquipment(
            type_="Universidade",
            extras={"nome": "Universidade de Évora"},
            escolas=[Escola("Universidade")],
        ),
        "609964dc33c8033e28f0c1fc": EducationEquipment(
            type_="Escola",
            escolas=[Escola("Secundário"), Escola("Básico")],
            extras={"nome": "Agrupamento de Escolas Gabriel Pereira"},
        ),
        "609964dc33c8033e28f0c1fd": SocialEquipment(
            type_="Centro de dia",
            extras={"nome": "Centro Social Nossa Senhora Auxiliadora"},
            fins_lucrativos=True,
        ),
        "609964dc33c8033e28f0c1fe": CulturalEquipment(
            type_="Templo",
            acesso_gratuito=True,
            mobilidade_reduzida=True,
            extras={"nome": "Templo Romano Évora"},
        ),
    }

    def get_equipment_by_id(self, _id: str):
        return InMemoryDatabaseAccessor.toy_equipments[_id]

    def get_all_equipments(self):
        return InMemoryDatabaseAccessor.toy_equipments.items()


class BaseEquipmentDataFromDB(TypedDict):
    area: EquipmentArea
    type: str
    extras: Dict[str, str]


class MongoDatabaseConfig(TypedDict):
    database_host: str
    database: str


class MongoDatabaseAccessor:

    def __init__(self, config: MongoDatabaseConfig) -> None:
        self.database = config["database"]
        self.database_host = config["database_host"]

    def _transfrom_equipment_data_from_db(self, data: BaseEquipmentDataFromDB) -> Equipment:
        area = data["area"]
        type_ = data["type"]
        extras = data["extras"]

        data_ = cast(Dict[str, Any], data)

        if area == "Social":
            return SocialEquipment(
                type_,
                extras,
                data_["fins lucrativos"]
            )

        if area == "Cultura":
            return CulturalEquipment(
                type_,
                extras,
                data_["acesso gratuito"],
                data_["mobilidade reduzida"]
            )

        if area == "Educação":
            schools = list(
                map(
                    lambda dto: Escola(dto["grau ensino"]),
                    data_["escolas"]
                )
            )

            return EducationEquipment(type_, extras, schools)

        if area == "Desporto":
            return SportEquipment(
                type_,
                extras,
                data_["iluminado"],
                data_["tipo piso"],
                data_["mobilidade reduzida prática"],
                data_["mobilidade reduzida assistência"],
            )

        if area == "Saúde":
            if type_ == "Saúde Hospitalar":
                return HospitalHealthEquipment(
                    extras,
                    data_["agrupamento saude"],
                    data_["centro hospitalar"],
                    data_["valências"],
                    data_["especialidades"],
                )

            else:
                return HealthEquipment(type_, extras)

        else:  # We don't know what this is
            return Equipment(area, type_, extras)

    def get_equipment_by_id(self, _id: str):
        collection_name = "equipment"

        with MongoClient(self.database_host) as client:
            db = client[self.database]
            equipment_collection = db[collection_name]

            equipment_from_db = equipment_collection.find_one(
                {"_id": ObjectId(_id)})

            # FIXME: Is this good?
            assert equipment_from_db

        return self._transfrom_equipment_data_from_db(equipment_from_db)

    def get_all_equipments(self):
        collection_name = "equipment"

        with MongoClient(self.database_host) as client:
            db = client[self.database]
            equipment_collection = db[collection_name]

            equipments_from_db = equipment_collection.find({})

        for equipment in equipments_from_db:
            yield str(equipment["_id"]), self._transfrom_equipment_data_from_db(equipment)
