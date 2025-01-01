Steps to Start the Project:

Step 1:
Build and Start the Services:
docker-compose up --build

Step 2:
Create Virtual Environment:
python -m venv env

Step 3:
Activate Virtual Environment:
source env/bin/activate

Step 4:
Install dependencies:
pip install -r requirements.txt

Step 5:
Migrate the models:
python manage.py migrate

Step 6: 
Start the server:
python manage.py runserver
