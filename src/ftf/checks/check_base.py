"""The base class with helpers for the checks."""

from __future__ import annotations

import difflib
import subprocess

from typing import TYPE_CHECKING, TypedDict, Unpack

from ftf.output import Color
from ftf.utils import ask_yes_no, tmp_file


if TYPE_CHECKING:
    from pathlib import Path

    from ftf.config import Config
    from ftf.repo import Repo


class CheckBaseParams(TypedDict):
    """The parameters for the CheckBase."""

    file_name: str
    config: Config
    repo_list: list[Repo]


class CheckBase:
    """The base class with helpers for the checks."""

    def __init__(
        self: CheckBase,
        **kwargs: Unpack[CheckBaseParams],
    ) -> None:
        """Initialize the class.

        Args:
            **kwargs: The parameters.
        """
        self.file_name = kwargs["file_name"]
        self.config = kwargs["config"]
        self.repo_list = kwargs["repo_list"]
        self.commit_msg: str = ""
        self.commit_text_file: Path
        self._revision_branch: str
        self._current_repo: Repo
        self._prs_made = False

    def _author_commit_msg(self: CheckBase) -> bool:
        """Allow the user to author a commit message.

        Returns:
            An indication of whether the commit message was updated or empty.
        """
        commit_text_file = tmp_file()
        commit_text_file.write_text(self.commit_msg)
        initial_ts = commit_text_file.stat().st_mtime
        command = f"{self.config.editor} {commit_text_file}"
        subprocess.Popen(args=command, shell=True).wait()
        post_ts = commit_text_file.stat().st_mtime
        if initial_ts == post_ts:
            return False
        with commit_text_file.open(mode="r") as f:
            commit_msg = f.read().strip()
        if commit_msg == "":
            return False
        self.commit_msg = commit_msg

        self.commit_text_file = commit_text_file
        return True

    def _compare(self: CheckBase, current: str, desired: str) -> bool:
        """Compare and diff the current and desired content.

        Args:
            current: The current content.
            desired: The desired content.

        Returns:
            True if the content is different, False otherwise.
        """
        same = current == desired
        if same:
            self.config.output.info(
                f"[{self._current_repo.name}] {self.file_name} no update needed.",
            )
            return True

        self.config.output.warning(
            f"[{self._current_repo.name}] {self.file_name} needs to be updated.",
        )
        diff = difflib.unified_diff(
            current.splitlines(),
            desired.splitlines(),
            n=5,
            fromfile="base",
            tofile="repo",
        )
        for line in diff:
            if line.startswith("---"):
                color = Color.BRIGHT_MAGENTA
            elif line.startswith("+++"):
                color = Color.BRIGHT_CYAN
            elif line.startswith("@@"):
                color = Color.BRIGHT_YELLOW
            elif line.startswith("-"):
                color = Color.BRIGHT_RED
            elif line.startswith("+"):
                color = Color.BRIGHT_GREEN
            else:
                color = Color.GREY
            print(f"{color}{line}{Color.END}")  # noqa: T201
        return False

    def _make_branch(self: CheckBase) -> None:
        """Make a new branch."""
        self._revision_branch = f"chore/file_{self.file_name}_{self.config.session_id}"
        self._current_repo.branch_in_origin(new_branch=self._revision_branch)

    def _get_commit_msg(self: CheckBase) -> bool:
        """Get a commit/PR message from the user.

        Returns:
            True if a PR was made, False otherwise.
        """
        q = f"Do you want to update the {self.file_name} file in {self._current_repo.name}?"
        if not ask_yes_no(q):
            return False

        have_commit_msg = True
        if not self.commit_msg:
            have_commit_msg = self._author_commit_msg()
        else:
            q = "Do you want to reuse the previous commit message?"
            if not ask_yes_no(q):
                have_commit_msg = self._author_commit_msg()

        if have_commit_msg:
            return True

        err = f"[{self._current_repo.name}] No commit message provided or updated, PR skipped."
        self.config.output.error(err)
        return False

    def _make_pr(self: CheckBase) -> None:
        """Make the PR."""
        self._current_repo.stage_file(file_name=self.file_name)
        self._current_repo.commit_file(commit_text_file=self.commit_text_file)
        self._current_repo.push_origin(new_branch=self._revision_branch)
        self._current_repo.create_pr(
            file_name=self.file_name,
            new_branch=self._revision_branch,
            commit_text_file=self.commit_text_file,
        )
        self._current_repo.ensure_main()
        self._prs_made = True
