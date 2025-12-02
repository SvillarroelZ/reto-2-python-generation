# Testing Suite

This directory contains comprehensive unit tests for the Cloud Instance Manager project.

## Running Tests

Run all tests with coverage:
```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Run specific test file:
```bash
pytest tests/test_config.py
```

Run tests with coverage report:
```bash
pytest --cov=src --cov-report=html
```

## Test Structure

### test_config.py
Tests for configuration module including:
- Credential retrieval from .env file or environment variables (via python-dotenv)
- Session token handling for temporary credentials
- Missing credential error handling
- Default region fallback behavior (us-east-1)
- Empty credential validation

### test_aws_client.py
Tests for AWS client creation including:
- Successful EC2 client creation
- Error handling for missing credentials
- NoCredentialsError handling
- BotoCoreError handling
- Session token support

### test_instances_cli.py
Tests for CLI operations including:
- Input validation and prompts
- Instance listing with and without filters
- Instance creation
- Instance stop/start/reboot operations
- Instance termination with confirmation
- Error handling for AWS operations
- Empty response handling

## Coverage

Current coverage: 100% (excluding entry point)
- src/config.py: 100%
- src/aws_client.py: 100%
- src/instances_cli.py: 100%
- src/main.py: excluded (entry point with interactive loop)

### Why is main.py excluded from coverage?

The `main.py` file is excluded from coverage reports because it serves as the application entry point and contains:

1. Interactive user input loop (while True with input())
2. Menu display and user interaction orchestration
3. No business logic (all logic is in tested modules)

This is a common practice in software testing because:
- Entry points are difficult to unit test due to blocking I/O operations
- The actual logic is already tested at 100% in the CLI functions
- Integration tests would be more appropriate for testing the full flow
- Industry standard excludes interactive entry points from coverage metrics

All business logic, error handling, and AWS operations are fully tested in the respective modules.

## Test Features

- Isolated environment using mocks and patches
- Edge case handling for empty inputs
- Error condition testing
- Case sensitivity validation
- AWS API error simulation
- Client error handling verification
