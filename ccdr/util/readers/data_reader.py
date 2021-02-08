from typing import List

from ...models.opening import Opening
from ...models.softskill import Softskill
from ...models.hardskill import Hardskill
from ...models.user import User


class DataReaderUsers:

    @staticmethod
    def populate(filename: str) -> List[User]:

        users = []

        state_starts = {0: "User:",
                        1: "Hardskills:",
                        2: "Softskills:"}

        with open(filename, 'r') as file:

            lines = file.readlines()
            state = 0
            username = ''
            hardskills = []
            softskills = []

            for line in lines:

                if state == 0 and line.startswith(state_starts[state]):
                    state = 1
                    username = line.split(":", 1)[1].strip()

                elif state == 1 and line.startswith(state_starts[state]):

                    state = 2
                    hardskills_temp = line.split(":", 1)[1].strip()
                    hardskills = [h_t.strip() for h_t in hardskills_temp.split(
                        ",") if h_t.strip() != '']

                elif state == 2 and line.startswith(state_starts[state]):

                    state = 0
                    softskills_temp = line.split(":", 1)[1].strip()
                    softskills = [s_t.strip() for s_t in softskills_temp.split(
                        ",") if s_t.strip() != '']

                    user_softskills = [
                        Softskill(name=softskill) for softskill in softskills]
                    user_hardskills = [
                        Hardskill(name=hardskill) for hardskill in hardskills]

                    user = User(name=username, hardSkills=user_hardskills,
                                softSkills=user_softskills)

                    username = ''
                    hardskills = []
                    softskills = []

                    users.append(user)

        return users


class DataReaderOpenings:

    def __init__(self):
        pass

    @staticmethod
    def populate(filename: str) -> List[Opening]:

        openings = []

        state_starts = {0: "Sector:",
                        1: "Area:", 2: "Hardskills:",
                        3: "Softskills:"}

        with open(filename, 'r') as file:

            lines = file.readlines()
            state = 0
            sector = ''
            area = ''
            hardskills = []
            softskills = []

            for line in lines:

                if state == 0 and line.startswith(state_starts[state]):

                    state = 1
                    sector = line.split(":", 1)[1].strip()

                elif state == 1 and line.startswith(state_starts[state]):

                    state = 2
                    area = line.split(":", 1)[1].strip()

                elif state == 2 and line.startswith(state_starts[state]):

                    state = 3
                    hardskills_temp = line.split(":", 1)[1].strip()
                    hardskills = [h_t.strip() for h_t in hardskills_temp.split(
                        ",") if h_t.strip() != '']

                elif state == 3 and line.startswith(state_starts[state]):

                    state = 0
                    softskills_temp = line.split(":", 1)[1].strip()
                    softskills = [s_t.strip() for s_t in softskills_temp.split(
                        ",") if s_t.strip() != '']

                    opening_softskills = [
                        Softskill(name=softskill) for softskill in softskills]

                    opening_hardskills = [
                        Hardskill(name=hardskill) for hardskill in hardskills]

                    opening = Opening(entityId=str(len(openings)), hardSkills=opening_hardskills,
                                      softSkills=opening_softskills)

                    openings.append(opening)

        return openings
