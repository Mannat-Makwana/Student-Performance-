# Student Performance Dashboard

A responsive Django app for managing students and marks, reviewing class performance, and predicting final scores from internal marks.

## Features

- Student and marks create, list, update, and delete flows with Django ModelForms and validation.
- Paginated student list with live search by student name or roll number.
- CSRF-protected deletion confirmations using a Bootstrap modal.
- Dashboard statistics, subject averages, and server-rendered Matplotlib charts backed by Pandas.
- Linear regression predictions from internal marks to final marks.
- `seed_students` management command for 20 sample students and realistic marks.
- Django admin registrations for both models.

## Requirements and setup

Python 3.10 or newer is recommended. From the project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate
```

The project uses the default local SQLite database (`db.sqlite3`). Bootstrap 5, jQuery, and the Bootstrap JavaScript bundle are loaded from CDNs.

## Run the app

```bash
python manage.py runserver
```

Open <http://127.0.0.1:8000/>. For a populated demo dataset, run:

```bash
python manage.py seed_students
```

The seeder is safe to run more than once; it only adds missing sample students and marks.

## Run tests

```bash
python manage.py test students
```

## How GitHub Copilot was used

GitHub Copilot was used as a coding assistant to scaffold the Django project, implement CRUD and analytics features, and draft automated tests and setup documentation. The generated code and test results were reviewed and validated locally.

