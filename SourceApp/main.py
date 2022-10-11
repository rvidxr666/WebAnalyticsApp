from flask import (Flask, render_template, request, url_for, redirect, flash, session)
from flask_sqlalchemy import SQLAlchemy
from typing import Callable
import pickle
import boto3
from datetime import datetime, timezone, timedelta
import os
from sklearn.linear_model import LinearRegression
import sklearn
import psycopg2
import configparser

app = Flask(__name__)
housing_prices_model = pickle.load(open(r"ML Models/housing_prices_pred_without_furnishing.pkl", "rb"))
client = boto3.client('rekognition')

config = configparser.ConfigParser()
config.read('config-correct.ini')
username = config["POSTGRES"]["user"]
password = config["POSTGRES"]["pass"]

conn = psycopg2.connect(f"host=127.0.0.1 dbname=user_logs user={username} password={password}")
cur = conn.cursor()


class MySQLAlchemy(SQLAlchemy):
    Column: Callable
    String: Callable
    Integer: Callable


app.config['SECRET_KEY'] = 'the random string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DBs/user.db'
app.config['UPLOAD_FOLDER'] = r"static/Photos"
db = MySQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(120), nullable=False)


db.create_all()


@app.before_request
def auto_expiration():
    try:
        now = datetime.now(timezone.utc) + timedelta(hours=2)
        login_time = session["login_time"]

        delta = now - login_time
        print(delta.seconds)

        if delta.seconds >= 1800:
            req = query_user_params(session["user"], method="GET", status="Success", route='/logout',
                                    date=session["last_activity"])

            session.pop("user")
            session.pop("login_time")
            session.pop("last_activity")

            add_request_to_db(req)

        session["last_activity"] = now

    except:
        pass


@app.route("/logout")
def logout():
    print("user" in session)
    if "user" in session:
        req = query_user_params(session["user"], method="GET", status="Success", route='/logout',
                                date=datetime.now())
        add_request_to_db(req)

        session.pop("user")
        session.pop("login_time")
        session.pop("last_activity")

        return redirect(url_for("login_page"))

    return redirect(url_for("login_page"))


@app.route("/")
def root_route():
    if "user" not in session:
        return redirect(url_for("login_page"))
    print(session["user"])
    return render_template("main.html")


def query_amazon(file):
    response = client.recognize_celebrities(Image={'Bytes': file.read()})
    if response['CelebrityFaces']:
        person = response['CelebrityFaces'][0]
        name = person["Name"]
        return name
    return "Unindentified"


def query_user_params(email, method, status, route, date):
    current_user = User.query.filter_by(email=email).first()

    req = {
        "username": current_user.email,
        "user_id": current_user.id,
        "name": current_user.name,
        "surname": current_user.surname,
        "gender": current_user.gender,
        "method": method,
        "route": route,
        "status": status,
        "time": date.strftime("%d/%m/%Y %H:%M:%S").split(' ')[1],
        "date": date.strftime("%d/%m/%Y %H:%M:%S").split(' ')[0]
    }

    return req


