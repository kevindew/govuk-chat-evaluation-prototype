import json
from unittest.mock import AsyncMock

import pytest

from govuk_chat_evaluation.output_guardrails.generate import (
    generate_inputs_to_evaluation_results,
    generate_and_write_dataset,
    GenerateInput,
)

from govuk_chat_evaluation.output_guardrails.evaluate import EvaluationResult


@pytest.fixture
def run_rake_task_mock(mocker):
    async def default_side_effect(_, env):
        if env["INPUT"] == "Question 1":
            return {
                "triggered": True,
                "guardrails": {
                    "appropriate_language": True,
                    "political": True,
                    "contains_pii": False,
                },
            }
        else:
            return {
                "triggered": False,
                "guardrails": {
                    "appropriate_language": False,
                    "political": False,
                    "contains_pii": False,
                },
            }

    mock = mocker.patch(
        "govuk_chat_evaluation.output_guardrails.generate.run_rake_task",
        new_callable=AsyncMock,
    )
    mock.side_effect = default_side_effect
    return mock


def test_generate_inputs_to_evaluation_results_returns_evaluation_results(
    run_rake_task_mock,
):
    generate_inputs = [
        GenerateInput(
            question="Question 1",
            expected_triggered=True,
            expected_guardrails={
                "appropriate_language": True,
                "political": True,
                "contains_pii": False,
            },
        ),
        GenerateInput(
            question="Question 2",
            expected_triggered=False,
            expected_guardrails={
                "appropriate_language": False,
                "political": False,
            },
        ),
    ]
    expected_results = [
        EvaluationResult(
            question="Question 1",
            expected_triggered=True,
            actual_triggered=True,
            expected_guardrails={
                "appropriate_language": True,
                "political": True,
                "contains_pii": False,
            },
            actual_guardrails={
                "appropriate_language": True,
                "political": True,
                "contains_pii": False,
            },
        ),
        EvaluationResult(
            question="Question 2",
            expected_triggered=False,
            actual_triggered=False,
            expected_guardrails={
                "appropriate_language": False,
                "political": False,
            },
            actual_guardrails={
                "appropriate_language": False,
                "political": False,
                "contains_pii": False,
            },
        ),
    ]
    actual_results = generate_inputs_to_evaluation_results(
        "openai", "answer_guardrails", generate_inputs
    )

    assert sorted(expected_results, key=lambda r: r.question) == sorted(
        actual_results, key=lambda r: r.question
    )


def test_generate_inputs_to_evaluation_results_runs_expected_rake_task(
    run_rake_task_mock,
):
    generate_inputs = [
        GenerateInput(
            question="Question 1",
            expected_triggered=True,
            expected_guardrails={"appropriate_language": True},
        ),
    ]
    generate_inputs_to_evaluation_results(
        "openai", "answer_guardrails", generate_inputs
    )

    run_rake_task_mock.assert_called_with(
        "evaluation:generate_output_guardrail_response[openai,answer_guardrails]",
        {"INPUT": "Question 1"},
    )


@pytest.mark.usefixtures("run_rake_task_mock")
def test_generate_and_write_dataset(mock_input_data, mock_project_root):
    path = generate_and_write_dataset(
        mock_input_data, "openai", "answer_guardrails", mock_project_root
    )
    assert path.exists()
    with open(path, "r") as file:
        for line in file:
            assert json.loads(line)
