import pytest
from unittest.mock import Mock, patch, call
from botocore.exceptions import ClientError
from src.instances_cli import (
    _prompt_non_empty,
    _extract_instances_from_response,
    list_instances,
    create_instance,
    stop_instance,
    start_instance,
    reboot_instance,
    terminate_instance,
)


class TestPromptNonEmpty:
    @patch('builtins.input', return_value="valid_input")
    def test_prompt_non_empty_valid_input(self, mock_input):
        # Act
        result = _prompt_non_empty("Enter value: ")
        
        # Assert
        assert result == "valid_input"
        mock_input.assert_called_once_with("Enter value: ")

    @patch('builtins.input', side_effect=["", "  ", "valid_input"])
    def test_prompt_non_empty_retry_on_empty(self, mock_input, capsys):
        # Act
        result = _prompt_non_empty("Enter value: ")
        
        # Assert
        assert result == "valid_input"
        assert mock_input.call_count == 3
        captured = capsys.readouterr()
        assert "Error: This value is required" in captured.out

    @patch('builtins.input', return_value="  test  ")
    def test_prompt_non_empty_strips_whitespace(self, mock_input):
        # Act
        result = _prompt_non_empty("Enter value: ")
        
        # Assert
        assert result == "test"


class TestExtractInstancesFromResponse:
    def test_extract_instances_success(self):
        # Arrange
        response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-123",
                            "State": {"Name": "running"},
                            "InstanceType": "t2.micro",
                            "Placement": {"AvailabilityZone": "us-west-2a"}
                        },
                        {
                            "InstanceId": "i-456",
                            "State": {"Name": "stopped"},
                            "InstanceType": "t2.small",
                            "Placement": {"AvailabilityZone": "us-west-2b"}
                        }
                    ]
                }
            ]
        }
        
        # Act
        result = _extract_instances_from_response(response)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "i-123"
        assert result[0]["state"] == "running"
        assert result[0]["type"] == "t2.micro"
        assert result[0]["az"] == "us-west-2a"
        assert result[1]["id"] == "i-456"
        assert result[1]["state"] == "stopped"

    def test_extract_instances_empty_reservations(self):
        # Arrange
        response = {"Reservations": []}
        
        # Act
        result = _extract_instances_from_response(response)
        
        # Assert
        assert result == []

    def test_extract_instances_no_reservations_key(self):
        # Arrange
        response = {}
        
        # Act
        result = _extract_instances_from_response(response)
        
        # Assert
        assert result == []

    def test_extract_instances_multiple_reservations(self):
        # Arrange
        response = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-111",
                            "State": {"Name": "running"},
                            "InstanceType": "t2.micro",
                            "Placement": {"AvailabilityZone": "us-west-2a"}
                        }
                    ]
                },
                {
                    "Instances": [
                        {
                            "InstanceId": "i-222",
                            "State": {"Name": "stopped"},
                            "InstanceType": "t3.micro",
                            "Placement": {"AvailabilityZone": "us-west-2b"}
                        }
                    ]
                }
            ]
        }
        
        # Act
        result = _extract_instances_from_response(response)
        
        # Assert
        assert len(result) == 2
        assert result[0]["id"] == "i-111"
        assert result[1]["id"] == "i-222"


