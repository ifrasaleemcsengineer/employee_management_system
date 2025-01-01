Steps to Start the Project:

Step 1:
Build and Start the Services
docker-compose up --build

Step 2:
python -m venv env

Step 3:
source env/bin/activate

Step 4:
pip install -r requirements.txt

Step 5:
python manage.py migrate

Step 6: 
python manage.py runserver
