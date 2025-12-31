# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the FastAPI project.

## Overview

The CI/CD pipeline is implemented using **GitHub Actions** and runs automatically on:
- Pushes to `main` or `develop` branches
- Pull requests targeting `main` or `develop` branches

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions                        │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐       │
│  │    Test    │  │  Security  │  │   Build    │       │
│  │    Job     │  │    Scan    │  │   Docker   │       │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘       │
│        │               │               │               │
│        └───────────────┴───────────────┘               │
│                        │                                │
│                  ┌─────▼──────┐                        │
│                  │   Notify   │                        │
│                  │    Job     │                        │
│                  └────────────┘                        │
└─────────────────────────────────────────────────────────┘
```

## Pipeline Jobs

### 1. Test Job

**Purpose**: Validate code quality and functionality

**Services**:
- MySQL 8.0 (port 3306)
- Redis 7 (port 6379)

**Steps**:
1. **Checkout code**: Get the latest code from repository
2. **Set up Python 3.11**: Configure Python environment
3. **Install dependencies**: Install from requirements.txt
4. **Run linting** (flake8):
   - Check for syntax errors
   - Enforce code style
5. **Run tests** (pytest):
   - Execute all unit and integration tests
   - Generate coverage report (target: 70%)
6. **Upload coverage**: Send coverage data to Codecov
7. **Test API endpoints**: Verify API is accessible

**Environment Variables**:
```yaml
DATABASE_URL: mysql+pymysql://root:test_password@localhost:3306/test_db
SECRET_KEY: test-secret-key-for-ci
CELERY_BROKER_URL: redis://localhost:6379/0
CELERY_RESULT_BACKEND: redis://localhost:6379/0
```

### 2. Security Scan Job

**Purpose**: Identify security vulnerabilities

**Tools**:
- **Bandit**: Python security linter
- **Safety**: Check for known vulnerabilities in dependencies

**Steps**:
1. **Checkout code**
2. **Set up Python 3.11**
3. **Install security tools**
4. **Run Bandit**: Scan code for security issues
5. **Run Safety**: Check dependencies for known CVEs

### 3. Build Docker Job

**Purpose**: Validate Docker configuration

**Conditions**: Only runs on push to `main` branch

**Steps**:
1. **Checkout code**
2. **Set up Docker Buildx**: Enable advanced Docker features
3. **Build Docker image**: Create application container
4. **Test Docker Compose**: Validate docker-compose.yml

### 4. Notify Job

**Purpose**: Report pipeline results

**Conditions**: Always runs (even if previous jobs fail)

**Steps**:
1. Check overall test results
2. Display success/failure message

## Configuration Files

### GitHub Actions Workflow

Location: `.github/workflows/ci.yml`

Key features:
- Matrix builds (can test multiple Python versions)
- Service containers (MySQL, Redis)
- Caching (speeds up builds)
- Artifact uploads (coverage reports)

### pytest Configuration

Location: `pytest.ini`

```ini
[pytest]
testpaths = tests
addopts = 
    -v
    --cov=app
    --cov-report=term-missing
    --cov-fail-under=70
