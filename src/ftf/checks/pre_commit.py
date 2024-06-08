"""Check the pre-commit yaml file."""

from __future__ import annotations

import io

from typing import Unpack

from ansiblelint.yaml_utils import FormattedYAML

from ftf.checks.check_base import CheckBase, CheckBaseParams
from ftf.settings import PRE_COMMIT
from ftf.utils import (
    path_to_data_file,
)


class Check(CheckBase):
    """Check the pre-commit yaml file."""

    def __init__(self: Check, **kwargs: Unpack[CheckBaseParams]) -> None:
        """Initialize the class.

        Args:
            **kwargs: The parameters.
        """
        super().__init__(**kwargs)

        self.base_file_content: str
        self.yaml: FormattedYAML

    def run(self: Check) -> bool:
        """Run the check.

        Returns:
            True if PRs were made, False otherwise.
        """
        self.yaml = FormattedYAML()
        base_file_path = path_to_data_file(self.file_name)
        with base_file_path.open() as f:
            self.base_file_content = f.read()

        for repo in self.repo_list:
            self._current_repo = repo
            self._each_repo()
        return self._prs_made

    def _each_repo(self: Check) -> None:
        """Run the check for each repository.

        Returns:
            True if PRs were made, False otherwise.
        """
        base_data_content = self.yaml.load(self.base_file_content)

        repo_file_path = self._current_repo.work_dir.joinpath(self.file_name)
        with repo_file_path.open() as f:
            repo_file_content = f.read()
        repo_data_content = self.yaml.load(repo_file_content)

        new_repo_list = []
        expected_repos = []
        for base_pc_repo in base_data_content["repos"]:
            expected_repos.append(base_pc_repo["repo"])
            pc_repo_uri = base_pc_repo["repo"]
            found = [
                pc_repo for pc_repo in repo_data_content["repos"] if pc_repo["repo"] == pc_repo_uri
            ]
            if len(found) > 1:
                err = (
                    f"[{self._current_repo.name}] Multiple entries for"
                    " {pc_repo_uri} in {self.file_name}."
                )
                self.config.output.error(err)
                continue

            if not found:
                err = (
                    f"[{self._current_repo.name}] Entry not found for"
                    " {pc_repo_uri} in {self.file_name}."
                )
                self.config.output.error(err)
                found = [base_pc_repo]

            if (
                self._current_repo.name in PRE_COMMIT
                and base_pc_repo["repo"] in PRE_COMMIT[self._current_repo.name]["skip"]
            ):
                new_repo_list.append(found[0])
                continue

            new_base = {
                "repo": pc_repo_uri,
                "rev": found[0]["rev"],
                "hooks": base_pc_repo["hooks"],
            }

            if pc_repo_uri.endswith("mypy.git"):
                uniq = "additional_dependencies"
                new_base["hooks"][0][uniq] = found[0]["hooks"][0][uniq]

            if pc_repo_uri.endswith("pylint.git"):
                uniq = "additional_dependencies"
                new_base["hooks"][0][uniq] = found[0]["hooks"][0][uniq]

            new_repo_list.append(new_base)

        if self._current_repo.name in PRE_COMMIT:
            for skip in PRE_COMMIT[self._current_repo.name]["skip"]:
                if skip in expected_repos:
                    continue
                found = [r for r in repo_data_content["repos"] if r["repo"] == skip]
                if not found:
                    err = (
                        f"[{self._current_repo.name}] Entry not found for"
                        f" {skip} in {self.file_name}."
                    )
                    self.config.output.error(err)
                    continue
                new_repo_list.append(found[0])

        base_data_content["repos"] = new_repo_list

        buf = io.BytesIO()
        self.yaml.dump(data=base_data_content, stream=buf)
        new_content = buf.getvalue().decode()

        if self._compare(current=repo_file_content, desired=new_content):
            return

        if self.config.args.dry_run:
            return

        if not self._get_commit_msg():
            return

        self._make_branch()

        repo_file_path.write_text(new_content)
        self.config.output.debug(
            f"[{self._current_repo.name}] Updated {self.file_name}.",
        )

        self._make_pr()
