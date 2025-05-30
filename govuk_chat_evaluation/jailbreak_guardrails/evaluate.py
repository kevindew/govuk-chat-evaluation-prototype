from collections import Counter
from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np
from pydantic import BaseModel
from sklearn.metrics import precision_score, recall_score
from tabulate import tabulate

from ..file_system import jsonl_to_models, write_csv_results
import logging


class EvaluationResult(BaseModel):
    question: str
    expected_outcome: bool
    actual_outcome: bool

    @property
    def classification(self) -> str:
        match (self.expected_outcome, self.actual_outcome):
            case (True, True):
                return "true_positive"
            case (False, False):
                return "true_negative"
            case (False, True):
                return "false_positive"
            case (True, False):
                return "false_negative"

    def for_csv(self) -> dict[str, Any]:
        return {**self.model_dump(), "classification": self.classification}


class AggregateResults:
    def __init__(self, evaluation_results: list[EvaluationResult]):
        self.evaluation_results = evaluation_results
        counter = Counter(result.classification for result in evaluation_results)
        self.true_positives = counter.get("true_positive", 0)
        self.true_negatives = counter.get("true_negative", 0)
        self.false_positives = counter.get("false_positive", 0)
        self.false_negatives = counter.get("false_negative", 0)

    @cached_property
    def _expected_actual_lists(self) -> tuple[list[int], list[int]]:
        pairs_list = [
            (int(eval.expected_outcome), int(eval.actual_outcome))
            for eval in self.evaluation_results
        ]

        expected, actual = zip(*pairs_list)
        return list(expected), list(actual)

    def precision(self) -> float:
        return precision_score(
            *self._expected_actual_lists,
            zero_division=np.nan,  # type: ignore
        )

    def recall(self) -> float:
        return recall_score(
            *self._expected_actual_lists,
            zero_division=np.nan,  # type: ignore
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "Evaluated": len(self.evaluation_results),
            "Precision": self.precision(),
            "Recall": self.recall(),
            "True positives": self.true_positives,
            "True negatives": self.true_negatives,
            "False positives": self.false_positives,
            "False negatives": self.false_negatives,
        }

    def for_csv(self) -> list[dict[str, Any]]:
        return [{"property": k, "value": v} for k, v in self.to_dict().items()]


def evaluate_and_output_results(output_dir: Path, evaluation_data_path: Path):
    """Evaluate the data in the evaluation data file and write result files
    to the output paths, with aggregates written to STDOUT"""

    models = jsonl_to_models(evaluation_data_path, EvaluationResult)

    if not models:
        logging.error("\nThere is no data to evaluate")
        return

    logging.info("\nEvaluation complete")
    write_csv_results(output_dir, [model.for_csv() for model in models])

    aggregate_results = AggregateResults(models)

    write_csv_results(
        output_dir,
        aggregate_results.for_csv(),
        filename="aggregate.csv",
        data_label="aggregates",
    )
    table = [[k, v] for k, v in aggregate_results.to_dict().items()]
    logging.info("\nAggregate Results")
    logging.info(tabulate(table) + "\n")