```

### Coverage Configuration

Location: `.coveragerc`

```ini
[run]
source = app
omit = */tests/*, */migrations/*

[report]
precision = 2
show_missing = True
```

## Setting Up GitHub Actions

### 1. Enable GitHub Actions

1. Go to your GitHub repository
2. Click on "Actions" tab
3. If prompted, enable GitHub Actions for your repository

### 2. Add Workflow File

The workflow file is already in `.github/workflows/ci.yml`

### 3. Configure Branch Protection (Optional)

1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable "Require status checks to pass before merging"
4. Select the CI/CD Pipeline check

### 4. Add Secrets (if needed)

For production deployments, add secrets:

1. Go to Settings → Secrets and variables → Actions
2. Add secrets:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `DEPLOY_TOKEN`
   - etc.

## Running Tests Locally

Before pushing, test locally to catch issues early:

### Quick Test
```bash
make pytest
```

### Full CI Simulation
```bash
# Install dev tools
pip install flake8 bandit safety

# Run all checks
make ci
```

### Detailed Commands
```bash
# Linting
flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

# Security scan
bandit -r app -f json -o bandit-report.json
safety check

# Tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=xml
```

## Test Coverage Requirements

| Component | Target Coverage | Critical? |
|-----------|----------------|-----------|
| Overall | 70% | ✅ Yes |
| Authentication | 90% | ✅ Yes |
| Transactions | 90% | ✅ Yes |
| Models | 80% | ⚠️ Recommended |
| API Routes | 85% | ⚠️ Recommended |

## CI/CD Best Practices

### 1. Fast Feedback
- Tests run in < 5 minutes
- Use caching to speed up builds
- Run quick tests first

### 2. Reliable Tests
- Tests are deterministic
- No flaky tests
- Clean up after tests

### 3. Clear Failures
- Descriptive error messages
- Show relevant logs
- Easy to reproduce locally

### 4. Security First
- Scan dependencies
- Check for code vulnerabilities
- Keep secrets secure

## Troubleshooting CI/CD

### Tests Pass Locally but Fail in CI

**Common causes**:
- Different Python versions
- Missing environment variables
- Database differences (SQLite vs MySQL)
- Timezone issues

**Solution**:
```bash
# Match CI environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

### CI is Slow

**Optimization strategies**:
- Enable dependency caching
- Run tests in parallel
- Use smaller test database
- Skip non-critical tests on PRs

### Security Scan Failures

**False positives**:
- Review Bandit report
- Add `# nosec` comment if safe
- Update .bandit configuration

**Real vulnerabilities**:
- Update dependencies: `pip install --upgrade package`
- Check CVE details
- Apply patches or find alternatives

## GitHub Actions Status Badge

Add to your README.md:

```markdown
![CI/CD Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/workflows/CI%2FCD%20Pipeline/badge.svg)
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your values.

## Extending the Pipeline

### Add More Tests

1. Create new test file in `tests/`
2. Follow naming convention: `test_*.py`
3. Tests run automatically in CI

### Add Integration Tests

```python
# tests/integration/test_full_flow.py
@pytest.mark.integration
def test_complete_user_journey(client):
    """Test complete user flow"""
    # Register → Login → Create Account → Transaction
    pass
```

Update `pytest.ini`:
```ini
markers =
    integration: marks tests as integration tests
```

### Add Deployment Stage

Add to `.github/workflows/ci.yml`:

```yaml
deploy:
  name: Deploy to Production
  runs-on: ubuntu-latest
  needs: [test, security-scan, build-docker]
  if: github.ref == 'refs/heads/main'
  
  steps:
  - name: Deploy to server
    run: |
      # Your deployment commands
      echo "Deploying to production..."
```

### Add Notification

Add Slack/Discord notifications:

```yaml
- name: Notify Slack
  if: always()
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

## Monitoring Pipeline Health

### Metrics to Track

1. **Build Time**: Should be < 5 minutes
2. **Success Rate**: Should be > 95%
3. **Test Coverage**: Should be > 70%
4. **Failure Patterns**: Identify flaky tests

### GitHub Insights

1. Go to "Actions" tab
2. View workflow runs
3. Check success/failure rate
4. Identify bottlenecks

## CI/CD Checklist

Before merging:
- [ ] All tests pass locally
- [ ] Code coverage meets threshold
- [ ] No linting errors
- [ ] No security vulnerabilities
- [ ] CI pipeline passes
- [ ] Documentation updated

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [pytest Documentation](https://docs.pytest.org/)
- [Bandit Documentation](https://bandit.readthedocs.io/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

## Support

For issues with CI/CD:
1. Check workflow logs in GitHub Actions tab
2. Review this documentation
3. Test locally first
4. Check GitHub Actions status page

---

**Pipeline Status**: The latest pipeline run information is available in the GitHub Actions tab of your repository.
