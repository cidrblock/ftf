"""A data structure for a repository."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from ftf.utils import subprocess_run


if TYPE_CHECKING:

    from ftf.config import Config


@dataclass
class Repo:
    """A data structure for a repository."""

    config: Config
    origin: str
    upstream: str
    name: str

    origin_uri: str = ""
    upstream_uti: str = ""
    work_dir: Path = Path()
    origin_owner: str = ""

    def __post_init__(self: Repo) -> None:
        """Post initialization."""
        self.origin_uri = f"git@github.com:{self.origin}.git"
        self.upstream_uri = f"git@github.com{self.upstream}.git"
        self.origin_owner = self.origin.split("/")[0]
        self.work_dir = self.config.tmp_path.joinpath(self.name)

    def clone_origin(self: Repo) -> None:
        """Clone the origin repository."""
        if self.work_dir.exists():
            self.config.output.info(f"[{self.name}] Repository already cloned.")
            return
        msg = f"[{self.name}] Cloning from origin..."
        command = f"gh repo clone {self.origin_uri} -- --depth=1"
        subprocess_run(
            command=command,
            cwd=self.config.tmp_path,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def clone_upstream(self: Repo) -> None:
        """Clone the upstream repository."""
        command = f"gh repo clone {self.upstream_uri} -- --depth=1"
        msg = f"[{self.name}] Cloning from upstream..."
        subprocess_run(
            command=command,
            cwd=self.config.tmp_path,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def fork(self: Repo) -> None:
        """Fork the repository."""
        command = "gh repo fork --remote=False"
        msg = f"[{self.name}] Ensuring fork is available..."
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def ensure_main(self: Repo) -> None:
        """Checkout, main, reset the repository to the upstream/main branch.

        Push to origin main
        """
        msg = f"[{self.name}] Checkout main..."
        command = "git checkout main"
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

        msg = f"[{self.name}] Resetting to upstream/main..."
        command = "git reset --hard upstream/main"
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

        msg = f"[{self.name}] Pull upstream/main..."
        command = "git pull upstream main"
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

        msg = f"[{self.name}] Pushing to origin/main..."
        command = "git push origin main"
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def branch_in_origin(self: Repo, new_branch: str) -> None:
        """Create a new branch in the origin repository.

        Args:
            new_branch: The name of the new branch.
        """
        command = f"git checkout -t -b {new_branch}"
        msg = f"[{self.name}] Creating a new tracking branch {new_branch}..."
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def stage_file(self: Repo, file_name: str) -> None:
        """Stage a file for commit.

        Args:
            file_name: The name of the file to stage.
        """
        command = f"git add {file_name}"
        msg = f"[{self.name}] Staging changes..."
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def commit_file(self: Repo, commit_text_file: Path) -> None:
        """Commit a file.

        Args:
            commit_text_file: The path to the file with the commit message.
        """
        command = f"git commit --file {commit_text_file}"
        msg = f"[{self.name}] Committing changes..."
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def push_origin(self: Repo, new_branch: str) -> None:
        """Push changes to the origin repository.

        Args:
            new_branch: The name of the new branch.
        """
        command = f"git push origin {new_branch}"
        msg = f"[{self.name}] Pushing changes to origin..."
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

    def create_pr(
        self: Repo,
        file_name: str,
        new_branch: str,
        commit_text_file: Path,
    ) -> None:
        """Create a pull request in the origin repository.

        Args:
            file_name: The name of the file to check.
            new_branch: The name of the new branch.
            commit_text_file: The path to the file with the commit message.
        """
        title = f"chore: Update {file_name}"
        command = (
            f'gh pr create --repo {self.upstream} --title "{title}"'
            f" --base main --head {self.origin_owner}:{new_branch} --body-file {commit_text_file}"
        )
        msg = f"[{self.name}] Creating PR..."
        subprocess_run(
            command=command,
            cwd=self.work_dir,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )

        self.config.output.info(f"[{self.name}] PR created.")
