"""Sort and lowercase a file."""

from ftf.config import Config
from ftf.repo import Repo
from ftf.utils import ask_yes_no, tmp_file


def run(config: Config, repo_list: list[Repo], file_name: str) -> None:
    """Run the check.

    Args:
        config: The configuration data.
        repo_list: The list of repositories.
        file_name: The file to check.
    """
    commit_msg = f"Sort, lowercase and remove and duplicates in {file_name}"
    commit_text_file = None

    for repo in repo_list:
        with (repo.work_dir / file_name).open(mode="r") as f:
            orig_lines = f.readlines()
        revised_lines = sorted({line.lower() for line in orig_lines})
        if revised_lines == orig_lines:
            config.output.info(
                f"[{repo.name}] The {file_name} is sorted and lowercased.",
            )
            continue
        config.output.warning(
            f"[{repo.name}] The {file_name} is not sorted and lowercased.",
        )
        if config.args.dry_run:
            continue

        go = ask_yes_no(f"Do you want to remediate {file_name}?")
        if not go:
            continue

        commit_text_file = tmp_file()
        with commit_text_file.open(mode="w") as f:
            f.write(commit_msg)

        new_branch = f"chore/file_{file_name}_{config.session_id}"
        repo.branch_in_origin(new_branch=new_branch)

        with (repo.work_dir / file_name).open(mode="w") as f:
            f.writelines(revised_lines)
        config.output.info(f"[{repo.name}] Updated {file_name}.")

        repo.stage_file(file_name=file_name)
        repo.commit_file(commit_text_file=commit_text_file)
        repo.push_origin(new_branch=new_branch)
        repo.create_pr(
            file_name=file_name,
            new_branch=new_branch,
            commit_text_file=commit_text_file,
        )
        repo.ensure_main()
