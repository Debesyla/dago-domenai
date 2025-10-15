# Test Suite for dago-domenai v1.0

Comprehensive test suite covering unit tests, integration tests, and fixtures.

## Test Structure

```
tests/
├── __init__.py              Test package
├── conftest.py              Pytest configuration and shared fixtures
├── pytest.ini               Pytest settings
├── unit/                    Unit tests for individual components
│   ├── test_profiles.py     Profile system tests (84 tests)
│   ├── test_database.py     Database utility tests
│   └── test_schema.py       Result schema tests
├── integration/             Integration tests
│   └── test_orchestrator.py End-to-end workflow tests
└── fixtures/                Test data and mocks
    └── sample_data.py       Sample results, check data, configs
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# Run specific test file
pytest tests/unit/test_profiles.py

# Run specific test class
pytest tests/unit/test_profiles.py::TestProfileDefinitions

# Run specific test
pytest tests/unit/test_profiles.py::TestProfileDefinitions::test_all_profiles_defined
```

### Run Tests by Marker

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Skip database tests
pytest -m "not db"

# Skip slow tests
pytest -m "not slow"

# Skip network tests
pytest -m "not network"
```

## Test Markers

Tests are marked with the following categories:

- `@pytest.mark.unit` - Fast unit tests for individual components
- `@pytest.mark.integration` - Integration tests requiring external services
- `@pytest.mark.db` - Tests requiring database connection
- `@pytest.mark.slow` - Tests taking >5 seconds
- `@pytest.mark.network` - Tests requiring network access

## Test Coverage

### Unit Tests

#### Profile System (`test_profiles.py`) - 84 tests
- ✅ Profile definitions (all 21 profiles)
- ✅ Profile metadata validation
- ✅ Profile category organization
- ✅ Profile parsing and validation
- ✅ Meta profile expansion
- ✅ Dependency resolution
- ✅ Execution plan generation
- ✅ Real-world scenarios
- ✅ Error handling

#### Database (`test_database.py`) - 12 tests
- ✅ Connection management
- ✅ Result persistence
- ✅ Domain flag updates
- ✅ Query functions
- ⏭️ Integration tests (require database)

#### Schema (`test_schema.py`) - 20 tests
- ✅ Result structure creation
- ✅ Metadata updates
- ✅ Check result addition
- ✅ Summary generation
- ✅ JSON serialization
- ✅ Edge cases

### Integration Tests

#### Orchestrator (`test_orchestrator.py`)
- ⏭️ Check determination
- ⏭️ Domain processing
- ⏭️ Profile-based workflows
- ⏭️ Batch processing
- ⏭️ Database integration

**Note:** Integration tests are marked with `@pytest.mark.integration` and require:
- Network access (`@pytest.mark.network`)
- Database connection (`@pytest.mark.db`)
- Longer runtime (`@pytest.mark.slow`)

## Test Configuration

### Environment Variables

```bash
# Test database (for integration tests)
export TEST_DATABASE_URL="postgresql://localhost/dago_test"

# Run integration tests
pytest -m integration
```

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

addopts = 
    --verbose
    --strict-markers
    --tb=short
    --color=yes

markers =
    unit: Unit tests
    integration: Integration tests
    db: Database tests
    slow: Slow tests
    network: Network tests
```

### Coverage Configuration

```ini
[coverage:run]
source = src
omit = */tests/*, */__pycache__/*

[coverage:report]
precision = 2
show_missing = True
fail_under = 70
```

## Writing New Tests

### Unit Test Example

```python
"""tests/unit/test_my_module.py"""
import pytest

class TestMyFeature:
    """Test my feature"""
    
    def test_basic_functionality(self):
        """Test basic functionality"""
        result = my_function("input")
        assert result == "expected"
    
    def test_edge_case(self):
        """Test edge case"""
        with pytest.raises(ValueError):
            my_function(None)
```

### Integration Test Example

```python
"""tests/integration/test_my_workflow.py"""
import pytest

@pytest.mark.integration
@pytest.mark.network
class TestMyWorkflow:
    """Test complete workflow"""
    
    @pytest.mark.slow
    async def test_full_workflow(self, test_config):
        """Test end-to-end workflow"""
        result = await process_workflow()
        assert result["status"] == "success"
```

## Fixtures

### Built-in Fixtures

Available in `conftest.py`:

```python
def test_with_fixtures(
    test_config,                # Test configuration
    sample_domain,              # "example.com"
    sample_active_domain,       # "google.com"
    sample_domain_result,       # Sample result structure
    all_profile_names,          # All 21 profile names
    core_profile_names,         # 4 core profiles
    meta_profile_names,         # 6 meta profiles
):
    # Your test code
    pass
```

### Sample Data

Available in `tests/fixtures/sample_data.py`:

```python
from tests.fixtures.sample_data import (
    SAMPLE_SUCCESS_RESULT,
    SAMPLE_WHOIS_DATA,
    get_sample_result,
    get_sample_check_data,
    TEST_DOMAINS,
    TEST_PROFILE_COMBINATIONS,
)
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-cov
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure you're in the project root
cd /path/to/dago-domenai
pytest
```

**Module Not Found**
```bash
# Install in development mode
pip install -e .
```

**Database Tests Failing**
```bash
# Skip database tests
pytest -m "not db"

# Set test database URL
export TEST_DATABASE_URL="postgresql://localhost/dago_test"
```

**Network Tests Failing**
```bash
# Skip network tests
pytest -m "not network"
```

## Test Statistics

- **Total Tests:** ~116 tests
- **Unit Tests:** ~116 tests
- **Integration Tests:** ~8 tests (skipped by default)
- **Coverage Target:** 70%+

## Next Steps

1. **Run tests locally:**
   ```bash
   pytest tests/unit/ -v
   ```

2. **Check coverage:**
   ```bash
   pytest --cov=src --cov-report=html
   open htmlcov/index.html
   ```

3. **Add new tests:**
   - Create test file in appropriate directory
   - Follow naming convention: `test_*.py`
   - Use markers for test categories

4. **Integration testing:**
   ```bash
   # Setup test database
   createdb dago_test
   psql dago_test -f db/schema.sql
   
   # Run integration tests
   pytest -m integration
   ```

## Support

- Main documentation: `docs/README.md`
- Profile documentation: `docs/PROFILE_QUICK_REFERENCE.md`
- Database setup: `db/README.md`
