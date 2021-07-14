import abc
from typing import Any, Generic, List, Dict, TypeVar, Optional, Union
from typing_extensions import Literal, Final, TypedDict
from dataclasses import dataclass, asdict, field
from ccdr.models.equipment import Localizacao

from ccdr.utils.string import stringify_value_func_guard_none, dict_to_string

InfrastructureArea = Literal["energia", "comunicacao"]


@dataclass
class EnergyDetails(abc.ABC):
    num_operadores: Optional[int]
    lojas_por_operador: Optional[Dict[str, int]]
    agentes_por_operador: Optional[Dict[str, int]]


@dataclass
class GasDetails(EnergyDetails):
    num_consumo_gas: Optional[Dict[Localizacao, int]]
    consumo_gas: Optional[Dict[Localizacao, int]]
    pontos_acesso: Optional[Dict[Localizacao, int]]


@dataclass
class ActivityConsumption:
    activity: str
    numberOfConsumers: int

    def __str__(self) -> str:
        return f"{self.activity} - {self.numberOfConsumers}"


@dataclass
class ElectricConsumption:
    activity: str
    consumption: float

    def __str__(self) -> str:
        return f"{self.activity} - {self.consumption}"


@dataclass
class LightDetails(EnergyDetails):
    num_consumo_elec_p_atividade: Optional[Dict[Localizacao,
                                                ActivityConsumption]]
    consumo_elec_p_atividade: Optional[Dict[Localizacao, ElectricConsumption]]


@dataclass
class CommunicationDetails(abc.ABC):
    num_operadores: Optional[int]
    lojas_por_operador: Optional[Dict[str, int]]
    cobertura_por_operador: Optional[Dict[Localizacao, Dict[str, int]]]


@dataclass
class Access:
    type: str
    numAccess: int

    def __str__(self) -> str:
        return f"{self.type} - {self.numAccess}"


@dataclass
class ClientNumber:
    type: str
    num: int

    def __str__(self) -> str:
        return f"{self.type} - {self.num}"


@dataclass
class TelephoneDetails(CommunicationDetails):
    num_postos: Optional[Dict[Localizacao, int]]
    num_acessos: Optional[Dict[Localizacao, Access]]
    num_acessos_p_100: Optional[Dict[Localizacao, int]]
    num_postos_publicos: Optional[Dict[Localizacao, int]]
    num_clientes: Optional[Dict[Localizacao, ClientNumber]]


@dataclass
class InternetDetails(CommunicationDetails):
    num_clientes_banda_larga: Optional[Dict[str, int]]
    num_acessos_banda_larga_100: Optional[Dict[str, int]]
    num_acessos_banda_larga: Optional[Dict[Localizacao, Access]]


@dataclass
class Company:
    numStations: Optional[Dict[str, int]]
    numPosts: Optional[Dict[str, int]]

    def __str__(self) -> str:
        numStations = stringify_value_func_guard_none(
            self.numStations, lambda s: dict_to_string(s))

        numPosts = stringify_value_func_guard_none(
            self.numPosts, lambda s: " - " + dict_to_string(s))

        return f"{numStations}{numPosts}"


@dataclass
class MailDetails(CommunicationDetails):
    _: Optional[Dict[Localizacao, Company]]


@dataclass
class TVDetails(CommunicationDetails):
    num_subscricoes: Optional[Dict[Localizacao, int]]
    num_clientes: Optional[Dict[str, int]]
