import abc
from typing import Any, Generic, List, Dict, TypeVar, Optional, Union
from typing_extensions import Literal, Final, TypedDict
from dataclasses import dataclass, asdict, field
from ccdr.models.equipment import Localizacao

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


@dataclass
class ElectricConsumption:
    activity: str
    consumption: float


@dataclass
class LightDetails(EnergyDetails):
    num_consumo_elec_p_atividade: Optional[Dict[Localizacao,
                                                ActivityConsumption]]
    consumo_elec_p_atividade: Optional[Dict[Localizacao, ElectricConsumption]]
