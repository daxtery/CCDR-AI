import logging

from ..models.user import User
from ..models.opening import Opening

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('matches')
logger.setLevel(logging.INFO)


def real_metric(similarity_score: float, quality_score: float, similarity_weight: float = .5, quality_weight: float = .5):
    return similarity_weight * similarity_score + quality_weight * quality_score


def quality_metric(user: User, opening: Opening, hardskill_weight: float = 0.6, softskill_weight: float = 0.4):
    u_h = set(user.hardSkills)
    u_s = set(user.softSkills)

    o_h = set(opening.hardSkills)
    o_s = set(opening.softSkills)

    if len(o_h) == 0:
        HS_s = 1
    else:
        HS_s = len(o_h.intersection(u_h)) / len(o_h)

    if len(o_s) == 0:
        SS_s = 1

    else:
        SS_s = len(o_s.intersection(u_s)) / len(o_s)

    Mq = hardskill_weight * HS_s + softskill_weight * SS_s

    return Mq