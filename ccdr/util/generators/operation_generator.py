import random
from trigger.instances.user_instance import UserInstance

from typing import Dict, List, Tuple

from ...instances.opening_instance import OpeningInstance

from interference.operations import Operation, OperationType, AddInfo, UpdateInfo, RemoveInfo, CalculateMatchesInfo, CalculateScoringInfo, EvaluateClustersInfo, EvaluateMatchesInfo

def random_from_instances(
            opening_instances: List[OpeningInstance],
            users_instances: List[UserInstance],
            operation_blueprints: List[Tuple[OperationType, int]],
            should_evaluate_fetch_instance: bool = False
        ) -> List[Operation]:
        operations = []

        usable_opening_instances = random.sample(opening_instances, len(opening_instances))
        added_opening_instances: Dict[str, OpeningInstance] = {}

        for operation_type, number  in operation_blueprints:

            for _ in range(number):
            
                if operation_type == OperationType.ADD:

                    opening_instance = random.choice(usable_opening_instances)
                    tag = opening_instance.value.entityId

                    usable_opening_instances.remove(opening_instance)
                    added_opening_instances[tag] = opening_instance

                    operations.append(
                        Operation(
                            type=operation_type,
                            info=AddInfo(tag, opening_instance, "identity"))
                    )

                elif operation_type == OperationType.UPDATE:

                    opening_instance = random.choice(usable_opening_instances)

                    old_opening_instance = random.choice(list(added_opening_instances.values()))

                    usable_opening_instances.remove(opening_instance)
                    usable_opening_instances.append(old_opening_instance)

                    tag_to_replace = old_opening_instance.value.entityId
                    tag = opening_instance.value.entityId

                    opening_instance.value.entityId = tag_to_replace
                    old_opening_instance.value.entityId = tag

                    added_opening_instances[tag_to_replace] = opening_instance

                    operations.append(
                        Operation(
                            type=operation_type,
                            info=UpdateInfo(tag_to_replace, opening_instance, "identity"),
                        )
                    )
                elif operation_type == OperationType.REMOVE:

                    old_opening_instance = random.choice(list(added_opening_instances.keys()))

                    usable_opening_instances.append(added_opening_instances.pop(old_opening_instance))

                    operations.append(
                        Operation(
                            type=operation_type,
                            info=RemoveInfo(old_opening_instance),
                        )
                    )
                    
                elif operation_type == OperationType.CALCULATE_SCORES:

                    user_instance = random.choice(users_instances)

                    operation = Operation(
                        type=operation_type,
                        info=CalculateScoringInfo(user_instance, "identity")
                    )

                    operations.append(operation)

                elif operation_type == OperationType.CALCULATE_MATCHES:
                    user_instance = random.choice(users_instances)
                    
                    operations.append(
                        Operation(
                            type=operation_type,
                            info=CalculateMatchesInfo(user_instance, "identity"),
                        )
                    )

                elif operation_type == OperationType.EVALUATE_CLUSTERS:
                    operations.append(
                        Operation(
                            type=operation_type,
                            info=EvaluateClustersInfo(),
                        )
                    )

                elif operation_type == OperationType.EVALUATE_MATCHES:
                    operations.append(
                        Operation(
                            type=operation_type,
                            info=EvaluateMatchesInfo(values=[
                                CalculateMatchesInfo(user_instance, "identity")
                                for user_instance in users_instances
                            ], fetch_instance=should_evaluate_fetch_instance),
                        )
                    )

        return operations

    
def add_all_then_evaluate(
        opening_instances: List[OpeningInstance],
        users_instances: List[UserInstance],
        eval_matches: bool = True,
        eval_clusters: bool = True,
    ) -> List[Operation]:

    add_all: List[Tuple[OperationType, int]] = [
        (OperationType.ADD, len(opening_instances)),
    ]

    if eval_clusters:
        add_all.append((OperationType.EVALUATE_CLUSTERS, 1))
    if eval_matches:
        add_all.append((OperationType.EVALUATE_MATCHES, 1))

    return random_from_instances(opening_instances, users_instances, add_all)