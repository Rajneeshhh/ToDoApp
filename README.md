To-Do List App

Project Setup

Step 1: Create and Activate Virtual Environment

python -m venv env

source env/bin/activate

Step 2: Install Dependencies

pip install -r requirements.txt

Step 3: Initialize Database

python -m core.db

Step 4: Run the Application

uvicorn app:app --reload

This will start the server, and the application will be available at `http://localhost:8000`.

API Endpoints
The application provides the following API endpoints:

- `GET /tasks/api`: Retrieve a list of all tasks
- `POST /tasks`: Create a new task
- `GET /tasks/api/{task_id}`: Retrieve a task by ID
- `PUT /tasks/api/{task_id}`: Update a task
- `DELETE /tasks/api/{task_id}`: Delete a task

Testing
To run tests, use the following command:
pytest -v tests.test.py

UI routes

- `GET /tasks`: Displays a list of all tasks
- `GET /create-task`: Displays a form to create a new task
- `GET /update-task`: Displays a form to update an existing task
- `GET /delete`: Displays a confirmation page for deleting a task