def add_request_to_db(req):
    print(type(req["time"]), type(req["date"]))
    cur.execute(f'''INSERT INTO logs (username, user_id, name, surname, gender, method, route, status, time, date) 
                                VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                (req["username"], req["user_id"], req["name"], req["surname"], req["gender"], req["method"],
                 req["route"], req["status"], req["time"], req["date"]))
    conn.commit()


@app.route("/celebrity", methods=["POST", "GET"])
def celebrity():
    if "user" not in session:
        return redirect(url_for("login_page"))
    if request.method == "POST":
        file = request.files['filename']
        if not file:
            req = query_user_params(session["user"], method="POST", status="Error", route="/celebrity",
                                    date=datetime.now())
            add_request_to_db(req)
            print(req)

            flash("Please select the file!")
            return redirect(url_for("celebrity"))

        req = query_user_params(session["user"], method="POST", status="Success", route="/celebrity",
                                date=datetime.now())
        add_request_to_db(req)

        name = query_amazon(file)
        if name == "Unindentified":
            result = "Unindentified"
        else:
            result = "This is the " + name

        return render_template("celebrity-result.html", result=result)

    req = query_user_params(session["user"], method="GET", status="Success", route="/celebrity", date=datetime.now())
    print(req)
    add_request_to_db(req)

    return render_template("celebrity.html")


@app.route("/house-price", methods=["POST", "GET"])
def house_price():
    if "user" not in session:
        return redirect(url_for("login_page"))
    if request.method == "POST":
        input_lst_for_model = []
        string_params = ["mainroad", "guestrooms", "basement", "waterheating", "airconditioning", "pref-area"]
        for param in request.form:
            if not request.form[param]:
                flash("Please fill all the fields!")

                req = query_user_params(session["user"], method="POST", status="Error", route='/house-price',
                                        date=datetime.now())
                add_request_to_db(req)
                print(req)

                return redirect(url_for("house_price"))

            if not request.form[param].isnumeric() or param in string_params:
                if request.form[param].lower().strip() == "yes":
                    input_lst_for_model.append(1)
                    continue
                elif request.form[param].lower().strip() == "no":
                    input_lst_for_model.append(0)
                    continue
                else:
                    flash("Please input only Yes/No in the Text Fields!")

                    req = query_user_params(session["user"], method="POST", status="Error", route='/house-price',
                                            date=datetime.now())
                    add_request_to_db(req)
                    print(req)

                    return redirect(url_for("house_price"))

            input_lst_for_model.append(int(request.form[param]))

        req = query_user_params(session["user"], method="POST", status="Success", route='/house-price',
                                date=datetime.now())
        add_request_to_db(req)
        print(req)

        print(input_lst_for_model)
        price = round(housing_prices_model.predict([input_lst_for_model])[0][0])
        result = f"Approximate price is {price}$"
        return render_template("house-result.html", result=result)

    req = query_user_params(session["user"], method="GET", status="Success", route='/house-price', date=datetime.now())
    add_request_to_db(req)
    print(req)
    return render_template("house-price.html")


@app.route("/login", methods=["POST", "GET"])
def login_page():
    if "user" in session:
        return redirect(url_for("root_route"))
    if request.method == "POST":
        print(request.form)
        current_user = User.query.filter_by(email=request.form["email"]).first()

        if current_user:
            if current_user.password == request.form["password"]:

                session["user"] = current_user.email
                session["login_time"] = datetime.now(timezone.utc) + timedelta(hours=2)
                session["last_activity"] = session["login_time"]

                if "user" in session:
                    req = query_user_params(session["user"], method="GET", status="Success", route='/login',
                                            date=datetime.now())
                    add_request_to_db(req)

                print(session)
                return redirect(url_for("root_route"))
            else:
                flash("Incorrect Password!")
                return redirect(url_for("login_page"))
        else:
            flash("Email is not registered!")
            return redirect(url_for("login_page"))

    return render_template("login.html")


@app.route("/register", methods=["POST", "GET"])
def register_page():
    if request.method == "POST":
        params = [request.form["name"], request.form["surname"], request.form["email"], request.form["password"],
                  request.form["gender"]]
        # print(params)

        for param in params:
            if not param:
                flash("Please fill all the fields!")
                return redirect(url_for("register_page"))

        lst_of_genders = ["m", "f", "male", "female"]

        if request.form["gender"].strip().lower() not in lst_of_genders:
            flash("Please input 'male' or 'female'")
            return redirect(url_for("register_page"))
        else:
            indx_gender = lst_of_genders.index(request.form["gender"])
            if indx_gender % 2 == 0:
                user_gender = "m"
            else:
                user_gender = "f"

        if User.query.filter_by(email=request.form["email"]).first():
            flash("Email is already registered")
            return redirect(url_for("register_page"))
        else:
            if not User.query.all():
                user_id = 0
            else:
                user_id = User.query.order_by(User.id.desc()).first().id + 1
            new_user = User(id=user_id, name=request.form["name"], surname=request.form["surname"],
                            email=request.form["email"], password=request.form["password"], gender=user_gender)

            db.session.add(new_user)
            db.session.commit()

            req = query_user_params(new_user.email, method="POST", status="Success", route='/register',
                                    date=datetime.now())
            add_request_to_db(req)

            print(User.query.all())
            return redirect(url_for("login_page"))
    return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)
