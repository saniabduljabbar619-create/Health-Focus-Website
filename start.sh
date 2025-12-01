chmod +x start.sh
./venv/Scripts/activate
export FLASK_APP=app.py
export FLASK_ENV=development
flask run