class TestListInstances:
    def test_list_instances_success(self, capsys):
        # Arrange
        mock_client = Mock()
        mock_client.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-test123",
                            "State": {"Name": "running"},
                            "InstanceType": "t2.micro",
                            "Placement": {"AvailabilityZone": "us-west-2a"}
                        }
                    ]
                }
            ]
        }
        
        # Act
        list_instances(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "All Instances" in captured.out
        assert "i-test123" in captured.out
        assert "running" in captured.out
        assert "t2.micro" in captured.out
        mock_client.describe_instances.assert_called_once()

    def test_list_instances_with_state_filter(self, capsys):
        # Arrange
        mock_client = Mock()
        mock_client.describe_instances.return_value = {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-running",
                            "State": {"Name": "running"},
                            "InstanceType": "t2.micro",
                            "Placement": {"AvailabilityZone": "us-west-2a"}
                        }
                    ]
                }
            ]
        }
        
        # Act
        list_instances(mock_client, state_filter="running")
        
        # Assert
        captured = capsys.readouterr()
        assert "state: running" in captured.out
        assert "i-running" in captured.out

    def test_list_instances_empty_result(self, capsys):
        # Arrange
        mock_client = Mock()
        mock_client.describe_instances.return_value = {"Reservations": []}
        
        # Act
        list_instances(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "No instances found in this account or region" in captured.out

    def test_list_instances_empty_with_filter(self, capsys):
        # Arrange
        mock_client = Mock()
        mock_client.describe_instances.return_value = {"Reservations": []}
        
        # Act
        list_instances(mock_client, state_filter="stopped")
        
        # Assert
        captured = capsys.readouterr()
        assert "No instances found in state: stopped" in captured.out

    def test_list_instances_client_error(self, capsys):
        # Arrange
        mock_client = Mock()
        error_response = {"Error": {"Code": "UnauthorizedOperation"}}
        mock_client.describe_instances.side_effect = ClientError(
            error_response, "DescribeInstances"
        )
        
        # Act
        list_instances(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Error: Failed to list instances" in captured.out


class TestCreateInstance:
    @patch('src.instances_cli._prompt_non_empty')
    def test_create_instance_success(self, mock_prompt, capsys):
        # Arrange
        mock_prompt.side_effect = ["ami-12345", "t2.micro"]
        mock_client = Mock()
        mock_client.run_instances.return_value = {
            "Instances": [{"InstanceId": "i-newinstance"}]
        }
        
        # Act
        create_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Instance created with ID: i-newinstance" in captured.out
        mock_client.run_instances.assert_called_once_with(
            ImageId="ami-12345",
            InstanceType="t2.micro",
            MinCount=1,
            MaxCount=1
        )

    @patch('src.instances_cli._prompt_non_empty')
    def test_create_instance_client_error(self, mock_prompt, capsys):
        # Arrange
        mock_prompt.side_effect = ["ami-invalid", "t2.micro"]
        mock_client = Mock()
        error_response = {"Error": {"Code": "InvalidAMIID.Malformed"}}
        mock_client.run_instances.side_effect = ClientError(
            error_response, "RunInstances"
        )
        
        # Act
        create_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Error: Failed to create instance" in captured.out


class TestStopInstance:
    @patch('src.instances_cli._prompt_non_empty', return_value="i-test123")
    def test_stop_instance_success(self, mock_prompt, capsys):
        # Arrange
        mock_client = Mock()
        
        # Act
        stop_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Stop request sent for instance i-test123" in captured.out
        mock_client.stop_instances.assert_called_once_with(
            InstanceIds=["i-test123"]
        )

    @patch('src.instances_cli._prompt_non_empty', return_value="i-invalid")
    def test_stop_instance_client_error(self, mock_prompt, capsys):
        # Arrange
        mock_client = Mock()
        error_response = {"Error": {"Code": "InvalidInstanceID.NotFound"}}
        mock_client.stop_instances.side_effect = ClientError(
            error_response, "StopInstances"
        )
        
        # Act
        stop_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Error: Failed to stop instance" in captured.out


class TestStartInstance:
    @patch('src.instances_cli._prompt_non_empty', return_value="i-test456")
    def test_start_instance_success(self, mock_prompt, capsys):
        # Arrange
        mock_client = Mock()
        
        # Act
        start_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Start request sent for instance i-test456" in captured.out
        mock_client.start_instances.assert_called_once_with(
            InstanceIds=["i-test456"]
        )

    @patch('src.instances_cli._prompt_non_empty', return_value="i-invalid")
    def test_start_instance_client_error(self, mock_prompt, capsys):
        # Arrange
        mock_client = Mock()
        error_response = {"Error": {"Code": "InvalidInstanceID.NotFound"}}
        mock_client.start_instances.side_effect = ClientError(
            error_response, "StartInstances"
        )
        
        # Act
        start_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Error: Failed to start instance" in captured.out


class TestRebootInstance:
    @patch('src.instances_cli._prompt_non_empty', return_value="i-test789")
    def test_reboot_instance_success(self, mock_prompt, capsys):
        # Arrange
        mock_client = Mock()
        
        # Act
        reboot_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Reboot request sent for instance i-test789" in captured.out
        mock_client.reboot_instances.assert_called_once_with(
            InstanceIds=["i-test789"]
        )

    @patch('src.instances_cli._prompt_non_empty', return_value="i-invalid")
    def test_reboot_instance_client_error(self, mock_prompt, capsys):
        # Arrange
        mock_client = Mock()
        error_response = {"Error": {"Code": "InvalidInstanceID.NotFound"}}
        mock_client.reboot_instances.side_effect = ClientError(
            error_response, "RebootInstances"
        )
        
        # Act
        reboot_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Error: Failed to reboot instance" in captured.out


class TestTerminateInstance:
    @patch('builtins.input', return_value="yes")
    @patch('src.instances_cli._prompt_non_empty', return_value="i-terminate")
    def test_terminate_instance_confirmed(self, mock_prompt, mock_input, capsys):
        # Arrange
        mock_client = Mock()
        
        # Act
        terminate_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Terminate request sent for instance i-terminate" in captured.out
        mock_client.terminate_instances.assert_called_once_with(
            InstanceIds=["i-terminate"]
        )

    @patch('builtins.input', return_value="no")
    @patch('src.instances_cli._prompt_non_empty', return_value="i-safe")
    def test_terminate_instance_cancelled(self, mock_prompt, mock_input, capsys):
        # Arrange
        mock_client = Mock()
        
        # Act
        terminate_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Termination cancelled" in captured.out
        mock_client.terminate_instances.assert_not_called()

    @patch('builtins.input', return_value="YES")
    @patch('src.instances_cli._prompt_non_empty', return_value="i-terminate2")
    def test_terminate_instance_case_insensitive(
        self, mock_prompt, mock_input, capsys
    ):
        # Arrange
        mock_client = Mock()
        
        # Act
        terminate_instance(mock_client)
        
        # Assert - YES should be converted to lowercase and match "yes"
        captured = capsys.readouterr()
        assert "Terminate request sent for instance i-terminate2" in captured.out
        mock_client.terminate_instances.assert_called_once_with(
            InstanceIds=["i-terminate2"]
        )

    @patch('builtins.input', return_value="yes")
    @patch('src.instances_cli._prompt_non_empty', return_value="i-invalid")
    def test_terminate_instance_client_error(
        self, mock_prompt, mock_input, capsys
    ):
        # Arrange
        mock_client = Mock()
        error_response = {"Error": {"Code": "InvalidInstanceID.NotFound"}}
        mock_client.terminate_instances.side_effect = ClientError(
            error_response, "TerminateInstances"
        )
        
        # Act
        terminate_instance(mock_client)
        
        # Assert
        captured = capsys.readouterr()
        assert "Error: Failed to terminate instance" in captured.out
