# Testing Guide

This document describes the testing setup and how to run tests for the FastAPI project.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py           # Test fixtures and configuration
├── test_auth.py          # Authentication endpoint tests
├── test_users.py         # User endpoint tests
├── test_accounts.py      # Account endpoint tests
└── test_transactions.py  # Transaction endpoint tests
```

## Running Tests

### Run All Tests

```bash
# Activate virtual environment first
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html
```

### Run Specific Tests

```bash
# Run tests in a specific file
pytest tests/test_auth.py

# Run a specific test class
pytest tests/test_auth.py::TestRegistration

# Run a specific test function
pytest tests/test_auth.py::TestRegistration::test_register_user_success

# Run tests matching a pattern
pytest -k "test_register"
```

### Run Tests with Different Verbosity

```bash
# Quiet mode (only show summary)
pytest -q

# Verbose mode (show each test)
pytest -v

# Very verbose (show more details)
pytest -vv
```

## Test Coverage

### Generate Coverage Report

```bash
# Terminal report
pytest --cov=app --cov-report=term-missing

# HTML report (opens in browser)
pytest --cov=app --cov-report=html
open htmlcov/index.html  # Mac
# or
xdg-open htmlcov/index.html  # Linux
# or
start htmlcov/index.html  # Windows

# XML report (for CI/CD)
pytest --cov=app --cov-report=xml
```

### Coverage Goals

- **Target**: 70%+ overall coverage
- **Critical paths**: 90%+ coverage (auth, transactions)
- **Models**: 80%+ coverage

## Test Categories

### 1. Authentication Tests (`test_auth.py`)

Tests for user registration and login:
- User registration (success, duplicate email/username, invalid data)
- User login (success, wrong password, non-existent user)
- JWT token authentication (valid/invalid tokens)

```bash
pytest tests/test_auth.py -v
```

### 2. User Tests (`test_users.py`)

Tests for user endpoints:
- Get current user
- Get user by ID
- Authorization checks

```bash
pytest tests/test_users.py -v
```

### 3. Account Tests (`test_accounts.py`)

Tests for account management:
- Account creation
- Account retrieval
- Access control (users can only access their own accounts)

```bash
pytest tests/test_accounts.py -v
```

### 4. Transaction Tests (`test_transactions.py`)

Tests for transactions:
- Creating deposits and withdrawals
- Balance updates
- Insufficient funds handling
- Transaction retrieval
- Pagination

```bash
pytest tests/test_transactions.py -v
```

## Test Fixtures

Located in `tests/conftest.py`:

- `client`: FastAPI test client
- `db_session`: Database session for tests
- `test_user_data`: Sample user data
- `test_user`: Created test user
- `auth_token`: JWT authentication token
- `auth_headers`: Authorization headers
- `test_account`: Created test account

### Using Fixtures

```python
def test_example(client, auth_headers, test_account):
    """Example test using fixtures"""
    response = client.get("/api/v1/accounts/me", headers=auth_headers)
    assert response.status_code == 200
```

## CI/CD Pipeline

### GitHub Actions Workflow

The project includes a comprehensive CI/CD pipeline that runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches

#### Pipeline Jobs

1. **Test Job**
   - Sets up MySQL and Redis services
   - Installs dependencies
   - Runs linting (flake8)
   - Executes pytest with coverage
   - Tests API endpoints
   - Uploads coverage to Codecov

2. **Security Scan Job**
   - Runs Bandit security scanner
   - Checks for known vulnerabilities (Safety)

3. **Build Docker Job**
   - Builds Docker image
   - Validates Docker Compose configuration

4. **Notify Job**
   - Reports test results

### Local CI Simulation

Test your code as CI would:

```bash
# Install dev dependencies
pip install flake8 bandit safety

# Run linting
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

# Run security scan
bandit -r app

# Check for vulnerabilities
safety check

# Run tests with coverage
pytest --cov=app --cov-report=xml
```

## Writing New Tests

### Test Template

```python
import pytest

