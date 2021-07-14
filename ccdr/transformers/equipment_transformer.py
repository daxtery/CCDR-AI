from ccdr.models.infrastructure import EnergyDetails, GasDetails, InternetDetails, LightDetails, MailDetails, TVDetails, TelephoneDetails
from typing import Any, Callable, Optional, TypeVar, Dict, List
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from sentence_transformers import SentenceTransformer

from ccdr.models.equipment import CulturalDetails, Equipment, InstalacaoApoio, Localizacao, Organizacao, SportDetails, SocialDetails, EducationDetails, GeneralHealthDetails, HospitalHealthDetails, Unidade

from ccdr.utils.string import stringify_value_func_guard_none, dict_to_string


def stringify(equipment: Equipment):
    def _base():
        if equipment.details is None:
            return f"{equipment.area}"

        if equipment.group == "equipment":
            if equipment.area == "social":
                return stringuify_social(equipment)
            elif equipment.area == "cultura":
                return stringuify_cultural(equipment)
            elif equipment.area == "educacao":
                return stringuify_education(equipment)
            elif equipment.area == "desporto":
                return stringuify_sport(equipment)
            elif equipment.area == "saude":
                if isinstance(equipment.details, GeneralHealthDetails):
                    return stringuify_general_health(equipment)
                elif isinstance(equipment.details, HospitalHealthDetails):
                    return stringuify_hospital_health(equipment)

        elif equipment.group == "infra":
            if equipment.area == "energia":
                if isinstance(equipment.details, GasDetails):
                    return stringify_gas(equipment)
                elif isinstance(equipment.details, LightDetails):
                    return stringify_light(equipment)
            elif equipment.area == "comunicacao":
                if isinstance(equipment.details, TelephoneDetails):
                    return stringuify_telephone(equipment)
                elif isinstance(equipment.details, InternetDetails):
                    return stringuify_internet(equipment)
                elif isinstance(equipment.details, MailDetails):
                    return stringuify_mail(equipment)
                elif isinstance(equipment.details, TVDetails):
                    return stringuify_tv(equipment)

        return f"{equipment.area}"

    # TODO: Horário?
    # TODO: numero_de_equipamentos?

    def loc_string(localizacao: Localizacao):
        return f"{localizacao.latitude}:{localizacao.longitude}"

    loc = stringify_value_func_guard_none(
        equipment.localizacao,
        loc_string
    )

    return f"{equipment.name}, {loc}. {equipment.description}. {_base()}. {dict_to_string(equipment.extras)}".strip()


def stringuify_social(equipment: Equipment[SocialDetails]):
    assert equipment.details

    def fins_lucrativos_string(f: bool):
        return "para fins lucrativos" if f else "sem fins lucrativos"

    _fins_lucrativos = stringify_value_func_guard_none(
        equipment.details.fins_lucrativos,
        fins_lucrativos_string
    )

    def organizacao_string(organizacao: Organizacao):
        return organizacao.nome

    org = stringify_value_func_guard_none(
        equipment.details.organizacao,
        organizacao_string
    )

    capacidade = stringify_value_func_guard_none(
        equipment.details.capacidade,
        lambda c: f"capacidade {c}"
    )

    utentes = stringify_value_func_guard_none(
        equipment.details.numero_de_utentes,
        lambda u: f"utentes {u}"
    )

    return f"{_fins_lucrativos}{capacidade}{utentes}{org}"


def stringuify_cultural(equipment: Equipment[CulturalDetails]):
    assert equipment.details

    mobilidade_reduzida = stringify_value_func_guard_none(
        equipment.details.mobilidade_reduzida,
        lambda v: "acesso mobilidade reduzida" if v
        else "sem acesso mobilidade reduzida"
    )

    acesso_gratuito = stringify_value_func_guard_none(
        equipment.details.acesso_gratuito,
        lambda v: "grátis" if v
        else "pago"
    )

    return f"{acesso_gratuito}{mobilidade_reduzida}"


def stringuify_sport(equipment: Equipment[SportDetails]):
    assert equipment.details

    iluminado = stringify_value_func_guard_none(
        equipment.details.iluminado,
        lambda v: "iluminado" if v
        else "não iluminado"
    )

    mobilidade_reduzida_pratica = stringify_value_func_guard_none(
        equipment.details.mobilidade_reduzida_pratica,
        lambda v: "prática mobilidade reduzida" if v
        else "não possível prática mobilidade reduzida"
    )

    mobilidade_reduzida_assistencia = stringify_value_func_guard_none(
        equipment.details.mobilidade_reduzida_assistencia,
        lambda v: "assistência a mobilidade reduzida" if v
        else "sem assitência a mobilidade reduzida"
    )

    def instalacao_apoio_string(instalacoes_apoio: List[InstalacaoApoio]):
        return "\n".join(map(lambda a: a.nome, instalacoes_apoio))

    apoio = stringify_value_func_guard_none(
        equipment.details.instalacoes_apoio,
        instalacao_apoio_string
    )

    tipo_piso = stringify_value_func_guard_none(
        equipment.details.tipo_piso,
        lambda v: v
    )

    capacidade = stringify_value_func_guard_none(
        equipment.details.capacidade,
        lambda v: f"com capacidade {v}"
    )

    return f"{iluminado}{mobilidade_reduzida_pratica}{mobilidade_reduzida_assistencia}{capacidade}{apoio}{tipo_piso}"


