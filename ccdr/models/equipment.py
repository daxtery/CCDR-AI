import abc
from typing import Any, Generic, List, Dict, TypeVar, Optional, Union
from typing_extensions import Literal, Final, TypedDict


class Localizacao(TypedDict, total=True):
    latitude: float
    longitude: float


class Horario(TypedDict):
    pass


class RequiredEquipmentFields(TypedDict):
    group: str
    area: str
    description: str
    name: str
    extras: Dict[str, str]


class OptionalEquipmentFields(TypedDict, total=False):
    horario: Horario
    numero_de_equipamentos: int
    localizacao: Localizacao
    equipmentDetails: Any


class Equipment(RequiredEquipmentFields, OptionalEquipmentFields):
    pass


Organizacao = str


class SocialDetails(TypedDict, total=False):
    fins_lucrativos: bool
    capacidade: int
    numero_de_utentes: int
    organizacao: Organizacao


class CulturalDetails(TypedDict, total=False):
    acesso_gratuito: bool
    mobilidade_reduzida: bool
    numero_visitantes_medio: int
    tutela: Organizacao


class Escola(TypedDict):
    # FIXME: maybe name?
    # name: str

    grau_ensino: str
    capacidade: int
    numero_de_alunos: int


class EducationDetails(TypedDict, total=False):
    escolas: List[Escola]


InstalacaoApoio = str


class SportDetails(TypedDict, total=False):
    iluminado: bool
    tipo_piso: str
    mobilidade_reduzida_pratica: bool
    mobilidade_reduzida_assistencia: bool
    capacidade: int
    instalacoes_apoio: List[InstalacaoApoio]


class RequiredHealthDetails(TypedDict):
    tipo_saude: str
    healh_details: Any


class OptionalHealthDetails(TypedDict, total=False):
    numero_de_utentes: int   # NOTE: Do we need this?


class HealthDetails(RequiredHealthDetails, OptionalHealthDetails):
    pass


Unidade = str


class HospitalHealthDetails(TypedDict, total=False):
    numero_de_equipamentos_por_especialidade: Dict[str, int]
    unidades: List[Unidade]
    agrupamento_saude: str
    centro_hospitalar: str
    valencias: List[str]
    especialidades: List[str]


class GeneralHealthDetails(TypedDict, total=False):
    capacidade: int
    numero_centros_saude: int
