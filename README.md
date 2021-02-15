# Plotly/Dash Dashboard

## Quick start

This is a little bit of a general Python project quickstart

### Setup Environment

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --upgrade pip setuptools
pip install -r requirements.txt
```

### Configuration (`pyproject.toml`)

```toml
[tool.black]
line-length = 110

[tool.pytest.ini_options]
minversion = "6.0"
addopts = '''
  -v
  -rs
  --strict-config
  --strict-markers
  --showlocals
  --black
  --flake8
  --isort
  --mypy

  --junitxml=junit/test-results.xml

  --cov=.
  --cov-branch
  --cov-report xml:cov.xml
  --cov-report html:htmlcov
  --cov-report term
  --cov-fail-under=80
'''

[tool.coverage.run]
branch=true
omit = [
  '**/test_*.py',
  '**/__init__.py',
  '.venv/**/*.py',
  'test/',
]

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 110
import_heading_stdlib='Standard Library'
import_heading_thirdparty='Third Party Libraries'
import_heading_firstparty='Our Libraries'

[tool.mypy]
mypy_path = 'mydash'
check_untyped_defs = true
disallow_any_generics = true
ignore_missing_imports = true
no_implicit_optional = true
show_error_codes = true
strict_equality = true
warn_redundant_casts = true
warn_return_any = true
warn_unreachable = true
warn_unused_configs = true
no_implicit_reexport = true
```

### Test Suite

Run the test suite even without any tests will give us a good start here.

Every source file generates a test for _formatting (`black`), linting (`flake8`), type checking (`mypy`)_

```
pytest
```

### Running the project

```
python3 -m mydash
```
