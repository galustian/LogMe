from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import mpld3
from datetime import date, datetime
import json
import random
from utils import read_log_only


app = Flask(__name__)

COLORS = ["red", "blue", "green", "yellow", "purple", "orange", "pink", "black", "brown", "grey"]
MAX_POINTS_IN_CHART = 180


def total_days_of_difference(from_date, to_date):
    total_days = (int(to_date[2]) - int(from_date[2])) * 365
    total_days += (int(to_date[1]) - int(from_date[1])) * 30
    total_days += int(to_date[0]) - int(from_date[0])
    return total_days


def get_days_dict_from_years_log(logs, from_date, to_date):
    from_month = int(from_date[1])
    from_day = int(from_date[0])
    
    to_month = int(to_date[1])
    to_day = int(to_date[0])
    
    days = {}

    # log_y is the log of an entire year to be partially included
    for log_y in logs:
        for log_d in log_y:
            log_date = log_d.split("-")
            log_day = log_date[0]
            log_month = log_date[1]

            if from_month < log_month < to_month:
                days[log_d] = log_y[log_d]
            elif log_month == from_month:
                if log_day >= from_day:
                    days[log_d] = log_y[log_d]
            elif log_month == to_month:
                if log_day <= to_day:
                    days[log_d] = log_y[log_d]
    
    return days


def increment_date(from_day, from_month, from_year):
    if from_day < 31:
        from_day += 1
    elif from_month < 12:
        from_month += 1
        from_day = 1
    else:
        from_year += 1
        from_month = 1
        from_day = 1
    
    return from_day, from_month, from_year


def get_available_dates_in_ordered_list(days, from_date, to_date):
    from_year = int(from_date[2])
    from_month = int(from_date[1])
    from_day = int(from_date[0])
    
    to_year = int(to_date[2])
    to_month = int(to_date[1])
    to_day = int(to_date[0])

    days_list = []

    # while from_date does not exceed to_date START
    while from_year <= to_year:
        if from_year == to_year and from_month > to_month:
            break
        if from_year == to_year and from_month == to_month and from_day > to_day:
            break
        # while from_date does not exceed to_date END

        date_str = '{}-{}-{}'.format(from_day, from_month, from_year)
        while date_str not in days:
            from_day, from_month, from_year = increment_date(from_day, from_month, from_year)
            date_str = '{}-{}-{}'.format(from_day, from_month, from_year)
        
        days_list.append(date_str)
        from_day, from_month, from_year = increment_date(from_day, from_month, from_year)

    return days_list


def get_all_app_names():
    app_names_list = []
    with open('app_names.json') as f:
        app_names_dict = json.load(f)
    for key in app_names_dict:
        app_names_list.append(app_names_dict[key])

    return app_names_list


def get_n_days_avg(days, n_days, from_date, to_date):
    from_to_dates_list = get_available_dates_in_ordered_list(days, from_date, to_date)

    app_names_list = get_all_app_names()

    avg_days = {}

    # create avg_day and append to avg_days
    for n in range(0, len(from_to_dates_list), n_days):
        n_days_list = []

        # append n_days to list
        for i in range(n_days):
            day = days[from_to_dates_list[n+i]]

            # if app not used that day, create its dict entry with 0
            for app_name in app_names_list:
                if app_name not in day:
                    day[app_name] = 0

            n_days_list.append(day)

        # create average day
        avg_day = {}
        # init avg_day dict
        for app_name in app_names_list:
            avg_day[app_name] = 0

        for i in range(n_days):
            for app_name in app_names_list:
                avg_day[app_name] += n_days_list[i][app_name] / n_days

        avg_days[from_to_dates_list[n+n_days]] = avg_day

    return avg_days


'''
@app.route('/pie/<years>', methods=['GET', 'POST'])
def pie_chart(years):
    pass
'''


def create_date_obj(date_str):
    date = date_str.split('-')
    return date(int(date[2]), int(date[1]), int(date[0]))


# format: 21_01_2018-16_09_2018
@app.route('/<date_range>', methods=['GET', 'POST'])
def homepage(date_range):
    dates = date_range.split('-')
    from_date = dates[0].split('_')
    to_date = dates[1].split('_')
    
    total_days = total_days_of_difference(from_date, to_date)
    n_days_avg_per_point = round(total_days / MAX_POINTS_IN_CHART)

    logs = {}
    years_list = [y for y in range(int(from_date[2]), int(to_date[2]) + 1)]
    for y in years_list:
        logs[y] = read_log_only(year=y)
    
    days = get_days_dict_from_years_log(logs, from_date, to_date)
    days_avg = get_n_days_avg(days, n_days_avg_per_point, from_date, to_date)

    fig = plt.figure()

    app_names_list = get_all_app_names()

    for app_name in app_names_list:

        date_obj_list = []
        hours_list = []

        for date_str in days_avg:
            date_obj_list.append(create_date_obj(date_str))
            hours_list.append(days_avg[date_str][app_name])

        plt.plot_date(date_obj_list, hours_list, color=random.choice(COLORS), label=app_name, linestyle='-')

    plt.xlabel('Date')
    plt.ylabel('Hours')
    plt.legend()

    graph = mpld3.fig_to_html(fig)

    return render_template('index.html', html_graph=graph)


if __name__ == '__main__':
    app.run(debug=True, port=5000)