class TestFeatureName:
    """Test description"""

    def test_success_case(self, client, auth_headers):
        """Test successful operation"""
        response = client.post(
            "/api/v1/endpoint/",
            json={"data": "value"},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["field"] == "expected_value"

    def test_failure_case(self, client, auth_headers):
        """Test failure scenario"""
        response = client.post(
            "/api/v1/endpoint/",
            json={"invalid": "data"},
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "error message" in response.json()["detail"].lower()
```

### Best Practices

1. **Use descriptive test names**: `test_user_cannot_withdraw_more_than_balance`
2. **One assertion per test**: Focus on testing one thing
3. **Use fixtures**: Avoid code duplication
4. **Test edge cases**: Empty inputs, large numbers, special characters
5. **Test authorization**: Ensure users can only access their own data
6. **Clean up**: Tests should be independent and not affect each other

## Common Testing Patterns

### Testing Authentication

```python
def test_protected_endpoint(client, auth_headers):
    """Test accessing protected endpoint"""
    response = client.get("/api/v1/protected/", headers=auth_headers)
    assert response.status_code == 200

def test_protected_endpoint_without_auth(client):
    """Test accessing protected endpoint without auth"""
    response = client.get("/api/v1/protected/")
    assert response.status_code == 401
```

### Testing Database Operations

```python
def test_create_and_retrieve(client, auth_headers):
    """Test creating and retrieving resource"""
    # Create
    create_response = client.post(
        "/api/v1/resource/",
        json={"name": "Test"},
        headers=auth_headers
    )
    resource_id = create_response.json()["id"]
    
    # Retrieve
    get_response = client.get(
        f"/api/v1/resource/{resource_id}",
        headers=auth_headers
    )
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test"
```

### Testing Error Handling

```python
def test_invalid_input(client, auth_headers):
    """Test with invalid input"""
    response = client.post(
        "/api/v1/resource/",
        json={"invalid_field": "value"},
        headers=auth_headers
    )
    assert response.status_code == 422  # Validation error
```

## Debugging Tests

### Run with Print Statements

```bash
pytest -s  # Show print statements
```

### Drop into Debugger on Failure

```bash
pytest --pdb  # Drop into pdb on failure
```

### Show Local Variables

```bash
pytest -l  # Show local variables in tracebacks
```

### Run Last Failed Tests

```bash
pytest --lf  # Run only last failed tests
pytest --ff  # Run failed first, then others
```

## Performance Testing

### Measure Test Duration

```bash
pytest --durations=10  # Show 10 slowest tests
```

### Run Tests in Parallel

```bash
pip install pytest-xdist
pytest -n auto  # Use all CPU cores
```

## Test Database

Tests use an in-memory SQLite database for speed and isolation:
- Created fresh for each test
- No need for database cleanup
- Fast execution
- Tests are independent

## Continuous Integration

### GitHub Actions Badge

Add to your README.md:

```markdown
![CI](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI%2FCD%20Pipeline/badge.svg)
```

### Required Checks

Configure branch protection rules to require:
- All tests pass
- Coverage meets threshold (70%)
- Security scan passes
- Code review approval

## Troubleshooting

### Tests Fail Locally but Pass in CI

- Check Python version matches CI
- Verify all dependencies are installed
- Check environment variables

### Tests Pass Locally but Fail in CI

- Database differences (SQLite vs MySQL)
- Timing issues (add appropriate waits)
- Environment-specific configurations

### Coverage is Lower Than Expected

- Check `.coveragerc` configuration
- Ensure all source files are included
- Add tests for untested code paths

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

## Quick Reference

```bash
# Basic commands
pytest                                    # Run all tests
pytest -v                                 # Verbose output
pytest -k "auth"                          # Run auth tests
pytest tests/test_auth.py                 # Specific file
pytest --cov=app                          # With coverage
pytest --cov=app --cov-report=html        # HTML coverage report
pytest -x                                 # Stop on first failure
pytest --lf                               # Run last failed
pytest -s                                 # Show print output
pytest --pdb                              # Debug on failure
pytest --durations=10                     # Show slowest tests

# CI/CD simulation
flake8 app                                # Linting
bandit -r app                             # Security scan
pytest --cov=app --cov-report=xml         # Coverage for CI
```

Happy testing! 🧪
