import click

from . import jailbreak_guardrails
from . import output_guardrails


@click.group()
def main():
    """Command line interface to run evaluations of GOV.UK chat"""


main.add_command(jailbreak_guardrails.main)
main.add_command(output_guardrails.main)