def stringuify_education(equipment: Equipment[EducationDetails]):
    assert equipment.details

    # TODO: Does school have any non-required fields?

    escolas = stringify_value_func_guard_none(
        equipment.details.escolas,
        lambda escolas:
            ("\n".
                join(
                    map(
                        lambda s:
                        f"{s.grau_ensino} com capacidade {s.capacidade}. Alunos inscritos {s.numero_de_alunos}",
                        escolas
                    )
                )
             )
    )

    return equipment.name + escolas


def stringuify_general_health(equipment: Equipment[GeneralHealthDetails]):
    assert equipment.details

    capacidade = stringify_value_func_guard_none(
        equipment.details.capacidade,
        lambda v: f"capacidade {v}"
    )

    numero_centros_saude = stringify_value_func_guard_none(
        equipment.details.numero_centros_saude,
        lambda v: f"{v} centros de saude"
    )

    return f"{capacidade}{numero_centros_saude}"


def stringuify_hospital_health(equipment: Equipment[HospitalHealthDetails]):
    assert equipment.details

    valencias = stringify_value_func_guard_none(
        equipment.details.valencias,
        lambda valencias: ','.join(valencias)
    )

    especialidades = stringify_value_func_guard_none(
        equipment.details.especialidades,
        lambda especialidades: ','.join(especialidades)
    )

    agrupamento_saude = stringify_value_func_guard_none(
        equipment.details.agrupamento_saude,
        lambda v: v
    )

    centro_hospitalar = stringify_value_func_guard_none(
        equipment.details.centro_hospitalar,
        lambda v: v
    )

    def unidade_string(unidade: Unidade):
        return unidade.nome

    unidades = stringify_value_func_guard_none(
        equipment.details.unidades,
        lambda unidades: '\n'.join(map(unidade_string, unidades))
    )

    return f"{agrupamento_saude}{centro_hospitalar}{valencias}{especialidades}{unidades}"


def stringify_gas(equipment: Equipment[GasDetails]):
    assert equipment.details

    num_consumo_gas = stringify_value_func_guard_none(
        equipment.details.num_consumo_gas,
        lambda s: dict_to_string(s) + "."
    )

    consumo_gas = stringify_value_func_guard_none(
        equipment.details.consumo_gas,
        lambda s: dict_to_string(s) + "."
    )

    pontos_acesso = stringify_value_func_guard_none(
        equipment.details.pontos_acesso,
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_consumo_gas}{consumo_gas}{pontos_acesso}"


def stringify_light(equipment: Equipment[LightDetails]):
    assert equipment.details

    num_consumo_elec_p_atividade = stringify_value_func_guard_none(
        equipment.details.num_consumo_elec_p_atividade,
        lambda s: dict_to_string(s) + "."
    )

    consumo_elec_p_atividade = stringify_value_func_guard_none(
        equipment.details.consumo_elec_p_atividade,
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_consumo_elec_p_atividade}{consumo_elec_p_atividade}"


def stringuify_telephone(equipment: Equipment[TelephoneDetails]):
    assert equipment.details

    num_postos = stringify_value_func_guard_none(
        equipment.details.num_postos,
        lambda s: dict_to_string(s) + "."
    )

    num_acessos = stringify_value_func_guard_none(
        equipment.details.num_acessos,
        lambda s: dict_to_string(s) + "."
    )

    num_acessos_p_100 = stringify_value_func_guard_none(
        equipment.details.num_acessos_p_100,
        lambda s: dict_to_string(s) + "."
    )

    num_postos_publicos = stringify_value_func_guard_none(
        equipment.details.num_postos_publicos,
        lambda s: dict_to_string(s) + "."
    )

    num_clientes = stringify_value_func_guard_none(
        equipment.details.num_clientes,
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_postos}{num_acessos}{num_acessos_p_100}{num_postos_publicos}{num_clientes}"


def stringuify_internet(equipment: Equipment[InternetDetails]):
    assert equipment.details

    num_clientes_banda_larga = stringify_value_func_guard_none(
        equipment.details.num_clientes_banda_larga,
        lambda s: dict_to_string(s) + "."
    )

    num_acessos_banda_larga_100 = stringify_value_func_guard_none(
        equipment.details.num_acessos_banda_larga_100,
        lambda s: dict_to_string(s) + "."
    )

    num_acessos_banda_larga = stringify_value_func_guard_none(
        equipment.details.num_acessos_banda_larga,
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_clientes_banda_larga}{num_acessos_banda_larga_100}{num_acessos_banda_larga}"


def stringuify_mail(equipment: Equipment[MailDetails]):
    assert equipment.details

    _ = stringify_value_func_guard_none(
        equipment.details._,
        lambda s: dict_to_string(s) + "."
    )

    return _


def stringuify_tv(equipment: Equipment[TVDetails]):
    assert equipment.details

    num_subscricoes = stringify_value_func_guard_none(
        equipment.details.num_subscricoes,
        lambda s: dict_to_string(s) + "."
    )

    num_clientes = stringify_value_func_guard_none(
        equipment.details.num_clientes,
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_subscricoes}{num_clientes}"


class EquipmentTypeTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment):
        stringuified = stringify(equipment)
        return self.model.encode(stringuified)
