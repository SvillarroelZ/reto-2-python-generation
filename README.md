# AWS EC2 Instance Manager CLI

## Overview

This project is a command-line interface (CLI) application for managing AWS EC2 instances. It demonstrates proficiency in Python development, AWS SDK integration, testing methodologies, and secure credential management.

The application enables users to:

- List EC2 instances with filtering capabilities by state
- Create new EC2 instances with custom configurations
- Perform instance lifecycle operations (stop, start, reboot, terminate)
- Handle AWS credentials securely using environment variables
- Manage errors gracefully with comprehensive exception handling

This project validates skills in cloud automation, software engineering best practices, and the ability to build production-ready tools with full test coverage.

## Architecture Diagram

For a detailed architecture diagram with data flow, security, and testing layers, see [Architecture Documentation](docs/architecture.md).

![Architecture Overview](docs/architecture.md)

## Project Structure

```
reto-2-python-generation/
├── src/
│   ├── __init__.py
│   ├── config.py              # AWS credentials and region management
│   ├── aws_client.py          # EC2 client creation with error handling
│   ├── instances_cli.py       # All EC2 instance operations
│   └── main.py                # Application entry point with interactive menu
├── tests/
│   ├── __init__.py
│   ├── test_config.py         # 8 tests for credential management
│   ├── test_aws_client.py     # 5 tests for client creation
│   ├── test_instances_cli.py  # 24 tests for CLI operations
│   └── README.md              # Test documentation and guidelines
├── docs/
│   └── architecture.md        # Architecture diagram and technical documentation
├── .env                       # AWS credentials (not tracked in git)
├── .env.example               # Template for .env file configuration
├── .gitignore                 # Git ignore rules for sensitive and generated files
├── requirements.txt           # Python dependencies (boto3, pytest, etc.)
├── setup.cfg                  # pytest and coverage configuration
└── README.md                  # This file
```

## Core Components

### Configuration Module (src/config.py)

Manages AWS credentials from environment variables with support for temporary session tokens:

- `get_aws_credentials()`: Retrieves AWS access key, secret key, optional session token, and region
- `get_aws_region()`: Returns configured AWS region with fallback to us-east-1
- Validates all required credentials are present before proceeding

### AWS Client Module (src/aws_client.py)

Creates configured boto3 EC2 client with comprehensive error handling:

- `create_ec2_client()`: Initializes boto3 EC2 client with credentials
- Handles NoCredentialsError, BotoCoreError, and general exceptions
- Provides clear error messages for troubleshooting

### Instance CLI Module (src/instances_cli.py)

Implements all EC2 instance operations with user-friendly interfaces:

- `list_instances()`: Display all instances with detailed information
- `filter_instances_by_state()`: Filter and display instances by state (running, stopped, etc.)
- `create_instance()`: Create new EC2 instances with custom AMI, type, and key pair
- `stop_instances()`: Stop running instances
- `start_instances()`: Start stopped instances
- `reboot_instances()`: Reboot running instances
- `terminate_instances()`: Permanently delete instances

All functions include input validation, error handling, and user feedback.

### Main Application (src/main.py)

Interactive menu-driven interface that orchestrates all operations:

- Displays numbered menu options for all available operations
- Handles user input with validation
- Manages KeyboardInterrupt for graceful exit
- Coordinates between CLI functions and AWS client

## Installation and Setup

### Prerequisites

- Python 3.12 or higher
- AWS account with EC2 access permissions
- Valid AWS credentials (access key and secret key)

### Step 1: Clone the Repository

```bash
git clone https://github.com/SvillarroelZ/reto-2-python-generation.git
cd reto-2-python-generation
```

### Step 2: Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure AWS Credentials

For security reasons, AWS credentials are stored in a `.env` file that is never committed to version control.

Create a `.env` file in the project root (you can copy from `.env.example`):

```bash
cp .env.example .env
```

Then edit `.env` with your actual credentials:

```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_SESSION_TOKEN=your_session_token_here  # Optional, for temporary credentials
AWS_DEFAULT_REGION=us-west-2
```

The `.env` file is automatically loaded by python-dotenv and is listed in `.gitignore` to prevent accidental credential exposure.

Note: The application also supports standard environment variables if you prefer not to use a .env file.

## Usage

### Running the Application

```bash
python src/main.py
```

### Interactive Menu

```
======================================================================
                    AWS EC2 Instance Manager
======================================================================
1. List all instances
2. Filter instances by state
3. Create instance
4. Stop instances
5. Start instances
6. Reboot instances
7. Terminate instances
8. Exit
======================================================================
Select an option: 
```

### Example Operations

#### List All Instances

Select option 1 to view all EC2 instances with their ID, name, type, state, and IP addresses.

#### Filter by State

Select option 2 and enter a state (running, stopped, pending, stopping, terminated) to view instances matching that state.

#### Create Instance

Select option 3 and provide:
- AMI ID (e.g., ami-0b8c6b923777519db for Amazon Linux 2023 in us-west-2)
- Instance type (e.g., t2.micro, t3.micro)
- Key pair name for SSH access
- Instance name tag

#### Lifecycle Operations

Select options 4-7 to stop, start, reboot, or terminate instances by entering their instance IDs (comma-separated for multiple instances).

## Testing

### Test Framework

The project uses pytest with comprehensive coverage:

- **pytest**: Test framework for writing and running tests
- **pytest-cov**: Coverage reporting tool
- **pytest-mock**: Mocking AWS API calls for isolated unit tests

### Test Structure

```
tests/
├── test_config.py         # 8 tests for credential management
├── test_aws_client.py     # 5 tests for client creation
└── test_instances_cli.py  # 24 tests for CLI operations
```

