from subprocess import run, CalledProcessError
from random import randint
from datetime import datetime, timedelta
from time import sleep
from os import environ, makedirs, chdir 
from sys import exit
import shutil
import logging
import argparse

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(format)
logger.addHandler(console_handler)

def main(username, repo, requested_days, weekdays):
    
    # Create directory
    make_directory(repo)

    # Create the repository
    create_repo(repo)    

    # Current date and time
    now = datetime.now()

    # Generate the start date
    start_date = now - timedelta(days=requested_days - 1)

    # Subtract the timedelta from the current date
    for day_offset in range(requested_days):
        time = (start_date + timedelta(days=day_offset)).date()
        # Check if the current day is withing the days requested by the user
        if time.weekday() < weekdays:
            # Select the color intensity of the cell randomly
            commits_quantity = get_commit_intensity()
            # Generate the commits
            generate_commit(time.day, time.month, time.year, commits_quantity)

    # Push the commits to GitHub
    try:
        # Check if the remote origin exists
        run(["git", "remote", "get-url", "origin"], check=True, capture_output=True)
        logger.info("Remote 'origin' already exists.")
    except CalledProcessError:
        # If it doesn't exist, add the remote
        try:
            run(["git", "remote", "add", "origin", f"https://github.com/{username}/{repo}.git"], check=True)
            logger.info("Remote 'origin' added successfully.")
        except CalledProcessError as error:
            logger.error(f"Error adding remote: {error}")
            exit(3)

    try:
        run(["git", "push", "--force", "origin", "main"], check=True)
    except CalledProcessError as error:
        logger.error("Error, failed to push the changes to GitHub. Please ensure the repository exists and you have the correct permissions.")
        exit(3)

def check_dependencies():

    tools = ["git", "gh"]
    missing_tools = []

    # checking for missing tools 
    for tool in tools:
        if not shutil.which(tool):
            missing_tools.append(tool)
    
    if missing_tools:
        logger.info(f"Missing tools: {', '.join(missing_tools)}")
        logger.info(f"Please install the missing tools and ensure they are in your system's PATH.")
        # Stop the script from executing in case the git and / or gh are missing 
        exit(1)
    else:
        print("All tools necessary are installed and accessible!")



def generate_commit(day, month, year, quantity):

    # Setting the starting hour of the provided date
    base_time = datetime(year, month, day, hour=9)

    # Generating an array of times starting from the base time 10 minutes apart
    time_slots = [base_time + timedelta(minutes=10 * i) for i in range(quantity)]

    # Iterating over all the time slots
    for commit_time in time_slots:
        # Formatting the date to the format git accepts 
        commit_date = commit_time.strftime("%Y-%m-%d %H:%M:%S")

        # Changing the envirement dates to the formatted date
        environ["GIT_AUTHOR_DATE"] = commit_date
        environ["GIT_COMMITTER_DATE"] = commit_date
        
        # Generating the commit
        with open("heat.txt", "a") as file:
            file.write(f"Commit date: {commit_date}\n")
        try:
            run(["git", "add", "heat.txt"], check=True)
            run(["git", "commit", "-m", f"Commit for {commit_date}"], check=True)
        except CalledProcessError as error:
            logger.error(f"Git command failed: {error}")
            exit(2)     

def create_repo(repository_name):
    try:
        # Initialize a git repo
        logger.info("Initializing git repository...")
        run(["git", "init"], check=True) 

        # Remove any existing remote named 'origin'
        run(["git", "remote", "remove", "origin"], check=False) 
        
        # Create a private GitHub repo and link it to the git folder
        logger.info(f"Creating GitHub repository: {repository_name}")
        result = run(["gh", "repo", "create", repository_name, "--private", "--source=.",  "--remote=origin"], check=True, capture_output=True, text=True)
        # log the output from the command
        logger.info(result.stdout)
        
        logger.info(f"Repository '{repository_name}' created successfully!")
    except CalledProcessError as error:
        logger.error(f"Failed to create repository: {error}")
        logger.error(f"Error details: {error.stderr}")
        exit(3)
    except Exception as unexpected_error:
        logger.error(f"An unexpected error occurred: {unexpected_error}")
        exit(4)


def make_directory(repository_name):
    # Automatically create the Directory if it doesn't exist and switch to it
    logger.info("Creating directory...")
    makedirs(repository_name, exist_ok=True)  
    chdir(repository_name)  

def get_commit_intensity():
    commit_ranges = [(1, 1), (2, 4), (5, 9), (10, 19), (20, 25)]
    intensity = commit_ranges[randint(0, 4)]
    return randint(intensity[0], intensity[1])

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=180, help="Number of days for commits.")
    parser.add_argument("--weekdays", type=int, default=7, help="Number of weekdays to commit.")
    parser.add_argument("--username", type=str, help="Your github username")
    parser.add_argument("--repo", type=str, help="Your github's repository")
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    if not args.username or not args.repo:
        logger.error("Error: Both --username and --repo are required.")
        exit(1)
    
    check_dependencies()
    main(repo=args.repo, username=args.username, requested_days=args.days, weekdays=args.weekdays)
