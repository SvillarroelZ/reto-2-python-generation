from botocore.exceptions import ClientError  # AWS API error handling
import jmespath  # JSON query language for filtering AWS API responses


def _prompt_non_empty(prompt_text: str) -> str:
    """
    Prompt the user for input until a non-empty value is provided.
    
    Parameters
    ----------
    prompt_text : str
        The prompt message to display to the user.
    
    Returns
    -------
    str
        The non-empty input value from the user.
    """
    while True:
        value = input(prompt_text).strip()  # Remove leading/trailing whitespace
        if value:
            return value
        # Loop until user provides non-empty input
        print("Error: This value is required. Please try again.")


def _extract_instances_from_response(response: dict) -> list:
    """
    Extract instance information from EC2 API response using JMESPath.
    
    Parameters
    ----------
    response : dict
        The response dictionary from EC2 describe_instances API call.
    
    Returns
    -------
    list
        List of dictionaries containing instance information with keys:
        id, state, type, and az (availability zone).
    """
    # JMESPath expression to extract specific fields from nested EC2 response
    # Navigates: Reservations -> Instances -> individual instance properties
    expression = (
        "Reservations[].Instances[]."
        "{id: InstanceId, state: State.Name, type: InstanceType, "
        "az: Placement.AvailabilityZone}"
    )
    instances = jmespath.search(expression, response)
    return instances if instances else []  # Return empty list if no instances found


def list_instances(ec2_client, state_filter: str | None = None) -> None:
    """
    List EC2 instances and display basic information.
    
    Parameters
    ----------
    ec2_client
        Boto3 EC2 client for making API calls.
    state_filter : str, optional
        Filter instances by state. Valid values include:
        pending, running, stopping, stopped, terminated.
    """
    try:
        # EC2 Filters allow you to query specific instances based on criteria
        # Common filter names: instance-state-name, instance-type, tag:Name, etc.
        filters = []
        if state_filter:
            # Filter by instance state (pending, running, stopping, stopped, terminated)
            filters.append({
                "Name": "instance-state-name",
                "Values": [state_filter]
            })
        
        # Call describe_instances API with or without filters
        response = ec2_client.describe_instances(Filters=filters) if filters else ec2_client.describe_instances()
        instances = _extract_instances_from_response(response)

        if not instances:
            if state_filter:
                print(f"\nNo instances found in state: {state_filter}")
            else:
                print("\nNo instances found in this account or region.")
            return

        print(f"\n{'=' * 70}")
        if state_filter:
            print(f"Instances with state: {state_filter}")
        else:
            print("All Instances")
        print("=" * 70)
        
        for inst in instances:
            print(f"ID: {inst['id']:<20} State: {inst['state']:<12} "
                  f"Type: {inst['type']:<12} AZ: {inst['az']}")
        print("=" * 70)

    except ClientError as exc:
        print(f"\nError: Failed to list instances.")
        print(f"Details: {exc}")


def create_instance(ec2_client) -> None:
    """
    Create a new EC2 instance.
    
    Prompts the user for AMI ID and instance type, then creates
    a single instance with the specified configuration.
    
    Parameters
    ----------
    ec2_client
        Boto3 EC2 client for making API calls.
    """
    print("\n" + "=" * 70)
    print("Create EC2 Instance")
    print("=" * 70)
    print("Note: Use Free Tier eligible options (t2.micro or t3.micro)")
    print()
    
    ami_id = _prompt_non_empty(
        "AMI ID (example for us-west-2 AL2023: ami-0b8c6b923777519db): "
    )
    instance_type = _prompt_non_empty(
        "Instance type (Free Tier: t2.micro or t3.micro): "
    )

    try:
        # run_instances: AWS API call to launch new EC2 instances
        # ImageId: AMI (Amazon Machine Image) defines the OS and software
        # InstanceType: Defines CPU, memory, and other compute resources
        # MinCount/MaxCount: Number of instances to launch (1 = single instance)
        response = ec2_client.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
        )
        # Extract the new instance ID from the API response
        instance_id = response["Instances"][0]["InstanceId"]
        print(f"\nSuccess: Instance created with ID: {instance_id}")
        print("=" * 70)
    except ClientError as exc:
        print(f"\nError: Failed to create instance.")
        print(f"Details: {exc}")
        print("=" * 70)


