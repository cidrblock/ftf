"""Sort and lowercase a file."""

from __future__ import annotations

from typing import Unpack

from ftf.checks.check_base import CheckBase, CheckBaseParams
from ftf.utils import tmp_file


class Check(CheckBase):
    """Sort and lowercase a file."""

    def __init__(self: Check, **kwargs: Unpack[CheckBaseParams]) -> None:
        """Initialize the class.

        Args:
            **kwargs: The parameters.
        """
        super().__init__(**kwargs)

        self.commit_msg = f"Sort, lowercase and remove duplicates in {self.file_name}"

    def run(self: Check) -> bool:
        """Run the check.

        Returns:
            True if PRs were made, False otherwise.
        """
        for repo in self.repo_list:
            self._current_repo = repo
            self._each_repo()
        return self._prs_made

    def _each_repo(self: Check) -> None:
        """Run the check for each repository."""
        repo_file_path = self._current_repo.work_dir / self.file_name

        orig_content = repo_file_path.read_text()
        revised_lines = sorted({line.lower() for line in orig_content.splitlines()})
        revised_content = "\n".join(revised_lines) + "\n"

        if self._compare(current=orig_content, desired=revised_content):
            return

        if self.config.args.dry_run:
            return

        if not self.commit_text_file:
            self.commit_text_file = tmp_file()
            self.commit_text_file.write_text(self.commit_msg)

        self._make_branch()

        repo_file_path.write_text(revised_content)
        msg = f"[{self._current_repo.name}] Updated {self.file_name}."
        self.config.output.info(msg)

        self._make_pr()
