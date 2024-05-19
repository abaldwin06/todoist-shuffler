# todoist-shuffler
Get around decision fatigue by randomly choosing which task to work on next

# How to use this
1. Download this program
2. Set up a virtual environment w/ Flask and Python in your program folder
    `python3.12 -m venv ./.env`
3. Install dependencies in requirements.txt in your virtual environment
    `pip install -r requirements.txt`
4. Find your account's Todoist API key and add it into the app.py program (until I set up OAuth feature)
5. Activate your virtual environment
    `source .env/bin/activate`
6. Run the Flask app and open the correct URL in your browser
    `flask run`
7. Set any due date, project or label filters and click the button to find a random task. There is OR logic between the projects if you select multiple, and the same for if you select multiple labels, but there is AND logic in between the due dates, projects, and labels you select.
 
# What I learned
A Flask app to learn how to use python as the back end of a web app. There is no backend database on this app, which will be my next project to exercise what I've learned.

# Known Issues
Reported [issue 135](https://github.com/Doist/todoist-api-python/issues/135) which causes whole app to fail.
Temporary workaround = In Todoist API Models file, comment out lines with `can_assign_tasks` key in the Project object
