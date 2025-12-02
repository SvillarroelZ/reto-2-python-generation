import pytest
from unittest.mock import Mock, patch
from botocore.exceptions import BotoCoreError, NoCredentialsError
from src.aws_client import create_ec2_client


class TestCreateEC2Client:
    @patch('src.aws_client.get_aws_credentials')
    @patch('src.aws_client.boto3.client')
    def test_create_ec2_client_success(self, mock_boto_client, mock_get_creds):
        # Arrange
        mock_get_creds.return_value = {
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "region_name": "us-west-2"
        }
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Act
        result = create_ec2_client()
        
        # Assert
        assert result == mock_client
        mock_get_creds.assert_called_once()
        mock_boto_client.assert_called_once_with(
            "ec2",
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            region_name="us-west-2"
        )

    @patch('src.aws_client.get_aws_credentials')
    def test_create_ec2_client_value_error(self, mock_get_creds, capsys):
        # Arrange
        mock_get_creds.side_effect = ValueError("Missing credentials")
        
        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            create_ec2_client()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Configuration error" in captured.out
        assert "Missing credentials" in captured.out

    @patch('src.aws_client.get_aws_credentials')
    @patch('src.aws_client.boto3.client')
    def test_create_ec2_client_no_credentials_error(
        self, mock_boto_client, mock_get_creds, capsys
    ):
        # Arrange
        mock_get_creds.return_value = {
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "region_name": "us-west-2"
        }
        mock_boto_client.side_effect = NoCredentialsError()
        
        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            create_ec2_client()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "AWS credentials not found" in captured.out

    @patch('src.aws_client.get_aws_credentials')
    @patch('src.aws_client.boto3.client')
    def test_create_ec2_client_botocore_error(
        self, mock_boto_client, mock_get_creds, capsys
    ):
        # Arrange
        mock_get_creds.return_value = {
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "region_name": "us-west-2"
        }
        mock_boto_client.side_effect = BotoCoreError()
        
        # Act & Assert
        with pytest.raises(SystemExit) as exc_info:
            create_ec2_client()
        
        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Unexpected error while creating EC2 client" in captured.out

    @patch('src.aws_client.get_aws_credentials')
    @patch('src.aws_client.boto3.client')
    def test_create_ec2_client_with_session_token(
        self, mock_boto_client, mock_get_creds
    ):
        # Arrange
        mock_get_creds.return_value = {
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "aws_session_token": "test_token",
            "region_name": "us-west-2"
        }
        mock_client = Mock()
        mock_boto_client.return_value = mock_client
        
        # Act
        result = create_ec2_client()
        
        # Assert
        assert result == mock_client
        mock_boto_client.assert_called_once_with(
            "ec2",
            aws_access_key_id="test_key",
            aws_secret_access_key="test_secret",
            aws_session_token="test_token",
            region_name="us-west-2"
        )
