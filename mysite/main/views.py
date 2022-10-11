from django.shortcuts import redirect, render
import sqlite3
import os
from django.contrib import messages
import matplotlib.pyplot as plt
from django.template.defaulttags import register

from Process.create_dashboards import Processing

db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'DB', 'target_db.db'))
conn = sqlite3.connect(db_path, check_same_thread=False)
curr = conn.cursor()

abs_path_static = os.path.dirname(os.path.abspath(__file__)) + "\\static\\"
print(abs_path_static)



def fetch_data_from_db(email, password):
    curr.execute('SELECT password FROM users WHERE email = (?)', (email,))
    result = curr.fetchall()
    print("Result ", result)

    if not result:
        return False

    db_pass = result[0][0]
    print("Db_pass", db_pass)
    if db_pass != password:
        return "Wrong Pass"

    return True


def insert_record_to_db(req):
    name = req.get("name")
    surname = req.get("surname")
    email = req.get("email")
    password = req.get("password")

    curr.execute("INSERT INTO users (email, name, surname, password) VALUES (?, ?, ?, ?)",
                 (email, name, surname, password))
    conn.commit()


@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)


def dashboards(request):
    if "username" not in request.session:
        return redirect("/login/")

    processing = Processing()

    plt_time_period_week = processing.mostLoadedPeriodWeekTest()
    plt_time_period_week.savefig(abs_path_static + "mostLoadedPeriodWeek.png", dpi=100)

    plt_time_period_today = processing.mostLoadedTimePeriodToday()
    plt_time_period_today.savefig(abs_path_static + "mostLoadedTimePeriodToday.png", dpi=100)

    plt_male_female = processing.maleOrFemale()
    plt_male_female.savefig(abs_path_static + "maleOrFemale.png", dpi=100)
    plt_male_female.clf()

    plt_most_popular_route = processing.theMostPopularRoute()
    plt_most_popular_route.savefig(abs_path_static + "theMostPopularRoute.png")

    return render(request, "main/dashboards.html", {
        "plots": {
            "mostLoadedPeriodWeek": {"name": "Most Loaded Time Period Week",
                                     "path": "/mostLoadedPeriodWeek.png"},

            "mostLoadedTimePeriodToday": {"name": "Most Loaded Time Period Today",
                                          "path": "/mostLoadedTimePeriodToday.png"},

            "maleOrFemale": {"name": "Male/Female ratio",
                             "path": "/maleOrFemale.png"},

            "theMostPopularRoute": {"name": "The Most Popular Route",
                                    "path": "/theMostPopularRoute.png"}
        }
    })


