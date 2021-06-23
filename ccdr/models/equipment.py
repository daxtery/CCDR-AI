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
class SocialEquipment(Equipment):
    fins_lucrativos: bool

    def __init__(self, name: str, type_: str, extras: Dict[str, str], fins_lucrativos: bool) -> None:
        super().__init__("Social", type_, name, extras)

        self.fins_lucrativos = fins_lucrativos

    def stringuify(self) -> str:
        _fins_lucrativos = "para fins lucrativos" if self.fins_lucrativos else "sem fins lucrativos"
        return f"{self.name} {_fins_lucrativos}"


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

    def __repr__(self) -> str:
        return self.grau_ensino


@dataclass
class EducationEquipment(Equipment):
    escolas: List[Escola]

    def __init__(self, name: str, type_: str, extras: Dict[str, str], escolas: List[Escola]) -> None:
        super().__init__("Educação", type_, name, extras)

        self.escolas = escolas

    def stringuify(self) -> str:
        return self.name + "\n".join(map(str, self.escolas))


@dataclass
class SportEquipment(Equipment):
    iluminado: bool
    tipo_piso: str
    mobilidade_reduzida_pratica: bool
    mobilidade_reduzida_assistencia: bool

    def __init__(
        self, name: str,
        type_: str,
        extras: Dict[str, str],
        iluminado: bool,
        tipo_piso: str,
        mobilidade_reduzida_pratica: bool,
        mobilidade_reduzida_assistencia: bool,
    ) -> None:
        super().__init__("Desporto", type_, name, extras)

        self.iluminado = iluminado
        self.tipo_piso = tipo_piso
        self.mobilidade_reduzida_pratica = mobilidade_reduzida_pratica
        self.mobilidade_reduzida_assistencia = mobilidade_reduzida_assistencia

    def stringuify(self) -> str:
        _iluminado = "iluminado" if self.iluminado else "não iluminado"
        _mobilidade_reduzida_pratica = "mobilidade reduzida prática" if self.mobilidade_reduzida_pratica else "não possível mobilidade reduzida prática"
        _mobilidade_reduzida_assistencia = "mobilidade reduzida assistência" if self.mobilidade_reduzida_assistencia else "não possível mobilidade reduzida assistência"

        return f"{self.name} {self.type_} {self.iluminado} {_iluminado} {_mobilidade_reduzida_pratica} {_mobilidade_reduzida_assistencia}"


@dataclass
class HealthEquipment(Equipment):
    def __init__(
        self,
        name: str,
        type_: str,
        extras: Dict[str, str],
    ) -> None:
        super().__init__("Saúde", type_, name, extras)


@dataclass
class HospitalHealthEquipment(HealthEquipment):
    agrupamento_saude: str
    centro_hospitalar: str
    valencias: List[str]
    especialidades: List[str]

    def __init__(
        self,
        name: str,
        extras: Dict[str, str],
        agrupamento_saude: str,
        centro_hospitalar: str,
        valencias: List[str],
        especialidades: List[str],
    ) -> None:
        super().__init__("Saúde Hospitalar", name, extras)

        self.agrupamento_saude = agrupamento_saude
        self.centro_hospitalar = centro_hospitalar
        self.valencias = valencias
        self.especialidades = especialidades

    def stringuify(self) -> str:
        return f"{self.name} {self.agrupamento_saude} {self.centro_hospitalar} {','.join(self.valencias)} {','.join(self.especialidades)}"


def stringify(equipment: Equipment) -> str:
    return equipment.stringuify() + " ".join(list(equipment.extras.values()))
