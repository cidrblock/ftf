"""Some settings in python format to avoid missing types from a yaml or toml file."""

REPOS: dict[str, dict[str, str]] = {
    "ansible-creator": {
        "origin": "{origin_org}/ansible-creator",
        "upstream": "ansible/ansible-creator",
    },
    "ansible-dev-environment": {
        "origin": "{origin_org}/ansible-dev-environment",
        "upstream": "ansible/ansible-dev-environment",
    },
    "ansible-dev-tools": {
        "origin": "{origin_org}/ansible-dev-tools",
        "upstream": "ansible/ansible-dev-tools",
    },
    "molecule": {
        "origin": "{origin_org}/molecule",
        "upstream": "ansible/molecule",
    },
    "pytest-ansible": {
        "origin": "{origin_org}/pytest-ansible",
        "upstream": "ansible/pytest-ansible",
    },
    "tox-ansible": {
        "origin": "{origin_org}/tox-ansible",
        "upstream": "ansible/tox-ansible",
    },
}

FULL_FILES: dict[str, dict[str, list[str]]] = {
    ".github/CODE_OF_CONDUCT.md": {},
    ".github/CODEOWNERS": {},
    ".github/dependabot.yml": {"skip": ["ansible-dev-tools"]},
    ".github/release-drafter.yml": {"skip": ["ansible-dev-tools"]},
    ".github/workflows/ack.yml": {},
    ".github/workflows/push.yml": {},
    ".github/workflows/release.yml": {"skip": ["ansible-dev-tools"]},
    ".github/workflows/tox.yml": {"skip": ["molecule", "ansible-dev-tools"]},
    ".readthedocs.yml": {},
    ".vscode/extensions.json": {},
    ".vscode/settings.json": {"skip": ["ansible-dev-tools"]},
    ".vscode/tasks.json": {},
    "codecov.yml": {},
    "__cspell.config.yaml": {},
    "tox.ini": {"skip": ["ansible-dev-tools", "molecule"]},
}

SORT_LOWER: list[str] = [
    ".config/dictionary.txt",
]

PRE_COMMIT: dict[str, dict[str, list[str]]] = {
    "ansible-dev-tools": {"skip": ["https://github.com/jazzband/pip-tools"]},
    "molecule": {"skip": ["https://github.com/ansible/ansible-lint"]},
}
