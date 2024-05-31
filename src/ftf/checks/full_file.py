"""Check the tox.ini file."""

import difflib
import shutil

from ftf.config import Config
from ftf.repo import Repo
from ftf.utils import (
    ask_yes_no,
    get_commit_msg,
    load_txt_file,
    path_to_data_file,
    render_diff,
)


def run(
    file_name: str,
    file_data: dict[str, list[str]],
    config: Config,
    repo_list: list[Repo],
) -> bool:
    """Run the check.

    Args:
        file_name: The name of the file to check.
        file_data: The data for the file.
        config: The configuration data.
        repo_list: The list of repositories.

    Returns:
        True if PRs were made, False otherwise.
    """
    src_file_name = file_name
    if file_name.startswith("__"):
        file_name = file_name[2:]
    prs_made = False
    base_file_path = path_to_data_file(src_file_name)
    base_content = load_txt_file(base_file_path).splitlines()
    commit_msg = ""
    commit_text_file = None
    skip = file_data.get("skip", [])
    for repo in repo_list:
        if repo.name in skip:
            config.output.warning(
                f"[{repo.name}] Configured as skip for {file_name}, please review manually",
            )
            continue
        config.output.info(f"[{repo.name}] Checking {file_name}...")
        repo_file_path = repo.work_dir.joinpath(file_name)
        repo_content = repo_file_path.read_text().splitlines()
        if base_content == repo_content:
            config.output.info(f"[{repo.name}] {file_name} is correct.")
            continue
        diff = difflib.unified_diff(
            base_content,
            repo_content,
            n=5,
            fromfile="base",
            tofile="repo",
        )
        render_diff(diff)

        if config.args.dry_run:
            answer = ask_yes_no(f"Dry run, continue checking {file_name}?")
            if not answer:
                return False
            continue

        do_update = ask_yes_no(
            f"Do you want to update the {file_name} file in {repo.name}?",
        )
        if not do_update:
            continue
        if not commit_msg:
            commit_msg, commit_text_file = get_commit_msg(
                config=config,
                commit_msg=commit_msg,
            )
        else:
            reuse_commit = ask_yes_no("Do you want to reuse the commit message?")
            if not reuse_commit:
                commit_msg, commit_text_file = get_commit_msg(
                    config=config,
                    commit_msg=commit_msg,
                )

        if commit_text_file is None:
            config.output.error("No commit message provided.")
            return False

        new_branch = f"chore/file_{file_name}_{config.session_id}"
        repo.branch_in_origin(new_branch=new_branch)

        shutil.copy(base_file_path, repo_file_path)
        config.output.info(f"[{repo.name}] Updated {file_name}.")

        repo.stage_file(file_name=file_name)
        repo.commit_file(commit_text_file=commit_text_file)
        repo.push_origin(new_branch=new_branch)
        repo.create_pr(
            file_name=file_name,
            new_branch=new_branch,
            commit_text_file=commit_text_file,
        )
        prs_made = True
        repo.ensure_main()
    return prs_made
