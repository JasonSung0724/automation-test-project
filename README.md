# Automation Test Project

Professional E2E testing framework built with Pytest + Playwright.

## Features

- **Pydantic Settings** - Type-safe configuration with validation
- **Page Factory Pattern** - Centralized page object management
- **Base Test Class** - Common test utilities and assertions
- **Custom Decorators** - `@retry`, `@step`
- **Structured Logging** - Loguru with file rotation
- **Code Quality** - Ruff linter + pre-commit hooks
- **Makefile** - Simplified command execution

## Project Structure

```
automation-test-project/
├── pyproject.toml          # Modern Python config
├── Makefile                 # Common commands
├── .pre-commit-config.yaml  # Git hooks
├── environment.yml          # Conda environment
└── src/
    ├── config/
    │   └── settings.py      # Pydantic settings
    ├── core/
    │   ├── base_test.py     # Base test class
    │   ├── decorators.py    # Custom decorators
    │   ├── logger.py        # Loguru setup
    │   └── page_factory.py  # Page factory pattern
    ├── pages/
    │   ├── base_page.py     # Base page with utilities
    │   ├── login_page.py
    │   ├── groups_page.py
    │   ├── group_detail_page.py
    │   └── profile_page.py
    ├── tests/
    │   ├── test_auth.py
    │   ├── test_groups.py
    │   ├── test_profile.py
    │   └── test_transactions.py
    ├── utils/
    │   ├── auth_helper.py
    │   └── api_helper.py
    ├── data/
    │   └── test_data.py
    └── conftest.py
```

## Quick Start

### 1. Install Conda Environment

```bash
conda env create -f environment.yml
conda activate automation-test
playwright install chromium
```

### 2. Install Allure (for Test Reports)

**macOS:**

```bash
brew install allure
```

**Windows:**

```powershell
# Option 1: Using Scoop
scoop install allure

# Option 2: Using Chocolatey
choco install allure

# Option 3: Manual installation
# Download from: https://github.com/allure-framework/allure2/releases
# Extract and add bin folder to PATH
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt-add-repository ppa:qameta/allure
sudo apt-get update
sudo apt-get install allure
```

### 3. Or Use Makefile

```bash
make install
```

## Running Tests

```bash
# Using Makefile (recommended)
make test          # Run all tests
make smoke         # Run smoke tests
make headed        # Run with visible browser
make debug         # Run with slow motion + visible browser

# Using pytest directly
cd src
pytest
pytest -m smoke
pytest -m auth
HEADLESS=false pytest
```

## Configuration

Environment variables (`.env` file in `src/`):

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV` | Environment (dev/staging/prod) | `dev` |
| `BASE_URL` | Target URL | `https://dev.mrsplitter.com` |
| `AUTH_TOKEN` | Auth token | (required) |
| `HEADLESS` | Headless mode | `true` |
| `SLOW_MO` | Action delay (ms) | `0` |
| `BROWSER` | Browser type | `chromium` |
| `TIMEOUT` | Default timeout (ms) | `30000` |

## Code Quality

```bash
make lint          # Check code
make format        # Format code

# Setup pre-commit hooks
pre-commit install
```

## Test Reports (Allure)

```bash
# Generate and open report
make report

# Or manually
cd src
allure serve ./allure-results

# Generate static report
allure generate ./allure-results -o ./allure-report --clean
allure open ./allure-report
```

## Usage Examples

### Using Page Factory

```python
from src.core.page_factory import Pages

def test_login(auth_pages: Pages):
    auth_pages.groups.open()
    auth_pages.groups.create_group("Test Group")
    auth_pages.group_detail.add_transaction("100", "Lunch")
```

### Using Base Test

```python
from src.core.base_test import BaseTest

class TestMyFeature(BaseTest):
    def test_something(self, auth_pages):
        auth_pages.groups.open()
        self.take_screenshot("groups_loaded")
        self.assert_url_contains("/groups")
```

### Using Decorators

```python
from src.core.decorators import retry, step

@retry(max_attempts=3, delay=1.0)
def flaky_operation():
    ...

@step("Fill login form")
def fill_form():
    ...
```
