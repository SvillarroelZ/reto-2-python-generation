# Import EC2 client creation function
from .aws_client import create_ec2_client

# Import all CLI operation functions for instance management
from .instances_cli import (
    list_instances,
    create_instance,
    stop_instance,
    start_instance,
    reboot_instance,
    terminate_instance,
)


def print_menu():
    """Show the main menu of the Cloud Instance Manager."""
    # Display formatted menu with all available operations
    print("\n" + "=" * 50)
    print("Cloud Instance Manager")
    print("=" * 50)
    print("1. List all instances")
    print("2. Create new instance")
    print("3. Stop instance")
    print("4. Start instance")
    print("5. Reboot instance")
    print("6. Terminate instance")
    print("7. Filter instances by state")
    print("0. Exit")
    print("=" * 50)


def handle_filter_by_state(ec2_client):
    """Handle the filter by state option."""
    print("\n" + "=" * 50)
    print("Filter Instances by State")
    print("=" * 50)
    # EC2 Instance Lifecycle States (for Cloud Practitioner exam):
    print("Available states:")
    print("  - pending")      # Instance is launching
    print("  - running")      # Instance is active and billable
    print("  - stopping")     # Instance is shutting down
    print("  - stopped")      # Instance is stopped (no compute charges)
    print("  - terminated")   # Instance is permanently deleted
    
    state = input("\nEnter state to filter by: ").strip().lower()
    
    if not state:
        print("Error: State cannot be empty.")
        return
    
    # Validate state against known EC2 instance states
    valid_states = ["pending", "running", "stopping", "stopped", "terminated"]
    if state not in valid_states:
        print(f"Warning: '{state}' might not be a valid state.")
        print("Proceeding anyway...")
    
    # Call list_instances with state filter
    list_instances(ec2_client, state_filter=state)


def main():
    """Entry point for the CLI application."""
    try:
        # Initialize EC2 client with credentials from environment
        ec2_client = create_ec2_client()
    except SystemExit:
        # Exit gracefully if credential setup fails
        return

    # Main application loop - runs until user selects exit
    while True:
        try:
            print_menu()
            option = input("Select an option: ").strip()

            # Route user choice to appropriate function
            if option == "1":
                list_instances(ec2_client)  # List all instances
            elif option == "2":
                create_instance(ec2_client)  # Launch new instance
            elif option == "3":
                stop_instance(ec2_client)  # Stop running instance
            elif option == "4":
                start_instance(ec2_client)  # Start stopped instance
            elif option == "5":
                reboot_instance(ec2_client)  # Reboot running instance
            elif option == "6":
                terminate_instance(ec2_client)  # Permanently delete instance
            elif option == "7":
                handle_filter_by_state(ec2_client)  # Filter by state
            elif option == "0":
                print("\nExiting Cloud Instance Manager. Goodbye!")
                break  # Exit the while loop
            else:
                print(f"Error: '{option}' is not a valid option.")
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully (user interruption)
            print("\n\nOperation cancelled by user.")
            print("Exiting Cloud Instance Manager. Goodbye!")
            break
        except Exception as exc:
            # Catch any unexpected errors to prevent crashes
            print(f"\nUnexpected error: {exc}")
            print("Please try again or contact support.")


# Only run main() if this file is executed directly (not imported)
if __name__ == "__main__":
    main()
