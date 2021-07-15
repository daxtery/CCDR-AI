import abc
from typing import Any, Generic, List, Dict, TypeVar
from typing_extensions import Literal, Final, TypedDict
from ccdr.models.equipment import Localizacao


class RequiredEnergyDetails(TypedDict):
    tipo_energia: str
    energy_details: Any


class OptionalEnergyDetails(TypedDict, total=False):
    num_operadores: int
    lojas_por_operador: Dict[str, int]
    agentes_por_operador: Dict[str, int]


class EnergyDetails(RequiredEnergyDetails, OptionalEnergyDetails):
    pass


class GasDetails(TypedDict, total=False):
    num_consumo_gas: Dict[Localizacao, int]
    consumo_gas: Dict[Localizacao, int]
    pontos_acesso: Dict[Localizacao, int]


class ActivityConsumption(TypedDict):
    activity: str
    numberOfConsumers: int


class ElectricConsumption(TypedDict):
    activity: str
    consumption: float


class LightDetails(TypedDict, total=False):
    num_consumo_elec_p_atividade: Dict[Localizacao, ActivityConsumption]
    consumo_elec_p_atividade: Dict[Localizacao, ElectricConsumption]


class OptionalCommunicationDetails(TypedDict, total=False):
    num_operadores: int
    lojas_por_operador: Dict[str, int]
    cobertura_por_operador: Dict[Localizacao, Dict[str, int]]


class RequiredCommunicationDetails(TypedDict):
    tipo_comunicacao: str
    communication_details: Any


class CommunicationDetails(RequiredCommunicationDetails, OptionalCommunicationDetails):
    pass


class Access(TypedDict):
    type: str
    numAccess: int


class ClientNumber(TypedDict):
    type: str
    num: int


class TelephoneDetails(TypedDict, total=False):
    num_postos: Dict[Localizacao, int]
    num_acessos: Dict[Localizacao, Access]
    num_acessos_p_100: Dict[Localizacao, int]
    num_postos_publicos: Dict[Localizacao, int]
    num_clientes: Dict[Localizacao, ClientNumber]


class InternetDetails(TypedDict, total=False):
    num_clientes_banda_larga: Dict[str, int]
    num_acessos_banda_larga_100: Dict[str, int]
    num_acessos_banda_larga: Dict[Localizacao, Access]


class Company(TypedDict):
    numStations: Dict[str, int]
    numPosts: Dict[str, int]


MailDetails = Dict[Localizacao, Company]


class TVDetails(TypedDict, total=False):
    num_subscricoes: Dict[Localizacao, int]
    num_clientes: Dict[str, int]
