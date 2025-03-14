from argparse import ArgumentParser

from . import jailbreak_guardrails


def main():
    parser = ArgumentParser(
        prog="govuk_chat_evaluation",
        description=("Command line interface to run evaluations of GOV.UK chat"),
        add_help=False,
    )

    parser.add_argument(
        "evaluation",
        nargs="?",
        choices=["jailbreak_guardrails"],
        help="The evaluation to run",
    )

    args, remaining_args = parser.parse_known_args()

    match args.evaluation:
        case "jailbreak_guardrails":
            jailbreak_guardrails.main(remaining_args)
        case _:
            parser.print_help()
