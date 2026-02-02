monorepo/
├── README.md
├── .gitignore
├── .editorconfig
├── .venv/
├── pyproject.toml           # tooling global (ruff, mypy, pytest)
├── ruff.toml
├── mypy.ini
├── pytest.ini
├── apps/
│   ├── image_scrubber_desktop/
│   │   ├── .venv/
│   │   ├── pyproject.toml
│   │   ├── src/image_scrubber_desktop/
│   │   │   ├── main.py
│   │   │   ├── ui/
│   │   │   │   ├── main_window.py
│   │   │   │   └── styles.qss
│   │   │   ├── services/
│   │   │   │   ├── qt_worker.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── tests/
│   │   │   └── test_smoke_desktop.py
│   │   └── README.md
│   │
│   ├── image_scrubber_cli/
│   │   ├── pyproject.toml
│   │   ├── src/image_scrubber_cli/
│   │   │   ├── main.py
│   │   │   └── __init__.py
│   │   ├── tests/
│   │   │   └── test_cli.py
│   │   └── README.md
│   │
│   ├── image_scrubber_api/
│   │   ├── pyproject.toml
│   │   ├── src/image_scrubber_api/
│   │   │   ├── main.py       # FastAPI app
│   │   │   ├── api/
│   │   │   │   ├── routes_images.py
│   │   │   │   └── __init__.py
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── tests/
│   │   │   └── test_images_endpoint.py
│   │   └── README.md
│   │
│   ├── vuln_scanner_api/      # futuro
│   └── vuln_scanner_worker/   # futuro
│
├── packages/
│   ├── image_scrubber_core/
│   │   ├── pyproject.toml
│   │   ├── src/image_scrubber_core/
│   │   │   ├── metadata/
│   │   │   │   ├── cleaner.py
│   │   │   │   ├── writer.py
│   │   │   │   └── __init__.py
│   │   │   ├── filenames/
│   │   │   │   ├── sanitizer.py
│   │   │   │   └── __init__.py
│   │   │   ├── security/
│   │   │   │   ├── hashing.py
│   │   │   │   └── __init__.py
│   │   │   ├── exceptions.py
│   │   │   └── __init__.py
│   │   └── tests/
│   │       ├── test_cleaner.py
│   │       ├── test_sanitizer.py
│   │       ├── test_hashing.py
│   │       └── __init__.py
│   │
│   ├── core_security/         # futuro, más general
│   ├── integrations/
│   └── observability/
│
├── docs/
│   ├── mkdocs.yml
│   └── docs/
│       ├── index.md
│       ├── image_scrubber/
│       │   ├── overview.md
│       │   ├── cli.md
│       │   ├── desktop.md
│       │   └── api.md
│       └── architecture.md
│
├── infra/
├── ops/
├── scripts/
└── .github/