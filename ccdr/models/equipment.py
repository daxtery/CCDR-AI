import abc
from typing import Any, Generic, List, Dict, TypeVar, Optional, Union, Tuple
from typing_extensions import Literal, Final, TypedDict


class Localizacao(TypedDict, total=True):
    lat: float
    long: float


class Horario(TypedDict):
    pass


class Extra(TypedDict):
    name: str
    value: str


class RequiredEquipmentFields(TypedDict):
    group: str
    area: str
    description: str
    name: str
    extras: List[Extra]


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
    num_utentes: int
    organizacao: Organizacao


class CulturalDetails(TypedDict, total=False):
    acesso_gratuito: bool
    mobilidade_reduzida: bool
    num_visitantes_medio: int
    tutela: Organizacao


class Escola(TypedDict):
    # FIXME: maybe name?
    # name: str

    grau_ensino: str
    capacidade: int
    num_alunos: int


class EducationDetails(TypedDict, total=False):
    escolas: List[Escola]


InstalacaoApoio = str


class SportDetails(TypedDict, total=False):
    iluminado: bool
    tipo_piso: str
    mobilidade_reduzida_pratica: bool
    mobilidade_reduzida_assistencia: bool
    capacidade: int
    instalacao_apoio: List[InstalacaoApoio]


class RequiredHealthDetails(TypedDict):
    tipo_saude: str
    healh_details: Any


class OptionalHealthDetails(TypedDict, total=False):
    num_utentes: int


class HealthDetails(RequiredHealthDetails, OptionalHealthDetails):
    pass


Unidade = str


class HospitalHealthDetails(TypedDict, total=False):
    num_equipamentos_por_especialidade: List[Tuple[str, int]]
    tipo_unidades: List[Unidade]
    agrupamento_saude: str
    centro_hospitalar: str
    valencias: List[str]
    especialidades: List[str]


class GeneralHealthDetails(TypedDict, total=False):
    capacidade: int
    num_centros_saude: int
