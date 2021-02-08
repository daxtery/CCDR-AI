import os
import logging

from ...transformers.user_transformer import UserTransformer
from ...transformers.opening_transformer import OpeningTransformer
from ...instances.user_instance import UserInstance, UserInstanceHelper
from ...instances.opening_instance import OpeningInstance, OpeningInstanceHelper
from ...transformers.opening_transformer import OpeningTransformer
from .data_reader import DataReaderUsers, DataReaderOpenings

from typing import List


class DataInitializer:

    @staticmethod
    def read_users(
        users_instances_path: str,
        users_path: str,
        user_transformer: UserTransformer = UserTransformer()
    ) -> List[UserInstance]:

        if os.path.exists(users_instances_path):

            logging.info("Users instances file found. Loading...")
            return UserInstanceHelper.load_instances(users_instances_path)

        else:
            logging.info("Users instances file not found. Reading Users...")

            users_files = [
                os.path.join(users_path, f) for f in os.listdir(users_path)
                if os.path.isfile(os.path.join(users_path, f))
            ]

            users = []
            for user_file in users_files:

                users += DataReaderUsers.populate(filename=user_file)

            logging.info("Creating instances...")

            users_instances = [
                user_transformer.transform(user)
                for user in users
            ]

            logging.info(f"Saving instances to {users_instances_path}...")

            UserInstanceHelper.save_instances(users_instances_path, users_instances)

            logging.info("Saved")

            return users_instances

    @staticmethod
    def read_openings(
        openings_instances_path: str, 
        openings_path: str,
        opening_transformer: OpeningTransformer=OpeningTransformer()
    ) -> List[OpeningInstance]:

        if os.path.exists(openings_instances_path):

            logging.info("Openings instances file found. Loading...")
            return OpeningInstanceHelper.load_instances(openings_instances_path)

        else:

            logging.info("Openings instances file not found. Reading Openings...")

            openings_files = [os.path.join(openings_path, f) for f in os.listdir(
                openings_path) if os.path.isfile(os.path.join(openings_path, f))]

            openings = []
            for opening_file in openings_files:

                openings += DataReaderOpenings.populate(filename=opening_file)

            logging.info("Creating instances...")

            openings_instances = [
                opening_transformer.transform(opening)
                for opening in openings
            ]

            logging.info(f"Saving instances to {openings_instances_path}...")

            OpeningInstanceHelper.save_instances(openings_instances_path, openings_instances)

            logging.info("Saved")

            return openings_instances
