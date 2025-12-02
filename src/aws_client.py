import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError
from .config import get_aws_credentials


def create_ec2_client():
    """
    Create and return a configured EC2 client.
    
    This function retrieves AWS credentials from the configuration
    and creates a boto3 EC2 client with proper error handling.
    
    Returns
    -------
    boto3.client
        Configured EC2 client ready for API calls.
    
    Raises
    ------
    SystemExit
        If credentials are invalid or client creation fails.
        The function prints an appropriate error message before exiting.
    """
    try:
        # Get AWS credentials from environment variables or .env file
        credentials = get_aws_credentials()
        
        # Create EC2 client using boto3 (AWS SDK for Python)
        # **credentials unpacks the dictionary into keyword arguments
        # This is equivalent to: boto3.client("ec2", aws_access_key_id=..., aws_secret_access_key=..., region_name=...)
        ec2_client = boto3.client("ec2", **credentials)
        return ec2_client
    except ValueError as exc:
        # ValueError raised when credentials are missing from environment
        print(f"Configuration error: {exc}")
        raise SystemExit(1)
    except NoCredentialsError:
        # NoCredentialsError is a boto3 exception when AWS credentials cannot be found
        print(
            "AWS credentials not found. "
            "Please run 'aws configure' or set environment variables."
        )
        raise SystemExit(1)
    except BotoCoreError as exc:
        # BotoCoreError handles general boto3/botocore library errors
        print(f"Unexpected error while creating EC2 client: {exc}")
        raise SystemExit(1)
