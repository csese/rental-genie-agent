# Rental Genie Tests

This directory contains all tests for the Rental Genie application, organized by type and purpose.

## Test Structure

```
tests/
├── README.md                 # This file
├── run_tests.py             # Test runner script
├── __init__.py              # Package initialization
├── unit/                    # Unit tests (fast, isolated)
│   ├── __init__.py
│   ├── test_extraction_models.py    # Pydantic model tests
│   └── test_extraction_logic.py     # Extraction logic tests
├── integration/             # Integration tests (medium speed)
│   ├── __init__.py
│   ├── test_simple_extraction.py    # LLM extraction tests
│   ├── test_llm_extraction.py       # Comprehensive extraction tests
│   └── test_integration.py          # Full pipeline tests
└── fixtures/                # Test fixtures and sample data
    ├── __init__.py
    └── sample_data.py       # Common test data
```

## Test Types

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and components in isolation
- **Speed**: Fast (milliseconds)
- **Dependencies**: Mocked external dependencies
- **Scope**: Single function/method/class
- **Examples**: Pydantic model validation, confidence filtering logic

### Integration Tests (`tests/integration/`)
- **Purpose**: Test how components work together
- **Speed**: Medium (seconds to minutes)
- **Dependencies**: May use real external services (APIs)
- **Scope**: Component interactions
- **Examples**: LLM extraction pipeline, full message handling

## Running Tests

### Using the Test Runner

```bash
# Run all tests
python tests/run_tests.py

# Run only unit tests
python tests/run_tests.py --type unit

# Run only integration tests
python tests/run_tests.py --type integration

# Run a specific test file
python tests/run_tests.py --test tests/unit/test_extraction_models.py

# List all available tests
python tests/run_tests.py --list
```

### Using Python unittest directly

```bash
# Run unit tests
python -m unittest discover tests/unit

# Run integration tests
python -m unittest discover tests/integration

# Run a specific test file
python -m unittest tests.unit.test_extraction_models
```

### Using pytest (if installed)

```bash
# Run all tests
pytest tests/

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with verbose output
pytest -v tests/
```

## Test Fixtures

The `tests/fixtures/sample_data.py` file contains common test data:

- **SAMPLE_PROPERTY_DATA**: Sample property information
- **SAMPLE_USER_MESSAGES**: Various user input messages
- **EXPECTED_EXTRACTIONS**: Expected extraction results
- **SAMPLE_TENANT_PROFILES**: Sample tenant profiles
- **SAMPLE_CONVERSATION_HISTORY**: Sample conversation data
- **TEST_CONFIG**: Test configuration settings

## Writing New Tests

### Unit Test Guidelines

1. **Test one thing at a time**: Each test should verify one specific behavior
2. **Use descriptive names**: Test method names should clearly describe what's being tested
3. **Mock external dependencies**: Don't make real API calls in unit tests
4. **Test edge cases**: Include tests for error conditions and boundary values
5. **Keep tests fast**: Unit tests should run in milliseconds

Example:
```python
def test_extraction_confidence_filtering(self):
    """Test that low-confidence extractions are filtered out"""
    # Arrange
    mock_result = Mock()
    mock_result.fields = {
        "age": Mock(value="25", confidence=0.9),      # High confidence
        "occupation": Mock(value="engineer", confidence=0.6)  # Low confidence
    }
    
    # Act
    result = process_extraction_result(mock_result)
    
    # Assert
    self.assertIn("age", result)
    self.assertNotIn("occupation", result)
```

### Integration Test Guidelines

1. **Test real workflows**: Test complete user scenarios
2. **Use real dependencies**: May use actual APIs and services
3. **Test data persistence**: Verify data is saved correctly
4. **Test error handling**: Ensure graceful failure handling
5. **Clean up after tests**: Reset state between tests

## Test Configuration

### Environment Variables

For integration tests that require external services:

```bash
# Required for LLM integration tests
export OPENAI_API_KEY="your_api_key_here"

# Optional: Set test-specific environment
export TEST_ENVIRONMENT="development"
export TEST_TIMEOUT="30"
```

### Test Configuration

The `TEST_CONFIG` in `fixtures/sample_data.py` contains:

- **min_confidence_threshold**: 0.7 (minimum confidence for field extraction)
- **max_confidence_threshold**: 1.0 (maximum confidence value)
- **test_session_prefix**: "test_session_" (prefix for test session IDs)
- **timeout_seconds**: 30 (timeout for integration tests)

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Unit Tests
  run: python tests/run_tests.py --type unit

- name: Run Integration Tests
  run: python tests/run_tests.py --type integration
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
```

## Best Practices

1. **Run tests frequently**: Run unit tests before every commit
2. **Keep tests up to date**: Update tests when code changes
3. **Use meaningful assertions**: Assert specific values, not just that something doesn't fail
4. **Test both success and failure cases**: Ensure error handling works
5. **Document test purpose**: Use clear docstrings explaining what each test verifies
6. **Avoid test interdependence**: Tests should not depend on each other
7. **Use appropriate test isolation**: Reset state between tests

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the app directory is in the Python path
2. **API key missing**: Set OPENAI_API_KEY for integration tests
3. **Test discovery issues**: Check that test files follow the naming convention `test_*.py`
4. **Mock issues**: Ensure external dependencies are properly mocked in unit tests

### Debugging Tests

```bash
# Run with verbose output
python tests/run_tests.py --type unit -v

# Run a single test method
python -m unittest tests.unit.test_extraction_models.TestExtractedField.test_valid_extracted_field

# Run with debugger
python -m pdb tests/run_tests.py --type unit
```
