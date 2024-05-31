"""The cli entrypoint for the ftf package."""

import os
import shutil
import sys

from pathlib import Path

from ftf.args import parse_args
from ftf.checks import full_file, pre_commit, py_project, sort_lower
from ftf.config import Config
from ftf.output import Output, TermFeatures
from ftf.repo import Repo
from ftf.settings import FULL_FILES, REPOS, SORT_LOWER
from ftf.utils import (
    ask_yes_no,
    tmp_path,
    xdg_cache_home,
)


def fork_clone_all(config: Config, repo_list: list[Repo]) -> None:
    """Fork all the repositories.

    Args:
        config: The configuration data.
        repo_list: The list of repositories.
    """
    for repo in repo_list:
        if config.args.check_forks:
            shutil.rmtree(repo.work_dir, ignore_errors=True)
            repo.clone_upstream()
            repo.fork()
            shutil.rmtree(repo.work_dir)

        repo.clone_origin()
        repo.work_dir = config.tmp_path.joinpath(repo.name)
        repo.ensure_main()


def reuse_or_new_tmp(new_temp: bool) -> Path:  # noqa: FBT001
    """Return a temporary path.

    Args:
        new_temp: Use a new temporary directory.

    Returns:
        The temporary path.
    """
    tracker = xdg_cache_home() / "tmp_dir.txt"
    if tracker.exists() and not new_temp:
        with tracker.open() as f:
            _tmp_path = Path(f.read().strip())
            if _tmp_path.exists():
                return _tmp_path
    new_tmp = tmp_path()
    with tracker.open("w") as f:
        f.write(str(new_tmp))
    return new_tmp


def generate_repo_list(config: Config) -> list[Repo]:
    """Generate the list of repositories.

    Args:
        config: The configuration data.

    Returns:
        The list of repositories.
    """
    repo_list = []
    for name, data in REPOS.items():
        repo_list.append(
            Repo(
                config=config,
                name=name,
                origin=data["origin"].format(origin_org=config.args.origin_org),
                upstream=data["upstream"],
            ),
        )
    return repo_list


def main() -> None:
    """Load the configuration data file."""
    args = parse_args()
    term_features = TermFeatures(
        color=False if os.environ.get("NO_COLOR") else not args.no_ansi,
        links=not args.no_ansi,
    )
    output = Output(
        log_file=args.log_file,
        log_level=args.log_level,
        log_append=args.log_append,
        term_features=term_features,
        verbosity=args.verbose,
    )

    _tmp_path = reuse_or_new_tmp(new_temp=args.new_temp)
    output.info(f"Using temporary directory {_tmp_path}")
    editor = os.environ.get("EDITOR", "vi")
    config = Config(
        args=args,
        editor=editor,
        output=output,
        tmp_path=_tmp_path,
    )
    repo_list = generate_repo_list(config=config)

    output.info(f"The current session ID is {config.session_id}.")
    proceed = ask_yes_no(
        "Note: You will have to be logged in `gh auth login`"
        " and the origin/main branches will be force updated. Continue?",
    )
    if not proceed:
        output.info("Exiting...")
        return
    try:
        q = "PRs have been made. Do you want to continue with the next file?"
        fork_clone_all(config, repo_list)
        for file_name, file_data in FULL_FILES.items():
            cls_full_file = full_file.Check(
                file_name=file_name,
                config=config,
                repo_list=repo_list,
            )
            changed = cls_full_file.run(file_data=file_data)
            if changed and ask_yes_no(q):
                sys.exit(0)

        for file_name in SORT_LOWER:
            cls_sort_lower = sort_lower.Check(
                file_name=file_name,
                config=config,
                repo_list=repo_list,
            )
            changed = cls_sort_lower.run()
            if changed and ask_yes_no(q):
                sys.exit(0)

        cls_pre_commit = pre_commit.Check(
            file_name=".pre-commit-config.yaml",
            config=config,
            repo_list=repo_list,
        )
        changed = cls_pre_commit.run()
        if changed and ask_yes_no(q):
            sys.exit(0)

        cls_pyproject = py_project.Check(
            file_name="pyproject.toml",
            config=config,
            repo_list=repo_list,
        )
        changed = cls_pyproject.run()
        if changed and ask_yes_no(q):
            sys.exit(0)

    except KeyboardInterrupt:
        print("/n")  # noqa: T201
        output.warning("Dirty exit. Some operations may not have completed.")
        return


if __name__ == "__main__":
    main()
