# Scripts Test Suite

This directory contains comprehensive tests for all modules in the `scripts/` directory of the GradexTool project.

## Test Files

### Core Test Files

- **`test_helpers.py`** - Tests for helper functions (`to_sentence_case`)
- **`test_main.py`** - Tests for the main entry point (`build_data` function)
- **`test_gradexDB.py`** - Tests for all database table classes in `gradexDB.py`

### Module-Specific Test Files

- **`test_revomon.py`** - Tests for revomon data fetching and processing
- **`test_natures.py`** - Tests for nature data and stat modifications
- **`test_abilities.py`** - Tests for ability data and descriptions
- **`test_modules.py`** - Tests for additional modules:
  - Items
  - Moves
  - Type charts
  - Evolutions
  - Capsules
  - Fruitys
  - Medicines
  - Movepools
  - Base types

## Test Configuration

The `conftest.py` file provides common fixtures used across all tests:

### Key Fixtures

- `temp_data_dir` - Temporary directory for test data files
- `temp_db_path` - Temporary database path for testing
- `sample_revomon_data` - Sample revomon data
- `sample_nature_data` - Sample nature data
- `sample_ability_data` - Sample ability data
- `sample_item_data` - Sample item data
- `mock_requests_get/post` - Mocked HTTP requests
- `event_loop` - Event loop for async tests

## Running Tests

### Run All Script Tests

```bash
pytest tests/scripts/
```

### Run Specific Test File

```bash
pytest tests/scripts/test_helpers.py
```

### Run Tests by Marker

```bash
# Run all helpers tests
pytest tests/scripts/ -m helpers

# Run all gradexDB tests
pytest tests/scripts/ -m gradexDB

# Run all revomon script tests
pytest tests/scripts/ -m revomon_script
```

### Run Tests by Class

```bash
# Run specific test class
pytest tests/scripts/test_helpers.py::TestToSentenceCase
```

### Run Tests with Coverage

```bash
pytest tests/scripts/ --cov=scripts --cov-report=html
```

### Run Tests with Detailed Output

```bash
pytest tests/scripts/ -v
```

## Test Coverage

The test suite covers:

### Database Operations

- Table creation and dropping
- Data insertion and retrieval
- Data export to JSON
- Foreign key relationships
- Transaction handling

### Data Processing

- Data normalization
- Name standardization
- Field mapping
- Data validation

### API Interactions

- HTTP request handling
- Response processing
- Error handling
- Timeout handling

### Data Validation

- Structure validation
- Field validation
- Range checking
- Required field verification

### Integration

- Cross-module data consistency
- Data format standardization
- End-to-end workflows
- Error propagation

## Test Organization

### Test Classes

Tests are organized into logical test classes using descriptive names:

```python
@pytest.mark.module_name
class TestFeatureName:
    """Test suite for specific feature."""
```

### Test Methods

Each test method has a descriptive name following the pattern:

```python
def test_specific_behavior_with_condition(self):
    """Test specific behavior under specific condition."""
```

### Markers

Tests use pytest markers for categorization:

- `@pytest.mark.helpers` - Helper function tests
- `@pytest.mark.gradexDB` - Database tests
- `@pytest.mark.main` - Main entry point tests
- `@pytest.mark.revomon_script` - Revomon module tests
- `@pytest.mark.natures_script` - Natures module tests
- `@pytest.mark.abilities_script` - Abilities module tests
- `@pytest.mark.items_script` - Items module tests
- `@pytest.mark.moves_script` - Moves module tests
- `@pytest.mark.type_charts_script` - Type charts module tests
- `@pytest.mark.evolutions_script` - Evolutions module tests
- `@pytest.mark.capsules_script` - Capsules module tests
- `@pytest.mark.fruitys_script` - Fruitys module tests
- `@pytest.mark.medicines_script` - Medicines module tests
- `@pytest.mark.movepools_script` - Movepools module tests
- `@pytest.mark.base_types_script` - Base types module tests
- `@pytest.mark.modules_integration` - Integration tests

## Best Practices

### Async Testing

For async functions, use the `@pytest.mark.asyncio` decorator:

```python
@pytest.mark.asyncio
async def test_async_function(self):
    """Test async function."""
    result = await some_async_function()
    assert result is not None
```

### Mocking External Dependencies

Use unittest.mock to mock external dependencies:

```python
@patch('scripts.module.function_name')
def test_with_mock(self, mock_function):
    """Test with mocked function."""
    mock_function.return_value = sample_data
    result = function_that_uses_mock()
    assert result is not None
```

### Temporary Files

Use the `temp_data_dir` fixture for temporary file operations:

```python
def test_with_temp_file(self, temp_data_dir):
    """Test using temporary directory."""
    test_file = temp_data_dir / "test.json"
    with open(test_file, 'w') as f:
        json.dump(test_data, f)
    assert test_file.exists()
```

## Adding New Tests

When adding new functionality to scripts:

1. Create test methods for each new function
1. Add appropriate markers
1. Use existing fixtures when possible
1. Create new fixtures in `conftest.py` if needed
1. Test both success and error cases
1. Add integration tests for cross-module functionality

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- Fast execution with mocking of external APIs
- No dependencies on external services
- Self-contained with temporary directories
- Clear pass/fail criteria
- Coverage reporting support

## Troubleshooting

### Import Errors

If you encounter import errors, ensure:

1. The `scripts/` directory is in the Python path
1. All dependencies are installed
1. Tests are run from the project root directory

### Async Test Issues

If async tests fail:

1. Ensure pytest-asyncio is installed
1. Check that event loop fixtures are properly used
1. Verify that async functions are properly decorated

### File Path Issues

If file operations fail:

1. Check that `temp_data_dir` fixture is used
1. Ensure proper directory changing with `os.chdir()`
1. Verify that original directory is restored in `finally` blocks

## Contributing

When contributing to the test suite:

1. Follow the existing naming conventions
1. Add docstrings to test classes and methods
1. Use descriptive test names
1. Add markers for categorization
1. Update this README for new test files
1. Ensure all tests are independent and isolated
