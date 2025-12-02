import os  # Access environment variables from the operating system
from dotenv import load_dotenv  # Library to load .env file variables

# Load variables from .env file into environment (if file exists)
load_dotenv()


def get_aws_region():
    """
    Get AWS region from environment variable with default fallback.
    
    Returns
    -------
    str
        The AWS region name, defaults to us-east-1 if not set.
    """
    # AWS Regions are geographic locations where AWS data centers are located
    # Examples: us-east-1 (Virginia), us-west-2 (Oregon), eu-west-1 (Ireland)
    return os.getenv("AWS_DEFAULT_REGION", "us-east-1")


def get_aws_credentials():
    """
    Retrieve AWS credentials from environment variables.
    
    Credentials are loaded from environment variables or a .env file
    using python-dotenv.
    
    Returns
    -------
    dict
        Dictionary containing AWS credentials with keys:
        - aws_access_key_id
        - aws_secret_access_key
        - region_name
        - aws_session_token (optional, for temporary credentials)
    
    Raises
    ------
    ValueError
        If required credentials (access key or secret key) are missing.
    """
    # AWS Access Key ID: Public identifier for your AWS account (like a username)
    access_key = os.getenv("AWS_ACCESS_KEY_ID")
    
    # AWS Secret Access Key: Private key for authentication (like a password)
    secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    
    # Session Token: Temporary credential for enhanced security (optional)
    # Used with temporary credentials from AWS STS (Security Token Service)
    session_token = os.getenv("AWS_SESSION_TOKEN")

    # Both access key and secret key are required for AWS authentication
    if not access_key or not secret_key:
        raise ValueError(
            "AWS credentials not found. "
            "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in your .env file."
        )

    # Build credentials dictionary with required AWS authentication parameters
    # This dict will be unpacked when creating boto3 clients
    credentials = {
        "aws_access_key_id": access_key,
        "aws_secret_access_key": secret_key,
        "region_name": get_aws_region(),
    }
    
    # Add session token only if present (for temporary credentials)
    if session_token:
        credentials["aws_session_token"] = session_token
    
    return credentials
