from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import DateField, SubmitField, SelectMultipleField
from todoist_api_python.api import TodoistAPI
from random import choice
from datetime import date, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
# TODO - Add OAuth login
api = TodoistAPI("8f9a6d7e0bb97fc8c47d5ac82c7ab31dbf9fc145")

class TodoistForm(FlaskForm):
    randomTask = SubmitField("Select a Random Task")
    dueDateFilter = DateField(label="Due on or before: ",default=date.today())
    # TODO - add try catch
    projectList = api.get_projects()
    projectChoices = []
    for project in projectList:
        projectChoices.append((project.name, project.name))
    projectFilter = SelectMultipleField(label="From the following project(s): ",choices=projectChoices,coerce=list)
    # TODO - add try catch
    labelList = api.get_labels()
    labelChoices = []
    for label in labelList:
        labelChoices.append((label.name,label.name))
    labelFilter = SelectMultipleField(label="From the following label(s): ",choices=labelChoices,coerce=list)


# ============================================================================
# Route for Shuffler Home Page
# - Page contains a form for selecting Projects, Labels, and Due Dates to filter the task shuffle by
#   - Due date defaults to today
#   - Project and Label lists pulled from Todoist API
# - Upon submit action (clicking randomTask), app takes user selections and constructs filter text to pass to Todoist getTasks API
# - After getting the list of tasks that passed the filters, app selects one option randomly and displays task & help text to user
# ============================================================================
@app.route('/', methods=["GET","POST"])
def index():
    randomTask = ""
    error = ""
    taskFilterText=""
    taskCount = ""
    projectName = ""
    projectColor="charcoal"
    if 'randomTask' in request.form:

        # Filter by Due Date if set
        if 'dueDateFilter' in request.form:
            if request.form['dueDateFilter']:
                dueDate = date.fromisoformat(request.form['dueDateFilter'])
                dueDate = dueDate + timedelta(days=1)
                taskFilterText = 'due before: ' + str(dueDate.month) + "/" + str(dueDate.day)

        # Filter by Project(s) if selected
        if 'projectFilter' in request.form:
            try:
                projectList = request.form.getlist('projectFilter')
            # Show error page if API has an error
            except Exception as error:
                return render_template('error.html',error=error)
            taskFilterText = filter_tasks_by_list(taskFilterText, projectList, "P")

        # Filter by Label(s) if selected
        if 'labelFilter' in request.form:
            try:
                labelList = request.form.getlist('labelFilter')
            # Show error page if API has an error
            except Exception as error:
                return render_template('error.html',error=error)
            taskFilterText = filter_tasks_by_list(taskFilterText, labelList, "L")

        # Pass Filter text to GetTasks Todoist API
        try:
            tasks = api.get_tasks(filter=taskFilterText)
            taskCount = len(tasks)
            if taskCount == 0:
                return render_template('error.html',error="No tasks meet your shuffle criteria, try again.")
            randomTask = choice(tasks)
        # Show error page if API has an error
        except Exception as error:
            return render_template('error.html',error=error)
        # If Random Task is generated, API call to get Project details
        try:
            project = api.get_project(project_id=randomTask.project_id)
            projectName = project.name
            projectColor = project.color
        except Exception as error:
            projectName="Unknown Project"
            projectColor="charcoal"
        # If Random Task is generated, API call to get Section details
        if randomTask.section_id:
            try:
                section = api.get_section(section_id=randomTask.section_id)
                projectName = projectName + " / " + section.name
            except Exception as error:
                pass
    # If Shuffler successful, show index page
    return render_template('index.html',template_form=TodoistForm(),randomTask=randomTask,taskFilterText=taskFilterText,taskCount=taskCount,projectName=projectName,projectColor=projectColor)

# ============================================================================
# Function to create Todoist filter text for the selected list of projects or labels
# Parameters:
#   - prevFilterText = whatever filter text has already been compiled before the function call
#   - selectedList = the list of user selected projects or labels to filter the task shuffle by (or logic)
#   - list type = whether the selected list is a list of projects (P) or labels (L)
# ============================================================================
def filter_tasks_by_list(prevFilterText, selectedList, listType):
   # select right filter text character for the list type
    if listType == "P":
        char = "#"
    elif listType == "L":
        char = "@"
    else:
        # TODO - handle this error w/ error.html page (does it need to be an exception)
        raise ValueError("listType should be P for projects or L for labels")

    # if there are multiple items selected from the list, combine them with OR logic
    if len(selectedList) > 1:
        newFilterText = "("
        for item in selectedList:
            newFilterText = newFilterText + char + item + "|"
        newFilterText = newFilterText.strip("|") + ")"
    # if there is only one item selected from the list, no OR logic or parens needed
    elif len(selectedList) == 1:
        newFilterText = char + selectedList[0]
    else:
        pass

    # if there already is filter text, concatenate this list filter with AND logic
    if prevFilterText != "":
        newFilterText = prevFilterText + "&" + newFilterText
    # otherwise AND logic not needed
    else:
        pass
    return newFilterText
