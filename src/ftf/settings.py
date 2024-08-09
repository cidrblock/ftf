"""Some settings in python format to avoid missing types from a yaml or toml file."""

REPOS: dict[str, dict[str, str]] = {
    # "ansible-compat": {
    #     "origin": "{origin_org}/ansible-compat",
    #     "upstream": "ansible/ansible-compat",
    # },
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
    # "ansible-lint": {
    #     "origin": "{origin_org}/ansible-lint",
    #     "upstream": "ansible/ansible-lint",
    # },
    # "ansible-navigator": {
    #     "origin": "{origin_org}/ansible-navigator",
    #     "upstream": "ansible/ansible-navigator",
    # },
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
    ".github/dependabot.yml": {
        "skip": ["ansible-dev-tools", "ansible-compat", "ansible-lint", "ansible-navigator"],
    },
    ".github/release-drafter.yml": {
        "skip": ["ansible-dev-tools", "ansible-compat", "ansible-lint", "ansible-navigator"],
    },
    ".github/workflows/ack.yml": {"skip": ["ansible-compat", "ansible-lint", "ansible-navigator"]},
    ".github/workflows/push.yml": {"skip": ["ansible-compat", "ansible-lint", "ansible-navigator"]},
    ".github/workflows/release.yml": {
        "skip": ["ansible-dev-tools", "ansible-compat", "ansible-lint", "ansible-navigator"],
    },
    ".github/workflows/tox.yml": {
        "skip": [
            "molecule",
            "ansible-dev-tools",
            "ansible-compat",
            "ansible-lint",
            "ansible-navigator",
        ],
    },
    ".readthedocs.yml": {"skip": ["ansible-compat", "ansible-lint", "ansible-navigator"]},
    ".sonarcloud.properties": {"skip": ["ansible-compat", "ansible-lint"]},
    ".vscode/extensions.json": {"skip": ["ansible-compat", "ansible-lint"]},
    ".vscode/settings.json": {"skip": ["ansible-compat", "ansible-lint", "ansible-dev-tools"]},
    ".vscode/tasks.json": {"skip": ["ansible-compat", "ansible-lint"]},
    "codecov.yml": {"skip": ["ansible-compat", "ansible-lint", "ansible-navigator"]},
    "__cspell.config.yaml": {"skip": ["ansible-compat", "ansible-lint", "ansible-navigator"]},
    "tox.ini": {
        "skip": [
            "ansible-dev-tools",
            "molecule",
            "ansible-compat",
            "ansible-lint",
            "ansible-navigator",
        ],
    },
}

SORT_LOWER: list[str] = [
    ".config/dictionary.txt",
]

PRE_COMMIT: dict[str, dict[str, list[str]]] = {
    "ansible-dev-tools": {"skip": ["https://github.com/jazzband/pip-tools"]},
    "molecule": {"skip": ["https://github.com/ansible/ansible-lint"]},
}
