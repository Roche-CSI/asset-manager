# Asset Manager CI/CD Pipeline Documentation

## Overview
This document outlines the continuous integration and continuous deployment (CI/CD) pipeline implemented for the Asset Manager monorepo. The pipeline is designed to automate testing, building, and deployment of Python packages while maintaining code quality and reliability.

## Pipeline Specifications

### Infrastructure
- **Runner Environment**: `ubuntu-latest`
- **Timeout**: 10 minutes
- **Python Version**: 3.10
- **Concurrency Control**: Single run per `workflow-ref-actor` combination

### Trigger Mechanisms
```yaml
on:
  push:
    branches:
      - '**'
    tags:
      - 'contents-v*.*.*'
    paths:
      - 'client/asset-client/asset-contents/**'
```

### Build Concurrency
The pipeline implements a concurrency control mechanism to prevent redundant builds:
```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}-${{ github.actor }}
  cancel-in-progress: true
```

## Quality Controls

### Code Quality
- **Linting**: Enforced using `flake8`
- **Testing**: Automated using `pytest`
- **Coverage**: Test coverage reports generated using `pytest-cov`

### Build Process
1. Code checkout
2. Python environment setup
3. Dependencies installation
4. Code quality checks
5. Test execution
6. Package building
7. Package verification

## Deployment

### Artifacts
- **GitHub Artifacts**: Built packages stored as workflow artifacts
- **PyPI Distribution**: Packages published to PyPI.org

### Package Publishing
Triggered by tags following the format:
```
{package-name}-v{major}.{minor}.{patch}
```

## Usage

### Local Development
```bash
# Install development dependencies
python -m pip install -e .

# Run tests locally
pytest

# Run linting
flake8
```

### Triggering Deployments
```bash
git tag contents-v1.0.0
git push origin contents-v1.0.0
```

## Directory Structure
```
.
├── .github
│   └── workflows
│       └── ci-asset-contents.yml
├── client
│   └── asset-contents
│       ├── asset_contents
│       └── pyproject.toml
```

## Environment Variables
| Variable | Description | Required |
|----------|-------------|----------|
| PYTHON_VERSION | Python version for build | Yes |
| TWINE_USERNAME | PyPI username | For deployment |
| TWINE_PASSWORD | PyPI token | For deployment |

## Security Considerations
- PyPI credentials stored as GitHub secrets
- Package verification before publishing
- Automated security scanning of dependencies

## Limitations
- Currently supports only Python 3.10
- Limited to Ubuntu runners
- 10-minute timeout constraint
