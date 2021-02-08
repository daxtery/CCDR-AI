from typing import List
from ccdr.models.fct_data import FCTData
from ccdr.models.position import Position
from dataclasses import dataclass
from enum import Enum
import datetime


class KnowledgeFocusType(str, Enum):
    INVESTIGATION = "Investigação",
    INNOVATION = "Inovação",
    TRANSFERENCE = "Transferência"


class KnowledgeActivityType(str, Enum):
    COURSE = "Curso",
    FORMATION_FOR_WORK = "Formação em contexto de trabalho",
    PRIVATE = "Aula privada/particular",
    WORKSHOP = "Workshop",
    SEMINAR = "Seminário",
    LECTURE = "Palestra",
    CONFERENCE = "Conferência",


class KnowledgeActivityRegime(str, Enum):
    PRESENTIAL = "Presencial",
    ONLINE_VIDEOCONFERENCE = "Online/videoconferência",
    E_LEARNING = "E-learning",


class KnowledgeActivityDemographic(str, Enum):
    ALL = "População em geral",
    SIXTY_FIVE_AND_ABOVE = "População com 65 e + anos",
    UNTIL_14 = "Crianças até aos 14 anos",
    FIFTEEN_TO_TWENTY_FOUR = "Jovens entre os 15 e os 24 anos",


class Competence(str, Enum):
    FLEXIBILITY = "Adaptação e Flexibilidade",
    COMMUNICATION = "Comunicação",
    CREATIVITY = "Creatividade e Inovação",
    ENTREPRENEURSHIP = "Empreendedorismo",
    CONFLICT_RESOLUTION = "Gestão de Conflitos",
    TIME_MANAGEMENT = "Gestão de Tempo",
    EMOTIONAL_INTELLIGENCE = "Inteligência Emocional",
    LEADERSHIP = "Liderança",
    CRITICAL_THINKING = "Pensamento Critico",
    PLANNING = "Planeamento e Organização",
    PROACTIVITY = "Proatividade/Iniciativa",
    INTERPERSONAL_RELATIONSHIP = "Relacionamento interpessoal",
    PROBLEM_SOLVING = "Resolução de Problemas",
    PROBLEM_SOLVING_AND_DECISION_TAKING = "Resolução de problemas e Tomada de decisão",
    TEAMWORK = "Trabalho em equipa e Colaboração",


@dataclass
class KnowledgeActivity:
    title: str
    area: str  # TODO: Is this strongly typed?
    subtype: KnowledgeActivityType
    regime: KnowledgeActivityRegime
    duration_hours: float  # 22.5 h...
    expected_start_date: datetime.date  # TODO: not sure if dates are useful
    expected_end_date: datetime.date  # TODO: not sure if dates are useful
    demographic: KnowledgeActivityDemographic
    promoted_competences: List[Competence]
    postion: Position


@dataclass
class KnowledgeEntity:
    name: str
    subtype: KnowledgeFocusType
    position: Position
    fct_info: FCTData
    keywords: List[str]
    activites: List[KnowledgeActivity]
