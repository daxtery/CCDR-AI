import json
from typing import List, Dict, Union
from typing_extensions import Literal, Final
from dataclasses import dataclass, asdict, field

EquipmentArea = Literal["Social", "Cultura", "Educação", "Desporto", "Saúde"]


@dataclass
class Equipment:
    area: EquipmentArea
    type_: str
    name: str
    extras: Dict[str, str] = field(repr=False)

    def stringuify(self) -> str:
        return f"{self.name} {self.type_} {self.area}"


@dataclass
class Organizacao:
    pass


@dataclass
class SocialEquipment(Equipment):
    fins_lucrativos: bool
    capacidade: int
    numero_de_utentes: int
    organizacao: Organizacao

    def __init__(self, name: str, type_: str, extras: Dict[str, str], fins_lucrativos: bool, capacidade: int,
                 numero_de_utentes: int,
                 organizacao: Organizacao,) -> None:
        super().__init__("Social", type_, name, extras)

        self.fins_lucrativos = fins_lucrativos
        self.capacidade = capacidade
        self.numero_de_utentes = numero_de_utentes
        self.organizacao = organizacao

    def stringuify(self) -> str:
        _fins_lucrativos = "para fins lucrativos" if self.fins_lucrativos else "sem fins lucrativos"
        return f"{self.name} {_fins_lucrativos} capacidade {self.capacidade} utentes {self.numero_de_utentes} {self.organizacao}"


@dataclass
class CulturalEquipment(Equipment):
    acesso_gratuito: bool
    mobilidade_reduzida: bool

    def __init__(self, name: str, type_: str, extras: Dict[str, str], acesso_gratuito: bool, mobilidade_reduzida: bool) -> None:
        super().__init__("Cultura", type_, name, extras)

        self.acesso_gratuito = acesso_gratuito
        self.mobilidade_reduzida = mobilidade_reduzida

    def stringuify(self) -> str:
        _mobilidade_reduzida = "acesso mobilidade reduzida" if self.mobilidade_reduzida else "sem acesso mobilidade reduzida"
        _acesso_gratuito = "grátis" if self.acesso_gratuito else "pago"

        return f"{self.name} {_mobilidade_reduzida} {_acesso_gratuito}"


@dataclass
class Escola:
    grau_ensino: str
    capacidade: int
    numero_de_alunos: int

    def __repr__(self) -> str:
        return f"{self.grau_ensino} com capacidade {self.capacidade}. Alunos inscritos {self.numero_de_alunos}"


@dataclass
class EducationEquipment(Equipment):
    escolas: List[Escola]

    def __init__(self, name: str, type_: str, extras: Dict[str, str], escolas: List[Escola]) -> None:
        super().__init__("Educação", type_, name, extras)

        self.escolas = escolas

    def stringuify(self) -> str:
        return self.name + "\n".join(map(str, self.escolas))


@dataclass
class InstalacaoApoio:
    pass


@dataclass
class SportEquipment(Equipment):
    iluminado: bool
    tipo_piso: str
    mobilidade_reduzida_pratica: bool
    mobilidade_reduzida_assistencia: bool
    capacidade: int
    instalacoes_apoio: List[InstalacaoApoio]

    def __init__(
        self, name: str,
        type_: str,
        extras: Dict[str, str],
        iluminado: bool,
        tipo_piso: str,
        mobilidade_reduzida_pratica: bool,
        mobilidade_reduzida_assistencia: bool,
        capacidade: int,
        instalacoes_apoio: List[InstalacaoApoio],
    ) -> None:
        super().__init__("Desporto", type_, name, extras)

        self.iluminado = iluminado
        self.tipo_piso = tipo_piso
        self.mobilidade_reduzida_pratica = mobilidade_reduzida_pratica
        self.mobilidade_reduzida_assistencia = mobilidade_reduzida_assistencia
        self.capacidade = capacidade
        self.instalacoes_apoio = instalacoes_apoio

    def stringuify(self) -> str:
        _iluminado = "iluminado" if self.iluminado else "não iluminado"
        _mobilidade_reduzida_pratica = "prática mobilidade reduzida" if self.mobilidade_reduzida_pratica else "não possível prática mobilidade reduzida"
        _mobilidade_reduzida_assistencia = "assistência a mobilidade reduzida" if self.mobilidade_reduzida_assistencia else "sem assitência a mobilidade reduzida"

        _apoio = "\n".join(map(str, self.instalacoes_apoio))

        return f"{self.name} {self.type_} {_iluminado} {_mobilidade_reduzida_pratica} {_mobilidade_reduzida_assistencia} com capacidade {self.capacidade} {_apoio}"


@dataclass
class HealthEquipment(Equipment):
    numero_de_utentes: int

    def __init__(
        self,
        name: str,
        type_: str,
        extras: Dict[str, str],
        numero_de_utentes: int
    ) -> None:
        super().__init__("Saúde", type_, name, extras)
        self.numero_de_utentes = numero_de_utentes


@dataclass
class Unidade:
    pass


@dataclass
class HospitalHealthEquipment(HealthEquipment):
    numero_de_equipamentos_por_especialidade: Dict[str, int]
    unidades: List[Unidade]
    agrupamento_saude: str
    centro_hospitalar: str
    valencias: List[str]
    especialidades: List[str]

    def __init__(
        self,
        name: str,
        extras: Dict[str, str],
        numero_de_utentes: int,
        unidades: List[Unidade],
        agrupamento_saude: str,
        centro_hospitalar: str,
        valencias: List[str],
        especialidades: List[str],
        numero_de_equipamentos_por_especialidade: Dict[str, int],
    ) -> None:
        super().__init__("Saúde Hospitalar", name, extras, numero_de_utentes)

        self.agrupamento_saude = agrupamento_saude
        self.centro_hospitalar = centro_hospitalar
        self.valencias = valencias
        self.especialidades = especialidades
        self.numero_de_equipamentos_por_especialidade = numero_de_equipamentos_por_especialidade
        self.unidades = unidades

    def stringuify(self) -> str:
        return f"{self.name} {self.agrupamento_saude} {self.centro_hospitalar} {','.join(self.valencias)} {','.join(self.especialidades)} {'\n'.join(map(str, self.unidades))}"


@dataclass
class GeneralHealthEquipment(HealthEquipment):
    capacidade: int
    numero_centros_saude: int

    def __init__(
        self,
        name: str,
        extras: Dict[str, str],
        numero_de_utentes: int,
        capacidade: int,
        numero_centros_saude: int,
    ) -> None:
        super().__init__("Saúde Geral", name, extras, numero_de_utentes)

        self.capacidade = capacidade
        self.numero_centros_saude = numero_centros_saude

    def stringuify(self) -> str:
        return f"{self.name} capacidade {self.capacidade} {self.numero_centros_saude} centros de saude"


def stringify(equipment: Equipment) -> str:
    return equipment.stringuify() + " ".join(list(equipment.extras.values()))
