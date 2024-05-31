"""The configuration module for the ftf package."""

from __future__ import annotations

import datetime

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from argparse import Namespace
    from pathlib import Path

    from ftf.output import Output


@dataclass
class Config:
    """The configuration data for the ftf package."""

    args: Namespace
    editor: str
    output: Output
    tmp_path: Path
    session_id: str = ""

    def __post_init__(self: Config) -> None:
        """Post initialization."""
        self.session_id = datetime.datetime.now(datetime.timezone.utc).strftime(
            "%y%m%d-%H%M%S",
        )
