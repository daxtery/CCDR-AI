from collections import defaultdict
from ccdr.models.infrastructure import CommunicationDetails, EnergyDetails, GasDetails, InternetDetails, LightDetails, MailDetails, TVDetails, TelephoneDetails
from typing import Any, Callable, Optional, TypeVar, Dict, List, cast
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from sentence_transformers import SentenceTransformer

from ccdr.models.equipment import CulturalDetails, Equipment, InstalacaoApoio, Localizacao, Organizacao, SportDetails, SocialDetails, EducationDetails, GeneralHealthDetails, HospitalHealthDetails, Unidade, HealthDetails

from ccdr.utils.string import stringuify_value_func_guard_none, dict_to_string


def stringuify(equipment: Equipment):

    def _stringuify_details():
        details = equipment.get("equipmentDetails")
        if details is None:
            return equipment.get("area")

        if equipment["group"] == "equipment":
            if equipment["area"] == "social":
                return stringuify_social(equipment)  # type:ignore

            elif equipment["area"] == "cultura":
                return stringuify_cultural(equipment)  # type:ignore

            elif equipment["area"] == "educacao":
                return stringuify_education(equipment)  # type:ignore

            elif equipment["area"] == "desporto":
                return stringuify_sport(equipment)  # type:ignore

            elif equipment["area"] == "saude":
                healt_details = cast(HealthDetails, details)

                numero_de_utentes = stringuify_value_func_guard_none(
                    healt_details.get("numero_de_utentes"),
                    lambda u: f"{u} utentes."
                )

                if healt_details["tipo_saude"] == "saude_geral":
                    finer = stringuify_general_health(equipment)  # type:ignore

                elif healt_details["tipo_saude"] == "saude_hospitalar":
                    finer = stringuify_hospital_health(equipment)  # type:ignore
                
                else:
                    finer = ""

                return f"{numero_de_utentes}{finer}"

        elif equipment["group"] == "infra":

            if equipment["area"] == "energia":
                energy_details = cast(EnergyDetails, details)

                num_operadores = stringuify_value_func_guard_none(
                    energy_details.get("num_operadores"),
                    lambda v: f"{v} operadores."
                )

                if energy_details.get("tipo_energia") == "gas":
                    finer = stringify_gas(equipment)   # type:ignore

                elif energy_details.get("tipo_energia") == "luz":
                    finer = stringify_light(equipment)   # type:ignore
                
                else:
                    finer = ""

                return f"{num_operadores}{finer}"

            elif equipment["area"] == "comunicacao":
                communication_details = cast(CommunicationDetails, details)

                num_operadores = stringuify_value_func_guard_none(
                    communication_details.get("num_operadores"),
                    lambda v: f"{v} operadores."
                )

                if communication_details.get("tipo_comunicacao") == "telefone":
                    finer = stringuify_telephone(equipment)   # type:ignore

                elif communication_details.get("tipo_comunicacao") == "internet":
                    finer = stringuify_internet(equipment)   # type:ignore

                elif communication_details.get("tipo_comunicacao") == "correio":
                    finer = stringuify_mail(equipment)   # type:ignore

                elif communication_details.get("tipo_comunicacao") == "televisao":
                    finer = stringuify_tv(equipment)   # type:ignore
                
                else:
                    finer = ""

                return f"{num_operadores}{finer}"

        return equipment["area"]

    # TODO: Horário?
    # TODO: numero_de_equipamentos?

    def loc_string(localizacao: Localizacao):
        return f"{localizacao['latitude']}:{localizacao['longitude']}"

    loc = stringuify_value_func_guard_none(
        equipment.get("localizacao"),
        loc_string
    )

    return f"{equipment['name']}, {loc}. {equipment['description']}. {_stringuify_details()}. {dict_to_string(equipment['extras'])}".strip()


def stringuify_social(details: SocialDetails):
    def fins_lucrativos_string(f: bool):
        return "para fins lucrativos" if f else "sem fins lucrativos"

    _fins_lucrativos = stringuify_value_func_guard_none(
        details.get("fins_lucrativos"),
        fins_lucrativos_string
    )

    def organizacao_string(organizacao: Organizacao):
        return organizacao

    org = stringuify_value_func_guard_none(
        details.get("organizacao"),
        organizacao_string
    )

    capacidade = stringuify_value_func_guard_none(
        details.get("capacidade"),
        lambda c: f"capacidade {c}"
    )

    utentes = stringuify_value_func_guard_none(
        details.get("numero_de_utentes"),
        lambda u: f"utentes {u}"
    )

    return f"{_fins_lucrativos}{capacidade}{utentes}{org}"


def stringuify_cultural(details: CulturalDetails):

    mobilidade_reduzida = stringuify_value_func_guard_none(
        details.get("mobilidade_reduzida"),
        lambda v: "acesso mobilidade reduzida" if v
        else "sem acesso mobilidade reduzida"
    )

    acesso_gratuito = stringuify_value_func_guard_none(
        details.get("acesso_gratuito"),
        lambda v: "grátis" if v
        else "pago"
    )

    return f"{acesso_gratuito}{mobilidade_reduzida}"


