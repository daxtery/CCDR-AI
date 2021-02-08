from collections import Counter
import statistics
from trigger.scoring import TriggerScoring
from typing import List, Sequence

from interference.util.statistics import to_range, stats_from_counter, Stats

from interference.transformers.transformer_pipeline import Instance

def eval_matches(
        instances_to_match: Sequence[Instance],
        individual_scorings: Sequence[Sequence[TriggerScoring]]
    ):

    by_instance = []

    num_matches_counter = Counter()

    num_potential_counter = Counter()
    num_potential_after_similarity_counter = Counter()

    matches_score_range_counter = Counter()
    similarity_matches_score_range_counter = Counter()

    score_range_counter = Counter()
    similarity_score_range_counter = Counter()
    quality_score_range_counter = Counter()

    avg_matches_score_range_counter = Counter()
    avg_similarity_matches_score_range_counter = Counter()

    avg_score_range_counter = Counter()
    avg_similarity_score_range_counter = Counter()
    avg_quality_score_range_counter = Counter()

    for instance, scorings in zip(instances_to_match, individual_scorings):

        scoring_scores = [
            scoring.score
            for scoring in scorings
        ]

        similarity_scores = [
            scoring.similarity_score
            for scoring in scorings
        ]

        quality_scores = [
            scoring.quality_score
            for scoring in scorings
        ]

        similarity_matches = list(filter(lambda scoring: scoring.is_similarity_match, scorings))

        similarity_match_scores = [
            similarity_match.similarity_score
            for similarity_match in similarity_matches
        ]

        matches = list(filter(lambda scoring: scoring.is_match, scorings))

        match_scores = [
            match.score
            for match in matches
        ]

        these_results = {
            'value': instance.value,
            '#matches': len(match_scores),
            '#potential': len(scoring_scores),
            '#potential after similarity': len(similarity_match_scores),
            'average score': statistics.mean(scoring_scores) if len(scoring_scores) > 0 else 0,
            'average match score': statistics.mean(match_scores) if len(match_scores) > 0 else 0,
            'average similarity match score': statistics.mean(similarity_match_scores) if len(similarity_match_scores) > 0 else 0,
            'average similarity score': statistics.mean(similarity_scores) if len(similarity_scores) > 0 else 0,
            'average quality score': statistics.mean(quality_scores) if len(quality_scores) > 0 else 0,
            'matches': list(matches)
        }

        by_instance.append(these_results)

        num_matches_counter.update([these_results['#matches']])

        num_potential_counter.update([these_results['#potential']])
        num_potential_after_similarity_counter.update([these_results['#potential after similarity']])

        for similarity_match in similarity_matches:
            similarity_matches_score_range_counter.update([to_range(similarity_match.similarity_score, 5)])

        for match in matches:
            matches_score_range_counter.update([to_range(match.score, 5)])

        for scoring in scorings:
            score_range_counter.update([to_range(scoring.score, 5)])
            similarity_score_range_counter.update([to_range(scoring.similarity_score, 5)])
            quality_score_range_counter.update([to_range(scoring.quality_score, 5)])

        if len(similarity_match_scores) > 0:
            avg_similarity_matches_range = to_range(these_results['average similarity match score'], 5)
            avg_similarity_matches_score_range_counter += Counter([avg_similarity_matches_range])

        if len(match_scores) > 0:
            avg_matches_range = to_range(these_results['average match score'], 5)
            avg_matches_score_range_counter += Counter([avg_matches_range])
            
        avg_score_range = to_range(these_results['average score'], 5)
        avg_score_range_counter += Counter([avg_score_range])

        avg_similarity_score_range = to_range(these_results['average similarity score'], 5)
        avg_similarity_score_range_counter += Counter([avg_similarity_score_range])

        avg_quality_score_range = to_range(these_results['average quality score'], 5)
        avg_quality_score_range_counter += Counter([avg_quality_score_range])


    json_obj = {}

    def add_stats_to_json(name: str, stats: Stats):
        nonlocal json_obj
        distribution, number_stats = stats
        json_obj[f"distribution {name}"] = distribution

        if (number_stats):
            avg, max, min = number_stats
            json_obj[f"average {name}"]= avg
            json_obj[f"max {name}"]= max
            json_obj[f"min {name}"]= min

    add_stats_to_json("#matches", stats_from_counter(num_matches_counter))
    add_stats_to_json("matches score range", stats_from_counter(matches_score_range_counter))
    add_stats_to_json("average matches score range", stats_from_counter(avg_matches_score_range_counter))

    json_obj["% at least 1 match"] = (1 - (num_matches_counter.get(0, 0) / sum(num_matches_counter.values()))) * 100

    add_stats_to_json("#potential after similarity", stats_from_counter(num_potential_after_similarity_counter))
    add_stats_to_json("similarity matches score range", stats_from_counter(matches_score_range_counter))
    add_stats_to_json("average similarity matches score range", stats_from_counter(avg_matches_score_range_counter))

    add_stats_to_json("#potential", stats_from_counter(num_potential_counter))

    add_stats_to_json("score range", stats_from_counter(score_range_counter))
    add_stats_to_json("average score range", stats_from_counter(avg_score_range_counter))

    add_stats_to_json("similarity score range", stats_from_counter(similarity_score_range_counter))
    add_stats_to_json("average similarity score range", stats_from_counter(avg_similarity_score_range_counter))
    
    add_stats_to_json("quality score range", stats_from_counter(quality_score_range_counter))
    add_stats_to_json("average quality score range", stats_from_counter(avg_quality_score_range_counter))

    json_obj["by_instance"] = by_instance

    return json_obj