def plotting_on_the_website(period, folder, processing, measure,
                            amount_of_users, amount_of_new_users):
    repeat_visitors_ratio = processing.repeatVisitors(period=period)

    # Will be deleted maybe
    plt_time_period_week = processing.mostLoadedPeriodWeekTest()
    plt_time_period_week.savefig(abs_path_static + f"\\{folder}\\mostLoadedPeriodWeek.png", dpi=100)
    plt_time_period_week.clf()

    # Pie-chart with routes and amount of requests made on them
    plt_most_popular_route = processing.theMostPopularRoute(period=period)
    views_on_the_routes = processing.amountOfViewsRoute(period=period)
    plt_most_popular_route.savefig(abs_path_static + f"\\{folder}\\theMostPopularRoute.png", dpi=100)

    # Chart with overall amount of actions throughout the week
    amount_of_actions_per_visit, plt_amount_of_actions_per_visit = processing.actionsPerVisit(period=period,
                                                                                              purpose="count-sum")
    plt_amount_of_actions_per_visit.savefig(abs_path_static + f"\\{folder}\\actionsPerVisit.png", dpi=100)

    # Chart with average amount of actions throughout the week
    amount_of_actions_per_visit_average, plt_amount_of_actions_per_visit_average = processing.actionsPerVisit(
        period=period, purpose="count-average")
    plt_amount_of_actions_per_visit_average.savefig(abs_path_static + f"\\{folder}\\actionsPerVisitAverage.png",
                                                    dpi=100)

    # Chart with average amount of time spent on the website
    plt_average_user_session, average_user_session = processing.averageUserSessionNew(period=period)
    plt_average_user_session.savefig(abs_path_static + f"\\{folder}\\averageUserSession.png", dpi=100)

    # Count Unique Sessions
    plt_count_sessions, count_sessions = processing.countSessions(period=period)
    plt_count_sessions.savefig(abs_path_static + f"\\{folder}\\countSessions.png", dpi=100)

    # Bounce Rate
    plt_bounce_rate, bounce_rate = processing.bounceRate(period=period)
    plt_bounce_rate.savefig(abs_path_static + f"\\{folder}\\bounceRate.png", dpi=100)

    # Conversion Rate
    plt_conversion_rate, conversion_rate = processing.conversionRate(period=period)
    plt_conversion_rate.savefig(abs_path_static + f"\\{folder}\\conversionRate.png", dpi=100)

    # Time to make a Conversion
    plt_time_to_make_a_conversion, time_to_make_a_conversion = processing.timeToMakeAPostRequest(period=period)
    plt_time_to_make_a_conversion.savefig(abs_path_static + f"\\{folder}\\timeToMakeAPostRequest.png", dpi=100)
    plt_time_to_make_a_conversion.clf()

    # Amount of males and females
    plt_gender, gender = processing.maleOrFemale(period=period)
    plt_gender.savefig(abs_path_static + f"\\{folder}\\maleOrFemale.png", dpi=100)

    print(gender)

    return {
        "plots": {
            "numbers": {"amount_of_users_week": amount_of_users,
                        "amount_of_new_users_week": amount_of_new_users,
                        "repeat_visitors_ratio": repeat_visitors_ratio},

            "mostLoadedPeriodWeek": {"name": f"Most Loaded Time Period per {period}",
                                     "path": f"{folder}/mostLoadedPeriodWeek.png"},

            "theMostPopularRoute": {"name": "Ratio of views on the routes",
                                    "path": f"{folder}/theMostPopularRoute.png",
                                    "celebrity": views_on_the_routes[1],
                                    "house-price": views_on_the_routes[0]},

            "actionsPerVisit": {"name": f"Sum of actions per {measure} throughout the {period}",
                                "path": f"{folder}/actionsPerVisit.png",
                                "value": amount_of_actions_per_visit},

            "actionsPerAverage": {"name": f"Average amount of actions per {measure} throughout the {period}",
                                  "path": f"{folder}/actionsPerVisitAverage.png",
                                  "value": amount_of_actions_per_visit_average},

            "averageUserSession": {"name": f"Average session time of the user throughout the {period}",
                                   "path": f"{folder}/averageUserSession.png",
                                   "value": average_user_session},

            "countSessions": {"name": f"Amount of sessions per {measure} throughout the {period}",
                              "path": f"{folder}/countSessions.png",
                              "value": count_sessions},

            "bounceRate": {"name": f"Bounce Rate per {measure} throughout the {period}",
                           "path": f"{folder}/bounceRate.png",
                           "value": bounce_rate},

            "conversionRate": {"name": f"Conversion Rate per {measure} throughout the {period}",
                               "path": f"{folder}/conversionRate.png",
                               "value": conversion_rate},

            "timeToMakeAPostRequest": {
                "name": f"Average time to make a conversion per {measure} throughout the {period}",
                "path": f"{folder}/timeToMakeAPostRequest.png",
                "value": time_to_make_a_conversion},

            "maleOrFemale": {"name": f"Male/Female ratio throughout the {period}",
                             "path": f"{folder}/maleOrFemale.png",
                             "male": gender[0],
                             "female": gender[1]},
        }
    }


def report_daily(request):
    if "username" not in request.session:
        return redirect("/login/")

    processing = Processing()

    amount_of_users_day = processing.amountOfUsersToday()
    amount_of_new_users_day = processing.amountOfNewUsersToday()

    daily_dict = plotting_on_the_website(period="day", folder="daily", processing=processing, measure="hour",
                                         amount_of_users=amount_of_users_day,
                                         amount_of_new_users=amount_of_new_users_day)

    return render(request, "main/dashboards-daily.html", daily_dict)


def report_weekly(request):
    if "username" not in request.session:
        return redirect("/login/")

    processing = Processing()

    # Extracting numbers
    amount_of_users_week = processing.amountOfUsersWeek()
    amount_of_new_users_week = processing.amountOfNewUsersWeek()

    # Using plotting function
    weekly_dict = plotting_on_the_website(period="week", folder="weekly", processing=processing, measure="day",
                                          amount_of_users=amount_of_users_week,
                                          amount_of_new_users=amount_of_new_users_week)

    return render(request, "main/dashboards-weekly.html", weekly_dict)


def logout(request):
    if "username" in request.session:
        request.session.pop("username")
        return redirect("/login/")

    return redirect("/login/")


def index(request):
    if "username" not in request.session:
        return redirect("/login/")
    return render(request, "main/base.html")


def login(request):
    if "username" in request.session:
        return redirect("/")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        result = fetch_data_from_db(email, password)

        if not result:
            messages.error(request, 'User is not registered!')
            return redirect("/login/")

        if result == "Wrong Pass":
            messages.error(request, 'Wrong Password!')
            return redirect("/login/")

        request.session["username"] = email
        return redirect("/")

    return render(request, "main/login.html")


def register(request):
    if request.method == "POST":

        for val in request.POST.keys():
            if not request.POST[val]:
                messages.error(request, 'Please fill all the fields!')
                return redirect("/register/")

        curr.execute('SELECT password FROM users WHERE email = (?)', (request.POST.get("email"),))
        result = curr.fetchall()

        if result:
            messages.error(request, 'Email is already registered!')
            return redirect("/register/")

        insert_record_to_db(request.POST)
        return redirect("/login/")

    return render(request, "main/register.html")