def stringuify_sport(details: SportDetails):

    iluminado = stringuify_value_func_guard_none(
        details.get("iluminado"),
        lambda v: "iluminado" if v
        else "não iluminado"
    )

    mobilidade_reduzida_pratica = stringuify_value_func_guard_none(
        details.get("mobilidade_reduzida_pratica"),
        lambda v: "prática mobilidade reduzida" if v
        else "não possível prática mobilidade reduzida"
    )

    mobilidade_reduzida_assistencia = stringuify_value_func_guard_none(
        details.get("mobilidade_reduzida_assistencia"),
        lambda v: "assistência a mobilidade reduzida" if v
        else "sem assitência a mobilidade reduzida"
    )

    def instalacao_apoio_string(instalacoes_apoio: List[InstalacaoApoio]):
        return "\n".join(map(lambda a: a, instalacoes_apoio))

    apoio = stringuify_value_func_guard_none(
        details.get("instalacoes_apoio"),
        instalacao_apoio_string
    )

    tipo_piso = stringuify_value_func_guard_none(
        details.get("tipo_piso"),
        lambda v: v
    )

    capacidade = stringuify_value_func_guard_none(
        details.get("capacidade"),
        lambda v: f"com capacidade {v}"
    )

    return f"{iluminado}{mobilidade_reduzida_pratica}{mobilidade_reduzida_assistencia}{capacidade}{apoio}{tipo_piso}"


def stringuify_education(details: EducationDetails):

    # TODO: Does school have any non-required fields?

    escolas = stringuify_value_func_guard_none(
        details.get("escolas"),
        lambda escolas:
            ("\n".
                join(
                    map(
                        lambda s:
                        f"{s['grau_ensino']} com capacidade {s['capacidade']}. Alunos inscritos {s['numero_de_alunos']}",
                        escolas
                    )
                )
             )
    )

    return escolas


def stringuify_general_health(details: GeneralHealthDetails):

    capacidade = stringuify_value_func_guard_none(
        details.get("capacidade"),
        lambda v: f"capacidade {v}"
    )

    numero_centros_saude = stringuify_value_func_guard_none(
        details.get("numero_centros_saude"),
        lambda v: f"{v} centros de saude"
    )

    return f"{capacidade}{numero_centros_saude}"


def stringuify_hospital_health(details: HospitalHealthDetails):

    valencias = stringuify_value_func_guard_none(
        details.get("valencias"),
        lambda valencias: ','.join(valencias)
    )

    especialidades = stringuify_value_func_guard_none(
        details.get("especialidades"),
        lambda especialidades: ','.join(especialidades)
    )

    agrupamento_saude = stringuify_value_func_guard_none(
        details.get("agrupamento_saude"),
        lambda v: v
    )

    centro_hospitalar = stringuify_value_func_guard_none(
        details.get("centro_hospitalar"),
        lambda v: v
    )

    def unidade_string(unidade: Unidade):
        return unidade

    unidades = stringuify_value_func_guard_none(
        details.get("unidades"),
        lambda unidades: '\n'.join(map(unidade_string, unidades))
    )

    return f"{agrupamento_saude}{centro_hospitalar}{valencias}{especialidades}{unidades}"


def stringify_gas(details: GasDetails):

    num_consumo_gas = stringuify_value_func_guard_none(
        details.get("num_consumo_gas"),
        lambda s: dict_to_string(s) + "."
    )

    consumo_gas = stringuify_value_func_guard_none(
        details.get("consumo_gas"),
        lambda s: dict_to_string(s) + "."
    )

    pontos_acesso = stringuify_value_func_guard_none(
        details.get("pontos_acesso"),
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_consumo_gas}{consumo_gas}{pontos_acesso}"


def stringify_light(details: LightDetails):

    num_consumo_elec_p_atividade = stringuify_value_func_guard_none(
        details.get("num_consumo_elec_p_atividade"),
        lambda s: dict_to_string(s) + "."
    )

    consumo_elec_p_atividade = stringuify_value_func_guard_none(
        details.get("consumo_elec_p_atividade"),
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_consumo_elec_p_atividade}{consumo_elec_p_atividade}"


def stringuify_telephone(details: TelephoneDetails):

    num_postos = stringuify_value_func_guard_none(
        details.get("num_postos"),
        lambda s: dict_to_string(s) + "."
    )

    num_acessos = stringuify_value_func_guard_none(
        details.get("num_acessos"),
        lambda s: dict_to_string(s) + "."
    )

    num_acessos_p_100 = stringuify_value_func_guard_none(
        details.get("num_acessos_p_100"),
        lambda s: dict_to_string(s) + "."
    )

    num_postos_publicos = stringuify_value_func_guard_none(
        details.get("num_postos_publicos"),
        lambda s: dict_to_string(s) + "."
    )

    num_clientes = stringuify_value_func_guard_none(
        details.get("num_clientes"),
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_postos}{num_acessos}{num_acessos_p_100}{num_postos_publicos}{num_clientes}"


def stringuify_internet(details: InternetDetails):

    num_clientes_banda_larga = stringuify_value_func_guard_none(
        details.get("num_clientes_banda_larga"),
        lambda s: dict_to_string(s) + "."
    )

    num_acessos_banda_larga_100 = stringuify_value_func_guard_none(
        details.get("num_acessos_banda_larga_100"),
        lambda s: dict_to_string(s) + "."
    )

    num_acessos_banda_larga = stringuify_value_func_guard_none(
        details.get("num_acessos_banda_larga"),
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_clientes_banda_larga}{num_acessos_banda_larga_100}{num_acessos_banda_larga}"


def stringuify_mail(details: MailDetails):

    _ = stringuify_value_func_guard_none(
        details.get("_"),
        lambda s: dict_to_string(s) + "."
    )

    return _


def stringuify_tv(details: TVDetails):

    num_subscricoes = stringuify_value_func_guard_none(
        details.get("num_subscricoes"),
        lambda s: dict_to_string(s) + "."
    )

    num_clientes = stringuify_value_func_guard_none(
        details.get("num_clientes"),
        lambda s: dict_to_string(s) + "."
    )

    return f"{num_subscricoes}{num_clientes}"


class EquipmentTypeTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment):
        stringuified = stringuify(equipment)
        return self.model.encode(stringuified)
