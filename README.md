# Real Time Web Analytics Application
## Description
Project was made for the purpose of my Bachelor's thesis in Kozminski University. 
The main idea of the project was to capture users' activity logs on the Source Website and calculate 
the most important Web Analytics metrics and visualize them in real time on the Target Dashboard Application

## Architecture of the Application
![image](https://github.com/rvidxr666/WebAnalyticsApp/blob/master/images/architecture.png?raw=true)

## How to run
1. Activate your venv or create one and run ```pip install -r requirements.txt``` in order to install all the needed dependencies
2. Make sure that you have a **PostgreSQL** database running on port **5432**. It can be running either in the container or locally.
Just make sure the root **"postgres"** user has a **"postgres"** password.
3. Run the **/SourceAppDB/create-tables.py** file by issuing ```python create-tables.py``` command. It will create the Database where
the logs of users will be stored for further processing and visualization.
3. Enter the **/SourceApp** directory and run the ```python app.py``` it will start the Source Flask Application which
is used for generating requests. It represents a simple Flask based Web Application with a few routes deployed.
You can access the app on the following address: http://localhost:5000. NOTE: if you want to use the **Celebrity Recognition** 
ML model you should authenticate to AWS in your cli and make sure that user or IAM Role has all the needed policies to access the AWS Rekognition
4. Enter the **/mysite** directory and run ```python manage.py runserver``` command. It will start the Application with 
dashboards and calculated metrics. You can access the application on **http://localhost:8000**
5. Finally click on routes on the Source Web Application and see how the dashboards and metrics are changing on the Target
Web Application

## Data and Metrics calculated

