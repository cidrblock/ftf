"""Some settings in python format to avoid missing types from a yaml or toml file."""

REPOS: dict[str, dict[str, str]] = {
    "tox-ansible": {
        "origin": "{origin_org}/tox-ansible",
        "upstream": "ansible/tox-ansible",
    },
    "ansible-dev-tools": {
        "origin": "{origin_org}/ansible-dev-tools",
        "upstream": "ansible/ansible-dev-tools",
    },
    "ansible-creator": {
        "origin": "{origin_org}/ansible-creator",
        "upstream": "ansible/ansible-creator",
    },
    "ansible-dev-environment": {
        "origin": "{origin_org}/ansible-dev-environment",
        "upstream": "ansible/ansible-dev-environment",
    },
}

FULL_FILES: dict[str, dict[str, list[str]]] = {
    ".github/CODE_OF_CONDUCT.md": {},
    ".github/CODEOWNERS": {},
    ".github/dependabot.yml": {"skip": ["ansible-dev-tools"]},
    ".github/release-drafter.yml": {},
    ".github/workflows/ack.yml": {},
    ".github/workflows/push.yml": {},
    ".github/workflows/tox.yml": {},
    ".readthedocs.yml": {},
    ".vscode/extensions.json": {},
    ".vscode/settings.json": {},
    "codecov.yml": {},
    "cspell.config.yaml": {},
    "tox.ini": {},
}
