from datetime import datetime
from pathlib import Path

import click
from pydantic import Field

from ..config import BaseConfig, apply_click_options_to_command, config_from_cli_args
from ..file_system import create_output_directory, write_config_file_for_reuse


class Config(BaseConfig):
    what: str = Field(..., description="what is being evaluated")


@click.command(name="rag_answers")
@click.argument(
    "config_path",
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    default="config/defaults/rag_answers.yaml",
)
@apply_click_options_to_command(Config)
def main(**cli_args):
    """Run RAG answers evaluation"""
    start_time = datetime.now()

    config: Config = config_from_cli_args(
        config_path=cli_args["config_path"],
        config_cls=Config,
        cli_args=cli_args,
    )

    output_dir = create_output_directory("rag_answers", start_time)

    write_config_file_for_reuse(output_dir, config)
