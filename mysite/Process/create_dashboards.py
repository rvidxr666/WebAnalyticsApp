import psycopg2
import configparser

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns

import datetime as dt

username = "postgres"
password = "postgres"


class Processing:

    def __init__(self):
        self.conn = psycopg2.connect(f"host=127.0.0.1 dbname=user_logs user={username} password={password}")
        self.cur = self.conn.cursor()

        self.df = pd.read_sql("SELECT * FROM logs", self.conn)
        self.date_today = dt.date.today()
        self.unique_users = self.df.username.unique()
        self.df_today = self.df[self.df.date == self.date_today]

        self._last_week_dates = [self.date_today - dt.timedelta(days=x) for x in range(7)]
        self.df_weekly = self.df[self.df.date.isin(self._last_week_dates)]

    def amountOfRequests(self):
        amount = len(self.df)
        return amount

    def _weeklyReport(self, column: str, lst_of_column_vals: list, users: bool = False, graph=True):
        lst_of_last_week_dates = [self.date_today - dt.timedelta(days=x) for x in range(7)]
        weekly_df = self.df[self.df.date.isin(lst_of_last_week_dates)]

        if not users:
            amounts = [len(weekly_df[weekly_df[column] == val]) for val in lst_of_column_vals]
            plt = self.pieChart(amounts, lst_of_column_vals, "Most Popular Routes")
        else:
            amounts = [len(weekly_df[weekly_df[column] == val].username.unique()) for val in lst_of_column_vals]
            plt = self.pieChart(amounts, ["male", "female"], "Most Popular Routes")

        if graph:
            return plt

        return amounts

    def _dailyReport(self, column: str, lst_of_column_vals: list, users: bool = False, graph=True):
        today_df = self.df[self.df.date == self.date_today]

        if not users:
            amounts = [len(today_df[today_df[column] == val]) for val in lst_of_column_vals]
            plt = self.pieChart(amounts, lst_of_column_vals, "Most Popular Routes")
        else:
            amounts = [len(today_df[today_df[column] == val].username.unique()) for val in lst_of_column_vals]
            plt = self.pieChart(amounts, ["male", "female"], "Most Popular Routes")

        if graph:
            return plt

        return amounts

    def theMostPopularRoute(self, period=""):
        lstOfRoutes = list(self.df.route.unique())
        not_needed_routes = ["/login", "/logout", '/register']

        [lstOfRoutes.remove(route) for route in not_needed_routes if
         route in not_needed_routes and route in lstOfRoutes]

        if period == "week":
            plot = self._weeklyReport("route", lstOfRoutes, graph=True)
            return plot

        if period == "day":
            plot = self._dailyReport("route", lstOfRoutes, graph=True)
            return plot

        amounts = [len(self.df[self.df.route == route]) for route in lstOfRoutes]
        plot = self.pieChart(amounts, lstOfRoutes, "Most Popular Routes")
        return plot

    def amountOfViewsRoute(self, period=""):
        lstOfRoutes = list(self.df.route.unique())
        not_needed_routes = ["/login", "/logout", '/register']

        [lstOfRoutes.remove(route) for route in not_needed_routes if
         route in not_needed_routes and route in lstOfRoutes]

        if period == "week":
            routes_weekly_views = self._weeklyReport("route", lstOfRoutes, graph=False)
            return routes_weekly_views

        if period == "day":
            routes_daily_views = self._dailyReport("route", lstOfRoutes, graph=False)
            return routes_daily_views

    def amountOfUsersToday(self):
        amount = len(self.df[self.df.date == self.date_today].username.unique())
        return amount

    def amountOfNewUsersToday(self):
        amount = len(self.df[(self.df.route == "/register") & (self.df.date == self.date_today)])
        return amount

    def amountOfNewUsersWeek(self):
        lst_of_last_week_dates = [self.date_today - dt.timedelta(days=x) for x in range(7)]
        amount = len(self.df[(self.df.route == "/register") & (self.df.date.isin(lst_of_last_week_dates))])
        return amount

    def amountOfUsersWeek(self):
        lst_of_last_week_dates = [self.date_today - dt.timedelta(days=x) for x in range(7)]
        amount = len(self.df[self.df.date.isin(lst_of_last_week_dates)].username.unique())
        return amount

    def averageUserSession(self):
        lstOfUniqueUsers = self.df.username.unique()
        session_time_lst = []

        for user in lstOfUniqueUsers:
            df_user = self.df[(self.df.username == user)][(self.df.route == "/login") | (self.df.route == "/logout")]
            df_user.reset_index(inplace=True, drop=True)
            print(df_user)

            for i, row in df_user.iterrows():
                if row.route == "/login":

                    try:
                        login_time = dt.datetime.combine(dt.date.min, row["time"])
                        logout_time = dt.datetime.combine(dt.date.min, df_user.iloc[i + 1, 8])

                        difference = logout_time - login_time
                        session_time_lst.append(difference)
                    except IndexError:
                        pass

        average_session_time = sum(session_time_lst, dt.timedelta(0)) / len(session_time_lst)
        average_session_time = average_session_time - dt.timedelta(microseconds=average_session_time.microseconds)

        return average_session_time

    def maleOrFemale(self, period=""):

        if period == "week":
            plt = self._weeklyReport("gender", ["m", "f"], users=True, graph=True)
            val = self._weeklyReport("gender", ["m", "f"], users=True, graph=False)

            return plt, val

        if period == "day":
            plt = self._dailyReport("gender", ["m", "f"], users=True, graph=True)
            val = self._dailyReport("gender", ["m", "f"], users=True, graph=False)

            return plt, val

        unique_male_count = len(self.df[self.df.gender == "m"].username.unique())
        unique_female_count = len(self.df[self.df.gender == "f"].username.unique())

        plt = self.pieChart([unique_male_count, unique_female_count], labels=["male", "female"],
                            title=r"Male/Female Ratio")
        return plt

    def pieChart(self, data, labels, title):
        colors = sns.color_palette('pastel')[0:5]
        plt.pie(data, labels=labels, colors=colors, autopct='%.0f%%')

        plt.tight_layout()

        return plt

    def barPlot(self, lst_for_x, lst_for_y, title, date: bool = False):

        if date:
            fig, ax = plt.subplots()
            bars = ax.plot(lst_for_x, lst_for_y, label="requests")

            plt.xticks(rotation=45)
            plt.yticks([])

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.spines['bottom'].set_color('#DDDDDD')

            plt.tight_layout()
            return plt

        fig, ax = plt.subplots()
        bars = ax.bar(lst_for_x, lst_for_y, label="requests")

        ax.set_xticks(list(lst_for_x))
        plt.xticks(rotation=45)
        plt.yticks([])

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_color('#DDDDDD')
        ax.tick_params(bottom=False, left=False)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color='#EEEEEE')
        ax.xaxis.grid(False)

        bar_color = bars[0].get_facecolor()
        for bar in bars:
            if bar.get_height():
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + (bar.get_height() * 0.03),
                    round(bar.get_height(), 1),
                    horizontalalignment='center',
                    color=bar_color,
                    weight='bold'
                )

        plt.tight_layout()
        return plt

    def mostLoadedTimePeriodToday(self):
        df = self.df[self.df.date == self.date_today]
        processes_column_hours = df.time.apply(
            lambda x: int(str(x.replace(microsecond=0, second=0, minute=0)).split(":")[0]))
        list_of_hours = list(processes_column_hours)
        hours = range(0, 24)

        dict_for_plot = {}
        for hour in hours:
            dict_for_plot[str(hour) + ":00"] = list_of_hours.count(hour)

        plt = self.barPlot(dict_for_plot.keys(), dict_for_plot.values(), "Right Now")

        return plt

    def mostLoadedPeriodWeekTest(self):
        grouped_df = self.df.groupby(self.df.date).size()
        dict_grouped_df = dict(grouped_df)

        lst_of_last_week_dates = [self.date_today - dt.timedelta(days=x) for x in range(7)]
        plotting_dict = {}
        for date in lst_of_last_week_dates:
            if date in dict_grouped_df.keys():
                plotting_dict[date] = dict_grouped_df[date]
            else:
                plotting_dict[date] = 0

        converted_dates = [date.strftime('%m/%d/%Y') for date in plotting_dict.keys()][::-1]
        values = list(plotting_dict.values())[::-1]

        print(values)

        plt = self.barPlot(converted_dates, values, "Last Week")

        return plt

    def _countRepeatVistors(self, df, lst_of_unique_users):
        lst_of_repeat_users = []

        for user in lst_of_unique_users:
            amount_of_entries = len(df[(df.username == user) & (df.route == "/login")])
            if amount_of_entries > 1:
                lst_of_repeat_users.append((user, amount_of_entries))

        if lst_of_repeat_users:
            ratio = round(len(lst_of_repeat_users) / len(lst_of_unique_users) * 100)
        else:
            ratio = 0

        return ratio

    def repeatVisitors(self, period=""):
        if period == "day":
            lst_of_unique_users = self.df_today.username.unique()
            ratio = self._countRepeatVistors(self.df_today, lst_of_unique_users)

            return ratio

        if period == "week":
            lst_of_unique_users = self.df_weekly.username.unique()
            ratio = self._countRepeatVistors(self.df_weekly, lst_of_unique_users)

            return ratio

        lst_of_unique_users = self.df.username.unique()
        ratio = self._countRepeatVistors(self.df, lst_of_unique_users)

        return ratio

    def _extractSessions(self, df, lst_of_unique_users, is_count_sessions=False):

        lst_of_sessions = []

        for user in lst_of_unique_users:
            df_user_sessions = df[df.username == user].reset_index(drop=True)
            df_login_logout = df_user_sessions.query('route == "/login" or route == "/logout"')

            prev_tuple = ()

            for tup in zip(df_login_logout.index, df_login_logout["username"], df_login_logout["route"]):
                if tup[2] == "/logout" and prev_tuple:
                    session_df = df_user_sessions.iloc[prev_tuple[0]:tup[0] + 1].reset_index(drop=True)
                    lst_of_sessions.append(session_df)

                elif tup[2] == "/login":
                    prev_tuple = tup

        return lst_of_sessions

    def _extractSessionsPerPeriod(self, df, lst_of_periods, column, purpose="count"):

        dict_with_periods = {}
        allowed_values = ["hour", "date"]

        if column not in allowed_values:
            raise ValueError("Not allowed value! Should be 'hour' or 'date'!")

        if not df.empty:

            if column == "hour":
                df["hour"] = df.apply(lambda x: x["time"].hour, axis=1)

            for period in lst_of_periods:
                df_period = df[df[column] == period]
                lst_of_unique_users = df_period.username.unique()

                if purpose == "count":
                    sessions = self._extractSessions(df_period, lst_of_unique_users)
                    dict_with_periods[period] = sessions

                if purpose == "count-post-requests":
                    time_for_post = self.amountOfTimeForPost(df_period, lst_of_unique_users)
                    dict_with_periods[period] = time_for_post

        else:
            for period in lst_of_periods:
                dict_with_periods[period] = []

        return dict_with_periods

    def amountOfTimeForPost(self, df, lst_of_unique_users):
        lst_of_sessions = self._extractSessions(df, lst_of_unique_users)
        lst_of_diffs = []

        for session_df in lst_of_sessions:
            login_time = session_df[session_df.route == "/login"].time.values[0]
            post_requests = session_df[session_df.method == "POST"].time.values
            usrname = session_df.username.values[0]

            if post_requests.any():
                first_post_request = post_requests[0]

                first_post_request_subs = dt.datetime.combine(dt.datetime.min, first_post_request)
                login_time_subs = dt.datetime.combine(dt.datetime.min, login_time)

                diff = first_post_request_subs - login_time_subs
                lst_of_diffs.append(diff)

        if lst_of_diffs:
            average_diff = sum(lst_of_diffs, dt.timedelta(0)) / len(lst_of_diffs)
            average_diff_time = average_diff - dt.timedelta(microseconds=average_diff.microseconds)
            return average_diff_time
        else:
            return dt.timedelta(seconds=0)

    def testing_shit(self):
        self._extractSessionsPerPeriod(df=self.df_today, lst_of_periods=range(0, 24), column="hour",
                                       purpose="count")

    def countSessions(self, period=""):

        if period == "day":
            lst_with_sessions = self._extractSessions(self.df_today, self.df_today.username.unique())
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_today, range(0, 24), "hour")

            hours_lst = [str(key) + ":00" for key in dict_with_sessions.keys()]

            amount_of_sessions = []
            for key in dict_with_sessions:

                if dict_with_sessions[key] == 0:
                    amount_of_sessions.append(dict_with_sessions[key])
                else:
                    amount_of_sessions.append(len(dict_with_sessions[key]))

            plt = self.barPlot(hours_lst[::-1], amount_of_sessions[::-1], title="Amount of Sessions")
            overall_amount_of_sessions_daily = len(lst_with_sessions)

            return plt, overall_amount_of_sessions_daily

        if period == "week":
            lst_with_sessions = self._extractSessions(self.df_weekly, self.df_weekly.username.unique())
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_weekly, self._last_week_dates, "date")

            dates_dict = [str(key) for key in dict_with_sessions.keys()]
            amount_of_sessions = [len(dict_with_sessions[key]) for key in dict_with_sessions]

            plt = self.barPlot(dates_dict[::-1], amount_of_sessions[::-1], title="Amount of Sessions")
            overall_amount_of_sessions_weekly = len(lst_with_sessions)

            return plt, overall_amount_of_sessions_weekly

    def _countingActions(self, df, period, column: str, purpose):

        lst_of_lengths = []
        dict_for_plot = {}

        dict_with_sessions = self._extractSessionsPerPeriod(df, period, column=column, purpose="count")
        for key in dict_with_sessions:

            if dict_with_sessions[key]:
                count_length_of_sessions = 0

                for session in dict_with_sessions[key]:
                    lst_of_lengths.append(len(session))
                    count_length_of_sessions += len(session)

                if purpose == "count-average":
                    dict_for_plot[key] = round(count_length_of_sessions / len(dict_with_sessions[key]))

                elif purpose == "count-sum":
                    dict_for_plot[key] = count_length_of_sessions

            else:
                dict_for_plot[key] = 0

        if lst_of_lengths:
            average = round(sum(lst_of_lengths) / len(lst_of_lengths))
            summa = sum(lst_of_lengths)
        else:
            average = 0
            summa = 0

        if purpose == "count-average":
            return average, dict_for_plot

        elif purpose == "count-sum":
            return summa, dict_for_plot

        else:
            raise ValueError("'purpose' value is not correctly defined")

    def actionsPerVisit(self, period, purpose):

        if period == "day":
            val, dict = self._countingActions(self.df_today, range(0, 24), column="hour", purpose=purpose)
            plt = self.barPlot([str(key) + ":00" for key in dict], dict.values(), title="")
            return val, plt

        if period == "week":
            val, dict = self._countingActions(self.df_weekly, self._last_week_dates, column="date", purpose=purpose)
            plt = self.barPlot([str(key) for key in dict][::-1], list(dict.values())[::-1], title="")
            return val, plt

    def _converTimesForPlottable(self, values_to_convert):
        zero = dt.datetime(2018, 1, 1)

        time = [zero + t for t in values_to_convert]
        zero = mdates.date2num(zero)
        time = [t - zero for t in mdates.date2num(time)]

        return time

    def _processingDictForTime(self, dict_to_process):
        for key in dict_to_process:
            if not dict_to_process[key]:
                dict_to_process[key] = dt.timedelta(seconds=0)

        return dict_to_process

    def timeToMakeAPostRequest(self, period=""):

        if period == "day":
            dict_with_times = self._extractSessionsPerPeriod(self.df_today, range(0, 24), "hour", "count-post-requests")
            average_time = self.amountOfTimeForPost(self.df_today, self.df_today.username.unique())

            dict_with_times = self._processingDictForTime(dict_with_times)

            time = self._converTimesForPlottable(dict_with_times.values())
            plt = self.barPlot([str(key) + ":00" for key in dict_with_times.keys()], time, title="", date=True)

            return plt, average_time

        if period == "week":
            dict_with_times = self._extractSessionsPerPeriod(self.df_weekly, self._last_week_dates, "date",
                                                             "count-post-requests")

            average_time = self.amountOfTimeForPost(self.df_weekly, self.df_weekly.username.unique())
            dict_with_times = self._processingDictForTime(dict_with_times)
            time = self._converTimesForPlottable(dict_with_times.values())
            plt = self.barPlot([str(key) for key in dict_with_times.keys()][::-1], time[::-1], title="", date=True)

            return plt, average_time

    def _countTimeUserSession(self, dict_with_sessions):
        dict_for_plot = {}
        lst_for_final_value = []

        for key in dict_with_sessions:

            if dict_with_sessions[key] == 0:
                dict_for_plot[key] = 0
                continue

            lst_for_diff_per_period = []
            lst_with_sessions_per_period = dict_with_sessions[key]

            for session in lst_with_sessions_per_period:
                df = session[(session.route == "/login") | (session.route == "/logout")]
                df.reset_index(inplace=True, drop=True)

                login_time = df.iloc[0, 8]
                logout_time = df.iloc[1, 8]

                login_time = dt.datetime.combine(dt.datetime.min, login_time)
                logout_time = dt.datetime.combine(dt.datetime.min, logout_time)

                diff = logout_time - login_time
                lst_for_diff_per_period.append(diff)

                lst_for_final_value.append(diff)

            dict_for_plot[key] = lst_for_diff_per_period

        return lst_for_final_value, dict_for_plot

    def _countBounceRate(self, lst_for_overall_bounce_rate, dict_with_periods):

        dict_for_plot = {}

        count_bounces_overall = 0

        for diff in lst_for_overall_bounce_rate:
            if diff <= dt.timedelta(seconds=3):
                count_bounces_overall += 1

        if lst_for_overall_bounce_rate:
            overall_bounce_rate = round((count_bounces_overall / len(lst_for_overall_bounce_rate)) * 100)
        else:
            overall_bounce_rate = 0

        for period in dict_with_periods:
            count_bounces = 0
            lst_with_diffs = []

            for diff in dict_with_periods[period]:
                lst_with_diffs.append(diff)
                if diff <= dt.timedelta(seconds=3):
                    count_bounces += 1

            if lst_with_diffs:
                dict_for_plot[period] = round((count_bounces / len(lst_with_diffs)) * 100)
            else:
                dict_for_plot[period] = 0

        print("Dict", dict_for_plot, "\n", "Overall bounce rate:", overall_bounce_rate)
        return dict_for_plot, overall_bounce_rate

    def bounceRate(self, period):
        if period == "day":
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_today, range(0, 24), "hour", purpose="count")
            overall_lst, dict_for_plot = self._countTimeUserSession(dict_with_sessions)
            dict_for_plot, overall_bounce_rate = self._countBounceRate(overall_lst, dict_for_plot)

            plot = self.barPlot([str(key) + ":00" for key in dict_for_plot.keys()], dict_for_plot.values(), title="")

            return plot, overall_bounce_rate

        if period == "week":
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_weekly, self._last_week_dates, "date",
                                                                purpose="count")
            overall_lst, dict_for_plot = self._countTimeUserSession(dict_with_sessions)
            self._countBounceRate(overall_lst, dict_for_plot)

            dict_for_plot, overall_bounce_rate = self._countBounceRate(overall_lst, dict_for_plot)
            plot = self.barPlot([str(key) for key in dict_for_plot][::-1], list(dict_for_plot.values())[::-1], title="")

            return plot, overall_bounce_rate

    def _countTimeDeltaAverage(self, lst):

        average = sum(lst, dt.timedelta(0)) / len(lst)
        average = average - dt.timedelta(microseconds=average.microseconds)

        return average

    def _countAverageUserSession(self, overall_lst, dict_for_plot):

        if overall_lst:
            overall_average_session_time = self._countTimeDeltaAverage(overall_lst)
        else:
            overall_average_session_time = dt.timedelta(seconds=0)

        final_dict_for_plot = {}

        for key in dict_for_plot:
            sessions_per_period = dict_for_plot[key]

            if sessions_per_period:
                session_time_per_period = self._countTimeDeltaAverage(sessions_per_period)
            else:
                session_time_per_period = dt.timedelta(seconds=0)

            final_dict_for_plot[key] = session_time_per_period

        return final_dict_for_plot, overall_average_session_time

    def averageUserSessionNew(self, period):
        if period == "day":
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_today, range(0, 24), "hour", purpose="count")
            overall_lst, dict_for_plot = self._countTimeUserSession(dict_with_sessions)

            final_dict_for_plot, overall_average_session_time = self._countAverageUserSession(overall_lst,
                                                                                              dict_for_plot)
            times = self._converTimesForPlottable(final_dict_for_plot.values())

            plt = self.barPlot([str(key) + ":00" for key in final_dict_for_plot.keys()], times, title="", date=True)

            return plt, overall_average_session_time

        if period == "week":
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_weekly, self._last_week_dates, "date",
                                                                purpose="count")
            overall_lst, dict_for_plot = self._countTimeUserSession(dict_with_sessions)

            final_dict_for_plot, overall_average_session_time = self._countAverageUserSession(overall_lst,
                                                                                              dict_for_plot)

            times = self._converTimesForPlottable(final_dict_for_plot.values())
            plt = self.barPlot([str(key) for key in final_dict_for_plot.keys()][::-1], times[::-1], title="", date=True)

            return plt, overall_average_session_time

    def _countConversionRate(self, dict_with_sessions):

        dict_for_plot = {}
        overall_count_of_conversions = 0
        overall_count_of_sessions = 0

        for key in dict_with_sessions:
            lst_with_sessions = dict_with_sessions[key]

            conversions_per_period = 0

            for session in lst_with_sessions:
                print(session)
                overall_count_of_sessions += 1

                if "POST" in list(session.method):
                    conversions_per_period += 1
                    overall_count_of_conversions += 1

            if lst_with_sessions:
                dict_for_plot[key] = round((conversions_per_period / len(lst_with_sessions)) * 100)
            else:
                dict_for_plot[key] = 0

        print("overall count of sessions", overall_count_of_sessions)
        print("overall count of conversions", overall_count_of_conversions)
        if overall_count_of_sessions:
            overall_conversion_rate = round(overall_count_of_conversions / overall_count_of_sessions * 100)
        else:
            overall_conversion_rate = 0

        return dict_for_plot, overall_conversion_rate

    def conversionRate(self, period):
        if period == "day":
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_today, range(0, 24), "hour", purpose="count")
            dict_for_plot, overall_conversion_rate = self._countConversionRate(dict_with_sessions)

            plot = self.barPlot([str(key) + ":00" for key in dict_for_plot.keys()], dict_for_plot.values(), title="")
            return plot, overall_conversion_rate

        if period == "week":
            dict_with_sessions = self._extractSessionsPerPeriod(self.df_weekly, self._last_week_dates, "date",
                                                                purpose="count")
            dict_for_plot, overall_conversion_rate = self._countConversionRate(dict_with_sessions)

            plot = self.barPlot([str(key) for key in dict_for_plot.keys()][::-1], list(dict_for_plot.values())[::-1],
                                title="")
            return plot, overall_conversion_rate

    def main(self):
        df = self.df
        print(df.head())
        print(df.iloc[1, 6])


if __name__ == "__main__":
    plot, val = Processing().countSessions(period="week")
    print(val)
    plot.show()
    # plot, val = Processing().countSessions(period="week")
    # print(val)
    # plot.show()
    # Processing().timeToMakeAPostRequest(period="day")
    # plt, average_time = Processing().timeToMakeAPostRequest(period="week")
    # print(average_time)
    # plt.show()

# TODO
# 1)Amount of people for today
