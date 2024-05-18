# IMPORTANT
We have noticed issues with installing dependencies.
With `Flask-Reuploaded` it installs it's files as `Flask-uploads`, which is a different Flask package. So if you are having issues with: `from flask_uploads import UploadSet, configure_uploads, IMAGES`.
MAKE SURE YOU `pip uninstall Flask-Uploads` and then `pip install Flask-Reuploaded`.

# Update dependencies to installation file
`pip freeze > requirements.txt`  

# Quick installation
Install python and run the following command
`pip install -r ./requirements.txt`

Packages need from pip:  
Flask			3.0.2  
Flask-Login		0.6.3  
Flask-SQLAlchemy	3.1.1  
SQLAlchemy		2.0.29  
Flask-Session     0.8.0  
Flask-SocketIO     5.3.6  
Flask-SocketIO     5.3.6  
Flask-Reuploaded   1.4.0  

# Getting started
run the following command
`python ./app.py`
and go to:
http://localhost:5000


# Viewing DB
 1. cmd into ./instance/
 2. 'sqlite3 (name of db).db'
 3. '.tables' for list of tables
 4. 'SELECT * FROM (table name);'
