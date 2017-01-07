#!/bin/bash
set -e

python /assethub/manage.py makemigrations
python /assethub/manage.py migrate
python /assethub/create-superuser.py

