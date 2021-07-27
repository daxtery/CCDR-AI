from collections import defaultdict
from ccdr.models.infrastructure import CommunicationDetails, EnergyDetails, GasDetails, InternetDetails, LightDetails, MailDetails, TVDetails, TelephoneDetails
from typing import Any, Callable, Optional, TypeVar, Dict, List, cast
from interference.transformers.transformer_pipeline import TransformerPipeline, Instance

from sentence_transformers import SentenceTransformer

from ccdr.models.equipment import CulturalDetails, Equipment, InstalacaoApoio, Localizacao, Organizacao, SportDetails, SocialDetails, EducationDetails, GeneralHealthDetails, HospitalHealthDetails, Unidade, HealthDetails

from ccdr.utils.string import stringuify_value_func_guard_none, tuple_dict_list_to_string


def stringuify(equipment: Equipment):

    def _stringuify_details():
        details = equipment.get("equipmentDetails")
        if details is None:
            return equipment.get("area")

        if equipment["group"] == "equipment":
            if equipment["area"] == "social":
                return stringuify_social(details)  # type:ignore

            elif equipment["area"] == "cultura":
                return stringuify_cultural(details)  # type:ignore

            elif equipment["area"] == "educacao":
                return stringuify_education(details)  # type:ignore

            elif equipment["area"] == "desporto":
                return stringuify_sport(details)  # type:ignore

            elif equipment["area"] == "saude":
                healt_details = cast(HealthDetails, details)

                num_utentes = stringuify_value_func_guard_none(
                    healt_details.get("num_utentes"),
                    lambda u: f"{u} utentes."
                )

                if healt_details["tipo_saude"] == "saude_geral":
                    finer = stringuify_general_health(
                        healt_details["healh_details"])  # type:ignore

                elif healt_details["tipo_saude"] == "saude_hospitalar":
                    finer = stringuify_hospital_health(
                        healt_details["healh_details"])  # type:ignore

                else:
                    finer = ""

                return f"{num_utentes}{finer}"

        elif equipment["group"] == "infra":

            if equipment["area"] == "energia":
                energy_details = cast(EnergyDetails, details)

                num_operadores = stringuify_value_func_guard_none(
                    energy_details.get("num_operadores"),
                    lambda v: f"{v} operadores."
                )

                if energy_details.get("tipo_energia") == "gas":
                    finer = stringify_gas(
                        energy_details["energy_details"])   # type:ignore

                elif energy_details.get("tipo_energia") == "luz":
                    finer = stringify_light(
                        energy_details["energy_details"])   # type:ignore

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
                    finer = stringuify_telephone(
                        communication_details["communication_details"])   # type:ignore

                elif communication_details.get("tipo_comunicacao") == "internet":
                    finer = stringuify_internet(
                        communication_details["communication_details"])   # type:ignore

                elif communication_details.get("tipo_comunicacao") == "correio":
                    finer = stringuify_mail(
                        communication_details["communication_details"])   # type:ignore

                elif communication_details.get("tipo_comunicacao") == "televisao":
                    finer = stringuify_tv(
                        communication_details["communication_details"])   # type:ignore

                else:
                    finer = ""

                return f"{num_operadores}{finer}"

        return equipment["area"]

    # TODO: Horário?
    # TODO: numero_de_equipamentos?

    def loc_string(localizacao: Localizacao):
        return f"{localizacao['lat']}:{localizacao['long']}"

    loc = stringuify_value_func_guard_none(
        equipment.get("localizacao"),
        loc_string
    )

    extras = ". ".join(
        map(lambda e: f"{e['name']} {e['value']}", equipment['extras'])
    )

    return f"{equipment['name']}, {loc}.{equipment['description']}.{_stringuify_details()}.{extras}".strip()


def stringuify_social(details: SocialDetails):
    def fins_lucrativos_string(f: bool):
        return "Para fins lucrativos." if f else "Sem fins lucrativos."

    _fins_lucrativos = stringuify_value_func_guard_none(
        details.get("fins_lucrativos"),
        fins_lucrativos_string
    )

    def organizacao_string(organizacao: Organizacao):
        return organizacao + "."

    org = stringuify_value_func_guard_none(
        details.get("organizacao"),
        organizacao_string
    )

    capacidade = stringuify_value_func_guard_none(
        details.get("capacidade"),
        lambda c: f"capacidade {c}."
    )

    utentes = stringuify_value_func_guard_none(
        details.get("num_utentes"),
        lambda u: f"{u} utentes."
    )

    return f"{_fins_lucrativos}{capacidade}{utentes}{org}"


def stringuify_cultural(details: CulturalDetails):

    mobilidade_reduzida = stringuify_value_func_guard_none(
        details.get("mobilidade_reduzida"),
        lambda v: "Acesso mobilidade reduzida." if v
        else "Sem acesso mobilidade reduzida."
    )

    acesso_gratuito = stringuify_value_func_guard_none(
        details.get("acesso_gratuito"),
        lambda v: "Grátis." if v
        else "Pago."
    )

    return f"{acesso_gratuito}{mobilidade_reduzida}"


