import abc
from typing import Generic, List, Dict, TypeVar, Optional, Union
from typing_extensions import Literal, Final, TypedDict
from dataclasses import dataclass, asdict, field

EquipmentArea = Literal["social", "cultura", "educacao", "desporto", "saude"]

Group = Literal["equipment", "infra"]


# NOTE: We freeze it so we can use it as a key in a dictionary (because it is hashable)
@dataclass(frozen=True)
class Localizacao:
    latitude: float
    longitude: float


@dataclass
class Horario:
    pass


T = TypeVar('T')


@dataclass
class Equipment(Generic[T]):
    group: str
    area: str
    description: str
    name: str
    extras: Dict[str, str] = field(repr=False)

    horario: Optional[Horario]
    numero_de_equipamentos: Optional[int]
    localizacao: Optional[Localizacao]
    details: Optional[T]



@dataclass
class Organizacao:
    nome: str


@dataclass
class SocialDetails:
    fins_lucrativos: Optional[bool]
    capacidade: Optional[int]
    numero_de_utentes: Optional[int]
    organizacao: Optional[Organizacao]


@dataclass
class CulturalDetails:
    acesso_gratuito: Optional[bool]
    mobilidade_reduzida: Optional[bool]
    numero_visitantes_medio: Optional[int]
    tutela: Optional[Organizacao]


@dataclass
class Escola:
    # FIXME: maybe name?
    # name: str

    # How much is required?...
    grau_ensino: str
    capacidade: int
    numero_de_alunos: int


@dataclass
class EducationDetails:
    escolas: Optional[List[Escola]]


@dataclass
class InstalacaoApoio:
    nome: str


@dataclass
class SportDetails:
    iluminado: Optional[bool]
    tipo_piso: Optional[str]
    mobilidade_reduzida_pratica: Optional[bool]
    mobilidade_reduzida_assistencia: Optional[bool]
    capacidade: Optional[int]
    instalacoes_apoio: Optional[List[InstalacaoApoio]]


@dataclass
class HealthDetails(abc.ABC):
    numero_de_utentes: Optional[int]   # NOTE: Do we need this?


@dataclass
class Unidade:
    nome: str


@dataclass
class HospitalHealthDetails(HealthDetails):
    numero_de_equipamentos_por_especialidade: Optional[Dict[str, int]]
    unidades: Optional[List[Unidade]]
    agrupamento_saude: Optional[str]
    centro_hospitalar: Optional[str]
    valencias: Optional[List[str]]
    especialidades: Optional[List[str]]


@dataclass
class GeneralHealthDetails(HealthDetails):
    capacidade: Optional[int]
    numero_centros_saude: Optional[int]
