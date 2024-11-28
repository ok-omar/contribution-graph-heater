from subprocess import run, CalledProcessError
from random import randint
from datetime import datetime, timedelta
from time import sleep
from os import environ, makedirs, chdir 
from sys import exit
import shutil
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
format = logging.Formatter('%(asctime)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(format)
logger.addHandler(console_handler)

def main(requested_days=180, weekdays=7):

    # Generating the repo name with date and time included, in case the script is executed multiple times
    repo_name = f"heated-repository-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Create directory
    make_directory(repo_name)

    # Create the repository
    create_repo(repo_name)    

    # Current date and time
    now = datetime.now()

    # Create a timedelta of 1 day
    delta = timedelta(days=1)

    # Subtract the timedelta from the current date
    for _ in range(requested_days):
        time = (now - delta).date()

        # Check if the current day is withing the days requested by the user
        if time.weekday() < weekdays:

            # Select the color intensity of the cell randomly
            commits_quantity = get_commit_intensity()

            # Generate the commits
            for _ in range(commits_quantity):
                generate_commit(time.day, time.month, time.year)
        # Increase the timedelta by one
        delta += timedelta(days=1)
    
    # Push the commits to github
    run(["git", "push", "-u", "origin", "main"])

def check_dependencies():

    tools = ["git", "gh"]
    missing_tools = []

    # checking for missing tools 
    for tool in tools:
        if not shutil.which(tool):
            missing_tools.append(tool)
    
    if missing_tools:
        logger.info(f"Missing tools: {", ".join(missing_tools)}")
        logger.info(f"Please install the missing tools and ensure they are in your system's PATH.")
        # Stop the script from executing in case the git and / or gh are missing 
        exit(1)
    else:
        print("All tools necessary are installed and accessible!")



def generate_commit(day, month, year):
    # Set commit date
    commit_date = f"{year}-{month:02d}-{day:02d} {randint(10,12)}:{randint(10,59)}:{randint(10,59)}"

    # Set envirement dates to ensure compatibility with Linux, MacOS and Windows
    environ["GIT_AUTHOR_DATE"] = commit_date
    environ["GIT_COMMITTER_DATE"] = commit_date
    
    # Create / open the dummy file to append the date of the commit
    with open("heat.txt", "a") as file:
        file.write(f"Commit date: {commit_date}\n")
    try: 
        run(["git", "add", "heat.txt"] ,check=True)
        run(["git", "commit", "-m", f"Commit for {commit_date}", "heat.txt"], check=True)
    except CalledProcessError as error:
        logger.error(f"Git command failed: {error}")
        exit(2)

def create_repo(repository_name):
    
    # Initialize a git repo
    logger.info("Initializing git...")  
    run(["git", "init"])
    sleep(0.1)
    # Create a private github repo and link it to the git folder
    logger.info(f"Creating repository: {repository_name}")
    run(["gh", "repo", "create", repository_name, "--private", "--source", "--remote=origin"])
    sleep(0.1)
    logger.info(f"Repository {repository_name} created succesfully!")

def make_directory(repository_name):
    # Automatically create the Directory if it doesn't exist and switch to it
    logger.info("Creating directory...")
    makedirs(repository_name, exist_ok=True)  
    chdir(repository_name)  

def get_commit_intensity():
    commit_ranges = [(1, 1), (2, 4), (5, 9), (10, 19), (20, 25)]
    intensity = commit_ranges[randint(0, 4)]
    return randint(intensity[0], intensity[1])


if __name__ == '__main__':
    check_dependencies()
    main()

