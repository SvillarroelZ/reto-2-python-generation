import os
import pytest
from unittest.mock import patch
from src.config import get_aws_credentials


class TestGetAWSCredentials:
    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_access_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret_key",
        "AWS_DEFAULT_REGION": "us-west-2"
    }, clear=True)
    def test_get_credentials_success(self):
        # Act
        credentials = get_aws_credentials()
        
        # Assert
        assert credentials["aws_access_key_id"] == "test_access_key"
        assert credentials["aws_secret_access_key"] == "test_secret_key"
        assert credentials["region_name"] == "us-west-2"
        assert "aws_session_token" not in credentials

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_access_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret_key",
        "AWS_SESSION_TOKEN": "test_session_token",
        "AWS_DEFAULT_REGION": "us-west-2"
    }, clear=True)
    def test_get_credentials_with_session_token(self):
        # Act
        credentials = get_aws_credentials()
        
        # Assert
        assert credentials["aws_access_key_id"] == "test_access_key"
        assert credentials["aws_secret_access_key"] == "test_secret_key"
        assert credentials["aws_session_token"] == "test_session_token"
        assert credentials["region_name"] == "us-west-2"

    @patch.dict(os.environ, {
        "AWS_SECRET_ACCESS_KEY": "test_secret_key"
    }, clear=True)
    def test_get_credentials_missing_access_key(self):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            get_aws_credentials()
        
        assert "AWS credentials not found" in str(exc_info.value)

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_access_key"
    }, clear=True)
    def test_get_credentials_missing_secret_key(self):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            get_aws_credentials()
        
        assert "AWS credentials not found" in str(exc_info.value)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_credentials_missing_both(self):
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            get_aws_credentials()
        
        assert "AWS credentials not found" in str(exc_info.value)

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "",
        "AWS_SECRET_ACCESS_KEY": "test_secret_key"
    }, clear=True)
    def test_get_credentials_empty_access_key(self):
        # Act & Assert
        with pytest.raises(ValueError):
            get_aws_credentials()

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_access_key",
        "AWS_SECRET_ACCESS_KEY": ""
    }, clear=True)
    def test_get_credentials_empty_secret_key(self):
        # Act & Assert
        with pytest.raises(ValueError):
            get_aws_credentials()

    @patch.dict(os.environ, {
        "AWS_ACCESS_KEY_ID": "test_access_key",
        "AWS_SECRET_ACCESS_KEY": "test_secret_key"
    }, clear=True)
    def test_default_region_when_not_set(self):
        # Act
        credentials = get_aws_credentials()
        
        # Assert - should use default region
        assert credentials["region_name"] == "us-east-1"