def stringuify_sport(details: SportDetails):

    iluminado = stringuify_value_func_guard_none(
        details.get("iluminado"),
        lambda v: "Iluminado." if v
        else "Não iluminado."
    )

    mobilidade_reduzida_pratica = stringuify_value_func_guard_none(
        details.get("mobilidade_reduzida_pratica"),
        lambda v: "Prática mobilidade reduzida." if v
        else "Não possível prática mobilidade reduzida."
    )

    mobilidade_reduzida_assistencia = stringuify_value_func_guard_none(
        details.get("mobilidade_reduzida_assistencia"),
        lambda v: "Assistência a mobilidade reduzida." if v
        else "Sem assistência a mobilidade reduzida."
    )

    def instalacao_apoio_string(instalacoes_apoio: List[InstalacaoApoio]):
        return ". ".join(map(lambda a: a, instalacoes_apoio)) + "."

    apoio = stringuify_value_func_guard_none(
        details.get("instalacao_apoio"),
        instalacao_apoio_string
    )

    tipo_piso = stringuify_value_func_guard_none(
        details.get("tipo_piso"),
        lambda v: f"Piso do tipo {v}."
    )

    capacidade = stringuify_value_func_guard_none(
        details.get("capacidade"),
        lambda v: f"Capacidade {v}."
    )

    return f"{iluminado}{mobilidade_reduzida_pratica}{mobilidade_reduzida_assistencia}{capacidade}{apoio}{tipo_piso}"


def stringuify_education(details: EducationDetails):

    # TODO: Does school have any non-required fields?

    escolas = stringuify_value_func_guard_none(
        details.get("escolas"),
        lambda escolas:
            (". ".
                join(
                    map(
                        lambda s:
                        f"{s['grau_ensino']} {s['num_alunos']} alunos inscritos e com capacidade {s['capacidade']}.",
                        escolas
                    )
                )
             )
    )

    return escolas


def stringuify_general_health(details: GeneralHealthDetails):

    capacidade = stringuify_value_func_guard_none(
        details.get("capacidade"),
        lambda v: f"capacidade {v}."
    )

    numero_centros_saude = stringuify_value_func_guard_none(
        details.get("numero_centros_saude"),
        lambda v: f"{v} centros de saude."
    )

    return f"{capacidade}{numero_centros_saude}"


def stringuify_hospital_health(details: HospitalHealthDetails):

    valencias = stringuify_value_func_guard_none(
        details.get("valencias"),
        lambda valencias: ','.join(valencias) + "."
    )

    especialidades = stringuify_value_func_guard_none(
        details.get("especialidades"),
        lambda especialidades: ','.join(especialidades) + "."
    )

    agrupamento_saude = stringuify_value_func_guard_none(
        details.get("agrupamento_saude"),
        lambda v: v + "."
    )

    centro_hospitalar = stringuify_value_func_guard_none(
        details.get("centro_hospitalar"),
        lambda v: f"Pertencente ao centro hospitalar {v}."
    )

    def unidade_string(unidade: Unidade):
        return unidade

    unidades = stringuify_value_func_guard_none(
        details.get("unidades"),
        lambda unidades: '. '.join(map(unidade_string, unidades))
    )

    return f"{agrupamento_saude}{centro_hospitalar}{valencias}{especialidades}{unidades}"


def stringify_gas(details: GasDetails):

    num_consumo_gas = stringuify_value_func_guard_none(
        details.get("num_consumo_gas"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    consumo_gas = stringuify_value_func_guard_none(
        details.get("consumo_gas"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    pontos_acesso = stringuify_value_func_guard_none(
        details.get("pontos_acesso"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    return f"{num_consumo_gas}{consumo_gas}{pontos_acesso}"


def stringify_light(details: LightDetails):

    num_consumo_elec_p_atividade = stringuify_value_func_guard_none(
        details.get("num_consumo_elec_p_atividade"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    consumo_elec_p_atividade = stringuify_value_func_guard_none(
        details.get("consumo_elec_p_atividade"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    return f"{num_consumo_elec_p_atividade}{consumo_elec_p_atividade}"


def stringuify_telephone(details: TelephoneDetails):

    num_postos = stringuify_value_func_guard_none(
        details.get("num_postos"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    num_acessos = stringuify_value_func_guard_none(
        details.get("num_acessos"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    num_acessos_p_100 = stringuify_value_func_guard_none(
        details.get("num_acessos_p_100"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    num_postos_publicos = stringuify_value_func_guard_none(
        details.get("num_postos_publicos"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    num_clientes = stringuify_value_func_guard_none(
        details.get("num_clientes"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    return f"{num_postos}{num_acessos}{num_acessos_p_100}{num_postos_publicos}{num_clientes}"


def stringuify_internet(details: InternetDetails):

    num_clientes_banda_larga = stringuify_value_func_guard_none(
        details.get("num_clientes_banda_larga"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    num_acessos_banda_larga_100 = stringuify_value_func_guard_none(
        details.get("num_acessos_banda_larga_100"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    num_acessos_banda_larga = stringuify_value_func_guard_none(
        details.get("num_acessos_banda_larga"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    return f"{num_clientes_banda_larga}{num_acessos_banda_larga_100}{num_acessos_banda_larga}"


def stringuify_mail(details: MailDetails):
    return tuple_dict_list_to_string(details)


def stringuify_tv(details: TVDetails):

    num_subscricoes = stringuify_value_func_guard_none(
        details.get("num_subscricoes"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    num_clientes = stringuify_value_func_guard_none(
        details.get("num_clientes"),
        lambda s: tuple_dict_list_to_string(s) + "."
    )

    return f"{num_subscricoes}{num_clientes}"


class EquipmentTypeTransformer(TransformerPipeline[Equipment]):

    def __init__(self, modelname: str = 'neuralmind/bert-large-portuguese-cased'):
        self.model = SentenceTransformer(modelname)

    def calculate_embedding(self, equipment: Equipment):
        stringuified = stringuify(equipment)
        return self.model.encode(stringuified)
