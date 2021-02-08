import os
import logging
from typing import List

from trigger.instances.opening_instance import OpeningInstance, OpeningInstanceHelper
from trigger.instances.user_instance import UserInstance, UserInstanceHelper

from interference.operations import Operation, OperationType, AddInfo, UpdateInfo, RemoveInfo


import io
import pickle


class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module: str, name):
        new_module = module
        new_name = name

        #print(">>>", module, name)

        if module.find("trigger_project") != -1:
            new_module = module.replace("trigger_project", "trigger")

        if name == "OpeningInstance":
            new_name = "FakeOI"

        elif name == "UserInstance":
            new_name = "FakeUI"

        #print("<<<", new_module, new_name)

        return super(RenameUnpickler, self).find_class(new_module, new_name)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()


def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)


# What I did:
# Create files with a different name. (For example Softskill -> Softskillz)
# Read the old embeddings and replace old Softskill for new one
# Save
# Delete file with the correct name (Softskill)
# Rename Softskillz -> Softskill
# edit the find_class and add something like:

# elif module == "trigger.models.softskillz":
#            renamed_module = "trigger.models.softskill"

# Run this again

def rename_instances(instances_paths: List[str]):
    for instances_path in instances_paths:

        instances_files = [
            os.path.join(instances_path, f)
            for f in os.listdir(instances_path)
            if os.path.isfile(os.path.join(instances_path, f))
        ]

        users_instances_files = [
            instance_path
            for instance_path in instances_files
            if instance_path.find("users") != -1
        ]

        openings_instances_files = [
            instance_path
            for instance_path in instances_files
            if instance_path.find("openings") != -1
        ]

        for users_instances_path in users_instances_files:

            logging.info("Users instances " + users_instances_path)

            with open(users_instances_path, 'rb') as file:
                users_instances = renamed_load(file)
                users_instances = [ UserInstance(fui.value, fui.embedding) for fui in users_instances ]

            UserInstanceHelper.save_instances(users_instances_path, users_instances)

        for openings_instances_path in openings_instances_files:

            logging.info("Opening instances " + openings_instances_path)

            with open(openings_instances_path, 'rb') as file:
                openings_instances = renamed_load(file)
                openings_instances = [ OpeningInstance(fui.value, fui.embedding) for fui in openings_instances ]

            OpeningInstanceHelper.save_instances(openings_instances_path, openings_instances)

def rename_operations(operations_folder: str):
    for operations_test in os.listdir(operations_folder):

        instances_files = [
            os.path.join(os.path.join(operations_folder, operations_test, f))
            for f in os.listdir(os.path.join(operations_folder, operations_test))
            if os.path.isfile(os.path.join(operations_folder, operations_test, f))
        ]

        users_instances_files = [
            instance_path
            for instance_path in instances_files
            if instance_path.find("users") != -1
        ]

        openings_instances_files = [
            instance_path
            for instance_path in instances_files
            if instance_path.find("openings") != -1
        ]

        for users_instances_path in users_instances_files:

            logging.info("Users instances " + users_instances_path)

            with open(users_instances_path, 'rb') as file:
                users_instances = renamed_load(file)

            UserInstanceHelper.save_instances(users_instances_path, users_instances)

        for openings_instances_path in openings_instances_files:

            logging.info("Opening instances " + openings_instances_path)

            with open(openings_instances_path, 'rb') as file:
                openings_instances = renamed_load(file)

            OpeningInstanceHelper.save_instances(openings_instances_path, openings_instances)

def rename_projects(projects_folder: str):

    for projects_path in os.listdir(projects_folder):

        with open(os.path.join(projects_folder, projects_path), 'rb') as file:
            projects = renamed_load(file)

        with open(os.path.join(projects_folder, projects_path), 'wb') as file:
            pickle.dump(projects, file)

def correct_entity_id(instances_paths):
    for instances_path in instances_paths:

        instances_files = [
            os.path.join(instances_path, f)
            for f in os.listdir(instances_path)
            if os.path.isfile(os.path.join(instances_path, f))
        ]

        openings_instances_files = [
            instance_path
            for instance_path in instances_files
            if instance_path.find("openings") != -1
        ]

        for openings_instances_path in openings_instances_files:

            logging.info("Opening instances " + openings_instances_path)

            with open(openings_instances_path, 'rb') as file:
                openings_instances = pickle.load(file)

            for i, opening_instance in enumerate(openings_instances):
                opening_instance.opening.entityId = str(i)

            OpeningInstanceHelper.save_instances(openings_instances_path, openings_instances)
