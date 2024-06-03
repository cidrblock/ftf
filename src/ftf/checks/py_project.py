# cspell:ignore btcr, rtcr, btpm, rtpm, btpi, rtpi, norecursedirs,
# cspell:ignore btpmi, rtpmi, btrl, btrlp, rtrl, rtrlp, addopts
"""Check the pyproject.toml file."""

from __future__ import annotations

import shutil

from typing import TYPE_CHECKING, Unpack

import tomlkit

from tomlkit import TOMLDocument, dumps
from tomlkit.items import Array, Table

from ftf.checks.check_base import CheckBase, CheckBaseParams
from ftf.utils import path_to_data_file, subprocess_run, tmp_file


if TYPE_CHECKING:
    from ftf.repo import Repo


class Check(CheckBase):
    """Check the pre-commit yaml file."""

    def __init__(self: Check, **kwargs: Unpack[CheckBaseParams]) -> None:
        """Initialize the class.

        Args:
            **kwargs: The parameters.
        """
        super().__init__(**kwargs)

        self.base_file_content: str

    def run(self: Check) -> bool:
        """Run the check.

        Returns:
            True if PRs were made, False otherwise.
        """
        msg = "The pyproject functionality is rough, please watch diffs closely"
        self.config.output.warning(msg)
        base_file_path = path_to_data_file(self.file_name)
        with base_file_path.open() as f:
            self.base_file_content = f.read()

        for repo in self.repo_list:
            self._current_repo = repo
            self._each_repo(repo=repo)
        return self._prs_made

    def _each_repo(self: Check, repo: Repo) -> None:  # noqa: C901, PLR0915, PLR0912
        """Run the check for each repository.

        Args:
            repo: The repository to check.

        Returns:
            True if PRs were made, False otherwise.
        """
        base_file_data = tomlkit.loads(self.base_file_content)

        repo_file_path = repo.work_dir / self.file_name
        repo_file_data = tomlkit.loads(repo_file_path.read_text())

        # build-system

        # project
        bp = get_table("project", base_file_data)
        rp = get_table("project", repo_file_data)
        rp.update(bp)
        bp.update(rp)

        # tool
        bt = get_table("tool", base_file_data)
        rt = get_table("tool", repo_file_data)

        # tool.black
        if "black" in rt:
            btb = get_table("black", bt)
            rtb = get_table("black", rt)
            rtb.update(btb)
            btb.update(rtb)

        # tool.coverage
        btc = get_table("coverage", bt)
        rtc = get_table("coverage", rt)
        # tool.coverage.report
        btcr = get_table("report", btc)
        rtcr = get_table("report", rtc)
        btcr["fail_under"] = rtcr["fail_under"]
        # tool.coverage.run
        btcr = get_table("run", btc)
        rtcr = get_table("run", rtc)
        btcr["source_pkgs"] = rtcr["source_pkgs"]

        # tool.mypy
        bm = get_table("mypy", bt)
        rm = get_table("mypy", rt)
        if "exclude" in rm:
            bm["exclude"] = rm["exclude"]
        if "overrides" in rm:
            bm["overrides"] = rm["overrides"]

        # tool.pylint
        btp = get_table("pylint", bt)
        rtp = get_table("pylint", rt)
        # tool.pylint.master
        btpm = get_table("master", btp)
        rtpm = get_table("master", rtp)
        if "ignore" in rtpm:
            btpm["ignore"] = get_array("ignore", rtpm)
            btpmi = get_array("ignore", btpm)
            btpmi.sort()

        # tool.pytest
        btp = get_table("pytest", bt)
        rtp = get_table("pytest", rt)
        # tool.pytest.ini_options
        btpi = get_table("ini_options", btp)
        rtpi = get_table("ini_options", rtp)
        if "markers" in rtpi:
            btpi["markers"] = rtpi["markers"]
        if "norecursedirs" in rtpi:
            btpi["norecursedirs"] = rtpi["norecursedirs"]
        if not str(rtpi["addopts"]).startswith(str(btpi["addopts"])):
            msg = "[{repo.name}] Check tool.pytest.init_options.addopts manually."
        btpi["addopts"] = rtpi["addopts"]

        # tool.ruff
        btr = get_table("ruff", bt)
        rtr = get_table("ruff", rt)
        if "exclude" in rtr:
            btr["exclude"] = rtr["exclude"]
        # tool.ruff.lint
        btrl = get_table("lint", btr)
        rtrl = get_table("lint", rtr)
        # tool.ruff.lint.per-file-ignores
        btrlp = get_table("per-file-ignores", btrl)
        rtrlp = get_table("per-file-ignores", rtrl)
        for key, value in rtrlp.items():
            if key not in btrlp:
                btrlp[key] = value

        # tool.setuptools.dynamic
        bts = get_table("setuptools", bt)
        rts = get_table("setuptools", rt)
        bts["dynamic"] = get_table("dynamic", rts)

        # tool.setuptools_scm
        bts = get_table("setuptools_scm", bt)
        rts = get_table("setuptools_scm", rt)
        bts["write_to"] = rts["write_to"]

        desired = dumps(base_file_data)

        new_file = tmp_file()
        new_file.write_text(desired)

        command = f"toml-sort --in-place {new_file}"
        msg = f"[{repo.name}] Sorting {self.file_name}."
        subprocess_run(
            command=command,
            msg=msg,
            output=self.config.output,
            verbose=self.config.args.verbose,
        )
        sorted_desired = new_file.read_text()

        if self._compare(current=repo_file_path.read_text(), desired=sorted_desired):
            return

        if self.config.args.dry_run:
            return

        if not self._get_commit_msg():
            return

        self._make_branch()

        shutil.copy(new_file, repo_file_path)
        msg = f"[{self._current_repo.name}] Updated {self.file_name}."
        self.config.output.info(msg)

        self._make_pr()


def get_table(name: str, obj: TOMLDocument | Table) -> Table:
    """Check the instance of an object.

    Args:
        name: The name of the object.
        obj: The object to check.

    Raises:
        TypeError: If the object is not a container.

    Returns:
        The container
    """
    result = obj.get(name)
    if not isinstance(result, Table):
        err = f"Expected {name} to be a table, got {type(result)}."
        raise TypeError(err)
    return result


def get_array(name: str, obj: Table) -> Array:
    """Check the instance of an object.

    Args:
        name: The name of the object.
        obj: The object to check.

    Raises:
        TypeError: If the object is not a container.

    Returns:
        The container
    """
    result = obj.get(name)
    if not isinstance(result, Array):
        err = f"Expected {name} to be an Array, got {type(result)}."
        raise TypeError(err)
    return result
