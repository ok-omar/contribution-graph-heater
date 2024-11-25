from subprocess import run
from random import randint
from datetime import datetime, timedelta
from time import sleep
import logging
from os import environ

def main(requested_days=180, weekdays=7):
    commit_ranges = [(1, 1), (2, 4), (5, 9), (10, 19), (20, 25)]
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
            contribution_intensity = commit_ranges[randint(0, 4)]
            commits_quantity = randint(contribution_intensity[0], contribution_intensity[1])
            # Generate the commits
            for _ in range(commits_quantity):
                generate_commit(time.day, time.month, time.year)
                sleep(0.1)
        # Increase the timedelta by one
        delta += timedelta(days=1)


def generate_commit(day, month, year):
    # Set commit date
    commit_date = f"{year}-{month:02d}-{day:02d} {randint(10,12)}:{randint(10,59)}:{randint(10,59)}"

    # Set envirement dates to ensure compatibility with Linux, MacOS and Windows
    environ["GIT_AUTHOR_DATE"] = commit_date
    environ["GIT_COMMITTER_DATE"] = commit_date
    
    # Create / open the dummy file to append the date of the commit
    with open("heat.txt", "a") as file:
        file.write(f"Commit date: {commit_date}\n")
    run(["git", "add", "heat.txt"])
    run(["git", "commit", "-m", f"Commit for {commit_date}", "heat.txt"])

if __name__ == '__main__':
    main()

