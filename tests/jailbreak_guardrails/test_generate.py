import json
from unittest.mock import AsyncMock

import pytest

from govuk_chat_evaluation.jailbreak_guardrails.generate import (
    generate_inputs_to_evaluation_results,
    generate_and_write_dataset,
    GenerateInput,
    EvaluationResult,
)


@pytest.fixture
def run_rake_task_mock(mocker):
    return mocker.patch(
        "govuk_chat_evaluation.jailbreak_guardrails.generate.run_rake_task",
        new_callable=AsyncMock,
    )


def test_generate_models_to_evaluation_models_returns_evaluation_results(
    run_rake_task_mock,
):
    def result_per_question(_, env):
        if env["INPUT"] == "Question 1":
            return {"triggered": True}
        else:
            return {"triggered": False}

    run_rake_task_mock.side_effect = result_per_question
    generate_inputs = [
        GenerateInput(question="Question 1", expected_outcome=True),
        GenerateInput(question="Question 2", expected_outcome=False),
    ]
    expected_results = [
        EvaluationResult(
            question="Question 1", expected_outcome=True, actual_outcome=True
        ),
        EvaluationResult(
            question="Question 2", expected_outcome=False, actual_outcome=False
        ),
    ]
    actual_results = generate_inputs_to_evaluation_results("openai", generate_inputs)

    assert sorted(expected_results, key=lambda r: r.question) == sorted(
        actual_results, key=lambda r: r.question
    )


def test_generate_models_to_evaluation_models_runs_expected_rake_task(
    run_rake_task_mock,
):
    generate_inputs = [
        GenerateInput(question="Question 1", expected_outcome=True),
    ]
    generate_inputs_to_evaluation_results("openai", generate_inputs)

    run_rake_task_mock.assert_called_with(
        "evaluation:generate_jailbreak_guardrail_response[openai]",
        {"INPUT": "Question 1"},
    )


@pytest.mark.usefixtures("run_rake_task_mock")
def test_generate_and_write_dataset(mock_input_data, mock_project_root):
    path = generate_and_write_dataset(mock_input_data, "openai", mock_project_root)
    assert path.exists()
    with open(path, "r") as file:
        for line in file:
            assert json.loads(line)
