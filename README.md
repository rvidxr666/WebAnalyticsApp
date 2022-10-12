# Real Time Web Analytics Application
## Description
Project was made for the purpose of my Bachelor's thesis in Kozminski University. 
The main idea of the project was to capture users' activity logs on the Source Website and calculate 
the most important Web Analytics metrics and visualize them in real time on the Target Dashboard Application during two tracking 
periods (day/week)

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
1. Example of the data that is being placed to the PostgreSQL DB whenever user makes a request on Source Webapp: 
    > ```{user_name: "maksimum232@gmail.com", user_id:0,	name:"Maksim", surname:"Turtsevich", gender:"m", method:"GET", route:"/celebrity", status:"Success", time:"14:48:10", date:"2022-10-11"}```
2. Metrics that are calculated and visualized on the Dashboard Application:
    - **Amount of Users** - amount of unique users that visited website
    - **Amount of new Users** - amount of unique users that accessed the **/register** route
    - **Repeat visitors Ratio** - amount of unique users that accessed the **/login** > 1 time divided by overall amount 
    of unique visitors that accessed the website per tracking periond
    - **Overall Amount of Actions** - count overall amount of interactions with the Source Web Application
    - **Overall amount of sessions** - counts the amount of unique sessions 
    - **Average Amount of Actions per Session** - average amount of actions (clicks) that user performs during the session between
    **/login** and **/logout** routes
    - **Time user spent on the Website** - average session duration
    - **Average Bounce Rate** - percentage of sessions that were shorter than 3 seconds
    - **Average Conversion Rate** - percentage of sessions where user submitted a certain form (made a POST request). On 
    the Source Web Application there are two forms that are activating ML models by using the input from user
    - **Average amount of time to make a conversion** - average which user spends to submit a certain form and activate ML model 
    (make a POST request)
    - **Male/Female ratio** - ratio of male and female visitors
    - **Page views ratio** - visualization of access distribution between routes on the Source Web Application

## Final Result
![demo](https://github.com/rvidxr666/WebAnalyticsApp/blob/master/images/demonstration.gif?raw=true)
    
    
