# Easy Access Patient Record

A web application for creating, storing and fetching the detailed medical records of a person, using the OpenEHR standards to store the medical data.


# To set up the project for local development

Clone the project

```bash
    git clone https://github.com/Prashast-Bhatnagar/flask.git
```

Activate virtual environment
```bash
    source venv/bin/activate
```
Install dependencies

```bash
    pip install -r requirements.txt
```
set the SqlAlchemy_URI

    set SQLALCHEMY_DATABASE_URI = "postgresql://{postgres_user}:{postgres_password}@{db_host_name}:{postgres_port}/{postgres_db}"

Migrate Database
```bash
    flask db init
    flask db migrate -m "message"
    flask db upgrade
```

Run the Server
```bash
    python ./app.py
```

# Deployment Steps

Create your branch
```bash
    git checkout -b "branch name"
```

Commit onto the branch
```bash
    git add .
    git commit -m "message"
    git push -u origin "branch name"
```
Once the code got merge into the main the CI/CD pipeline will deploy the changes to AWS EBS. 


# Project Overview

## Features

- Patient registration
- Doctor registration
- International Patient Summary (CRUD)
- Prescription (CRUD)
- Roles and Authorization 
- Authentication by JWT Token
- Multiple Prescription Record
- Single Page Application 
- Backend Code Deployed on EBS [Endpoint](http://testflaskapp-env.eba-xdrnw66m.us-east-2.elasticbeanstalk.com) (use with Postman according to API documentation)
- Database deployed on private RDS

## DB Schema

[click here](https://drive.google.com/file/d/1i_mw_l52nYpGqjA9DW-m3xpzpIrk4keM/view)


## AWS Architecture
![awsarch-Page-2 drawio (1)](https://user-images.githubusercontent.com/80159535/150690323-064916be-c21a-485a-986a-c4546a968b32.png)

