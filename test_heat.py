import pytest
from unittest.mock import patch, mock_open, call
from heat import generate_commit

# Mocking subprocess.run, open, and randint
@patch("heat.run")  # Mock the subprocess.run
@patch("heat.randint", side_effect=[10,20,30])  # Mock randint

def test_generate_commit(mock_randint, mock_run):
    # Create a mock file object
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        # Call the function with specific inputs
        generate_commit(15, 8, 2024)

    # Assert that open() was called with the correct parameters (to append to 'heat.txt')
    mock_file.assert_called_once_with("heat.txt", "a")
    
    # Assert that the file write happens with the expected commit date format
    expected_commit_date = "2024-08-15 10:20:30"
    mock_file.return_value.write.assert_called_once_with(f"Commit date: {expected_commit_date}\n")

    # Assert that subprocess.run was called with the correct git commands
    expected_calls = [
        call(["git", "add", "heat.txt"]),
        call(["git", "commit", "-m", f"Commit for {expected_commit_date}", "heat.txt"])
    ]
    
    mock_run.assert_has_calls(expected_calls, any_order=False)
    assert mock_run.call_count == 2