### Running Tests

Execute all tests:

```bash
pytest
```

Run tests with coverage report:

```bash
pytest --cov=src --cov-report=term-missing
```

Run specific test file:

```bash
pytest tests/test_config.py
```

### Coverage Results

The test suite achieves 100% coverage on all business logic modules:

```
Name                     Stmts   Miss  Cover
--------------------------------------------
src/__init__.py              0      0   100%
src/aws_client.py           15      0   100%
src/config.py               14      0   100%
src/instances_cli.py       110      0   100%
--------------------------------------------
TOTAL                      139      0   100%
```

Note: `src/main.py` is excluded from coverage reporting as it is an interactive entry point designed for manual execution, not programmatic testing.

### Test Documentation

For detailed information about test cases, mocking strategies, and best practices, see [tests/README.md](tests/README.md).

## Security Considerations

### Credential Management

- **.env File**: AWS credentials are loaded from `.env` file using python-dotenv library
- **Environment Variable Fallback**: Also supports system environment variables if .env file is not present
- **Git Exclusion**: `.env` file is listed in `.gitignore` to prevent accidental commits
- **Session Tokens**: Supports temporary credentials with AWS_SESSION_TOKEN for enhanced security
- **Validation**: All credentials are validated before AWS API calls

### Best Practices Applied

- Never hardcode credentials in source code
- Use least privilege IAM policies for AWS credentials
- Rotate credentials regularly
- Use temporary credentials when possible
- Keep `.env` file permissions restricted (chmod 600)

## Lessons Learned

### Technical Mastery

**AWS SDK Integration**: I gained deep understanding of boto3's EC2 client capabilities, including pagination, filtering with JMESPath queries, and handling various AWS service exceptions. The project reinforced the importance of proper error handling when working with cloud APIs.

**Test-Driven Development**: Implementing comprehensive unit tests with mocking taught me how to isolate components and verify behavior without making actual AWS API calls. Achieving 100% coverage on business logic demonstrated the value of thorough testing for production-ready code.

**Configuration Management**: I learned the critical importance of secure credential handling. Using .env files with python-dotenv for local development provides both security (via .gitignore) and flexibility, while still supporting standard environment variables for production deployments.

### Overcoming Challenges

**Import Resolution**: Initial ModuleNotFoundError issues were resolved by properly structuring the project with `__init__.py` files and using absolute imports. This reinforced the importance of Python package structure.

**Redundancy Elimination**: During code review, I identified and removed the redundant `filter_instances_by_state()` function in main.py, consolidating logic into the instances_cli module. This experience highlighted the value of regular code reviews for maintaining clean codebases.

**Coverage Configuration**: Understanding when to exclude code from coverage (interactive entry points like main.py) versus requiring 100% coverage for business logic was an important distinction that improved test quality.

### Design Decisions

**Separation of Concerns**: Splitting functionality into config, client, CLI operations, and main entry point created a modular architecture that is easy to test, maintain, and extend.

**User Experience**: Implementing input validation with `_prompt_non_empty()` and providing clear error messages ensures users understand what went wrong and how to fix it.

**Professional Standards**: Adopting conventions like English-only code, no emojis in production code, consistent formatting, and comprehensive docstrings demonstrates commitment to maintainable code.

## Improvements

To enhance the robustness and production-readiness of this CLI tool, the following improvements are recommended:

### High Priority

**Logging Implementation**: Replace print statements with Python's logging module for better observability and debugging in production environments. This allows filtering by severity (DEBUG, INFO, WARNING, ERROR) and directing logs to files or monitoring systems.

**Specific Exception Handling**: Instead of catching broad `Exception` types, handle specific boto3 exceptions like `ClientError`, `ParamValidationError`, and check error codes. This enables more precise error messages and recovery strategies.

**State Validation**: Add stricter validation in filter and lifecycle operations. For example, verify that users are not trying to start an already running instance or stop an already stopped instance, providing clear feedback before making API calls.

### Medium Priority

**Configuration File Support**: Extend beyond `.env` to support AWS credential profiles (`~/.aws/credentials`) and instance configuration files for common setups. This would allow users to switch between multiple AWS accounts easily.

**Batch Operations with Confirmation**: For destructive operations (terminate), implement a two-step confirmation process and display instance details before proceeding. This prevents accidental data loss.

**Output Formatting Options**: Add support for JSON and CSV output formats in addition to the current table format. This enables integration with other tools and automation scripts.

### Advanced Features

**Asynchronous Operations**: For listing large numbers of instances or performing bulk operations, implement async/await patterns with `aioboto3` to improve performance and responsiveness.

**Instance Templates**: Allow users to save and reuse instance configurations (AMI, type, security groups, user data) as templates, reducing repetitive input for common deployment patterns.

**Cost Estimation**: Integrate AWS Pricing API to provide estimated costs before creating instances, helping users make informed decisions about instance types and usage.

**Infrastructure as Code Integration**: Export current instance configurations as Terraform or CloudFormation templates, enabling version-controlled infrastructure management and reproducible deployments.

## Dependencies

```
boto3==1.35.93
botocore==1.35.93
jmespath==1.0.1
python-dotenv==1.0.1
pytest==9.0.1
pytest-cov==7.0.0
pytest-mock==3.15.1
```

## Contributing

Contributions are welcome. Please ensure:

1. All tests pass before submitting pull requests
2. New features include corresponding unit tests
3. Code follows existing style conventions (no emojis, English only, consistent formatting)
4. Documentation is updated to reflect changes

## License

This project is provided as-is for educational and demonstration purposes.

## Author

Sebastian Villarroel Z.  
GitHub: [@SvillarroelZ](https://github.com/SvillarroelZ)
