# eHealth Interview

# Introduction

This project was started on ***16/12/2023 4:00PM***, and submitted on ***17/12/2023 2:00PM***.


The project is written in Python using the Django web framework and launched in Docker. This simplifies the project’s initial deployment.


# Features

- Sign up page for users- A user can either sign-up as a health worker or as a normal patient

- A table that displays all users and their relevant medical records (only users registered as medical practitioners can view this page).

- A page were normal users/patients can fill in their medical information with relevant questions depending on the developer's discretion.

- A page that displays the statistical details of the medical records gotten from the users (all users can view this page). e.g. multi charts that shows the count for users with Ebola.

- A drop-down filter to show users with specified medical records of your own discretion e.g. show only users with malaria.

- Users should be able to search for any health worker and be able to book appointment with him or her and the health worker should be able to receive a mail about the appointment with information about who wants to book the appointment, date and time.

- A health worker should be able to either accept or reject an appointment through his dashboard.

- Total number of appointments booked and rejected for a particular month should be visible to a health worker when he/she logs into his dashboard.


Quick Start Guide
=========

Step 1 - Set up Docker
------------------------

Install Docker and Docker-Compose

1. Docker installation instructions: https://docs.docker.com/engine/installation/linux/docker-ce/ubuntu/#install-docker-ce
2. Docker-compose installation instructions: https://docs.docker.com/compose/install/#alternative-install-options

Then create a Docker image. To do this, enter the command:
```
    $ make build
```

Step 2 - set up a log folder and file
--------------------------
- create a log file in the root project if this has not been created - "cron/cron.log"
- ensure you set the path in the log settings tot he cron log file
```
    'handlers': {
        'cron_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR/'cron/cron.log',  # Replace with the desired path to your log file
        },
    },

```

Step 3 - change the celery settings
--------------------------
Go to the ```backend/settings.py``` and change as seen:
```
    CELERY_BROKER_URL = "redis://rd-sqlite:6379"
    CELERY_RESULT_BACKEND = "redis://rd-sqlite:6379"
```

Step 4 - run the app
-------------------------
launch the container
```
    $ docker-compose up --build
```

Step 5 - go to the localhost port on your browser
-------------------------
```localport:8000```


# Another way to run the app, through virtual env

1. Create a virtual environment
```
    $ virtualenv venv -p /usr/bin/python3 --no-site-package
```
2. Activate virtual environment
```
    $ source venv/bin/activate
```
3. Establish requirements
```
    $ pip install -r requirements.txt
```
4. Create a log file in a directory in the root project
5. Run migrations
```
    $ python manage.py makemigrations
```
6. Run migrate
```
    $ python manage.py migrate
```
7. Create superuser
```
    $ python manage.py createsuperuser
```
8. Run server
```
    $ python manage.py runserver
```
