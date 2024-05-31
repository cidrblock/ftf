"""Check the tox.ini file."""

from __future__ import annotations

import shutil

from typing import TYPE_CHECKING, Unpack

from ftf.checks.check_base import CheckBase, CheckBaseParams
from ftf.utils import load_txt_file, path_to_data_file


if TYPE_CHECKING:
    from pathlib import Path


class Check(CheckBase):
    """Perform full file comparisons."""

    def __init__(self: Check, **kwargs: Unpack[CheckBaseParams]) -> None:
        """Initialize the class.

        Args:
            **kwargs: The parameters.
        """
        super().__init__(**kwargs)

        self._base_file_content: str
        self._base_file_path: Path

    def run(self: Check, file_data: dict[str, list[str]]) -> bool:
        """Run the check.

        Args:
            file_data: The data for the file.

        Returns:
            True if PRs were made, False otherwise.
        """
        src_file_name = self.file_name
        if self.file_name.startswith("__"):
            self.file_name = self.file_name[2:]

        self._base_file_path = path_to_data_file(src_file_name)
        self._base_file_content = load_txt_file(self._base_file_path)
        skip = file_data.get("skip", [])

        for repo in self.repo_list:
            if repo.name in skip:
                msg = f"[{repo.name}] Configured as skip for {self.file_name}, check manually"
                self.config.output.warning(msg)
                continue
            self._current_repo = repo
            self._each_repo()
        return self._prs_made

    def _each_repo(self: Check) -> None:
        """Run the check for each repository."""
        self.config.output.info(
            f"[{self._current_repo.name}] Checking {self.file_name}...",
        )
        repo_file_path = self._current_repo.work_dir.joinpath(self.file_name)
        repo_content = repo_file_path.read_text()

        if self._compare(current=self._base_file_content, desired=repo_content):
            return

        if self.config.args.dry_run:
            return

        if not self._get_commit_msg():
            return

        self._make_branch()

        shutil.copy(self._base_file_path, repo_file_path)
        msg = f"[{self._current_repo.name}] Updated {self.file_name}."
        self.config.output.info(msg)

        self._make_pr()