def stop_instance(ec2_client) -> None:
    """
    Stop a running EC2 instance.
    
    Parameters
    ----------
    ec2_client
        Boto3 EC2 client for making API calls.
    """
    print("\n" + "=" * 70)
    print("Stop EC2 Instance")
    print("=" * 70)
    instance_id = _prompt_non_empty("Instance ID to stop: ")

    try:
        # stop_instances: Stops a running instance (data on EBS volumes persists)
        # Stopped instances do not incur compute charges but storage charges still apply
        # InstanceIds expects a list, even for a single instance
        ec2_client.stop_instances(InstanceIds=[instance_id])
        print(f"\nSuccess: Stop request sent for instance {instance_id}")
        print("=" * 70)
    except ClientError as exc:
        print(f"\nError: Failed to stop instance {instance_id}")
        print(f"Details: {exc}")
        print("=" * 70)


def start_instance(ec2_client) -> None:
    """
    Start a stopped EC2 instance.
    
    Parameters
    ----------
    ec2_client
        Boto3 EC2 client for making API calls.
    """
    print("\n" + "=" * 70)
    print("Start EC2 Instance")
    print("=" * 70)
    instance_id = _prompt_non_empty("Instance ID to start: ")

    try:
        # start_instances: Starts a previously stopped instance
        # The instance retains its instance ID, private IP, and EBS volumes
        # May receive a new public IP address unless using Elastic IP
        ec2_client.start_instances(InstanceIds=[instance_id])
        print(f"\nSuccess: Start request sent for instance {instance_id}")
        print("=" * 70)
    except ClientError as exc:
        print(f"\nError: Failed to start instance {instance_id}")
        print(f"Details: {exc}")
        print("=" * 70)


def reboot_instance(ec2_client) -> None:
    """
    Reboot a running EC2 instance.
    
    Parameters
    ----------
    ec2_client
        Boto3 EC2 client for making API calls.
    """
    print("\n" + "=" * 70)
    print("Reboot EC2 Instance")
    print("=" * 70)
    instance_id = _prompt_non_empty("Instance ID to reboot: ")

    try:
        # reboot_instances: Performs an OS-level reboot of the instance
        # The instance maintains its public and private IP addresses
        # Similar to rebooting your computer - temporary interruption only
        ec2_client.reboot_instances(InstanceIds=[instance_id])
        print(f"\nSuccess: Reboot request sent for instance {instance_id}")
        print("=" * 70)
    except ClientError as exc:
        print(f"\nError: Failed to reboot instance {instance_id}")
        print(f"Details: {exc}")
        print("=" * 70)


def terminate_instance(ec2_client) -> None:
    """
    Terminate an EC2 instance.
    
    Warning: Terminated instances cannot be recovered or restarted.
    
    Parameters
    ----------
    ec2_client
        Boto3 EC2 client for making API calls.
    """
    print("\n" + "=" * 70)
    print("Terminate EC2 Instance")
    print("=" * 70)
    print("WARNING: This action cannot be undone!")
    
    instance_id = _prompt_non_empty("Instance ID to terminate: ")

    confirmation = input(
        f"\nAre you sure you want to terminate {instance_id}?\n"
        "Type 'yes' to confirm: "
    ).strip().lower()

    # User confirmation required because termination is permanent
    if confirmation != "yes":
        print("\nTermination cancelled.")
        print("=" * 70)
        return

    try:
        # terminate_instances: Permanently deletes the instance
        # Cannot be undone - instance and its data are permanently deleted
        # EBS volumes may be retained if configured with DeleteOnTermination=false
        ec2_client.terminate_instances(InstanceIds=[instance_id])
        print(f"\nSuccess: Terminate request sent for instance {instance_id}")
        print("=" * 70)
    except ClientError as exc:
        print(f"\nError: Failed to terminate instance {instance_id}")
        print(f"Details: {exc}")
        print("=" * 70)
