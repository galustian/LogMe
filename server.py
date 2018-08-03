from flask import Flask, request, render_template, abort
import matplotlib.pyplot as plt
import mpld3
import os
import datetime
import json
from multiprocessing import Process
from utils import read_log_only
from logger import log_active_app_per_second


app = Flask(__name__)

MAX_POINTS_IN_BAR_CHART = 15


def number_of_logged_days(from_date, to_date):
    days = get_days_dict(from_date, to_date)
    return len(days)


def get_days_dict(from_date, to_date):
    logs = get_years_logs(int(from_date[2]), int(to_date[2]))

    days = {}

    # logs[log_y] is the log of an entire year to be partially included
    for log_y in logs:
        for log_date in logs[log_y]:
            from_year = int(from_date[2])
            from_month = int(from_date[1])
            from_day = int(from_date[0])
    
            to_year = int(to_date[2])
            to_month = int(to_date[1])
            to_day = int(to_date[0])

            log_day = int(log_date.split("-")[0])
            log_month = int(log_date.split("-")[1])
            
            if log_y > from_year:
                from_day = 1
                from_month = 1

            if from_month < log_month < to_month and log_y <= to_year:
                days[log_date] = logs[log_y][log_date]
            elif log_month == from_month and log_y <= to_year:
                if log_day >= from_day:
                    days[log_date] = logs[log_y][log_date]
            elif log_month == to_month and log_y <= to_year:
                if log_day <= to_day:
                    days[log_date] = logs[log_y][log_date]
    
    return days


def increment_date(from_day, from_month, from_year):
    if from_day < 31:
        from_day += 1
    else:
        from_day = 1
        from_month += 1
    
    if from_month > 12:
        from_month = 1
        from_day = 1
        from_year += 1
    
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

            if from_year == to_year and from_month > to_month:
                return days_list
            if from_year == to_year and from_month == to_month and from_day > to_day:
                return days_list

            date_str = '{}-{}-{}'.format(from_day, from_month, from_year)

        days_list.append(date_str)
        from_day, from_month, from_year = increment_date(from_day, from_month, from_year)

    return days_list


def get_all_app_names():
    app_names_list = []
    with open('app_names.json') as f:
        app_names_dict = json.load(f)
    for key in app_names_dict:
        if app_names_dict[key] not in app_names_list:
            app_names_list.append(app_names_dict[key])

    app_names_list.append('other')

    return app_names_list


def get_app_colors_dict():
    with open('app_colors.json') as f:
        colors_dict = json.load(f)
    return colors_dict


def get_n_days_avg(days, n_days, from_date, to_date):
    from_to_dates_list = get_available_dates_in_ordered_list(days, from_date, to_date)
    app_names_list = get_all_app_names()

    avg_days = {}

    # create avg_day and append to avg_days
    for n in range(0, len(from_to_dates_list), n_days):
        n_days_list = []
        # remaining days smaller than n_days (for the average)
        remaining_days = False
        if len(from_to_dates_list) - n < n_days:
            n_days = len(from_to_dates_list) - n
            remaining_days = True

        # append n_days to list (for average)
        for i in range(n_days):
            day = days[from_to_dates_list[n+i]]
            # if app not used that day, create its dict entry with 0
            for app_name in app_names_list:
                if app_name not in day:
                    day[app_name] = 0

            n_days_list.append(day)

        # create average day
        avg_day = {}
        for app_name in app_names_list:
            avg_day[app_name] = 0

        for i in range(n_days):
            for app_name in app_names_list:
                avg_day[app_name] += n_days_list[i][app_name] / n_days

        avg_days[from_to_dates_list[n+n_days-1]] = avg_day

        if remaining_days:
            break

    return avg_days


def create_date_obj(date_str):
    date = date_str.split('-')
    return datetime.date(int(date[2]), int(date[1]), int(date[0]))


def get_years_logs(from_year, to_year):
    logs = {}
    years_list = [y for y in range(from_year, to_year + 1)]
    for y in years_list:
        if os.path.isfile('logs/log-{}.json'.format(y)):
            logs[y] = read_log_only(year=y)

    return logs


def create_graph(days_avg):
    app_names_list = get_all_app_names()
    app_colors_dict = get_app_colors_dict()

    for i, app_name in enumerate(app_names_list):
        date_obj_list = []
        hours_list = []

        for date_str in days_avg:
            date_obj_list.append(create_date_obj(date_str))
            hours_list.append(days_avg[date_str][app_name] / 3600)
        plt.plot_date(date_obj_list, hours_list, color=app_colors_dict[app_name], label=app_name, markeredgewidth=0, linestyle='-', lw=3)

    plt.xlabel('Date')
    plt.ylabel('Hours')
    plt.legend()


def create_bar(days_avg):
    app_names_list = get_all_app_names()
    app_colors_dict = get_app_colors_dict()

    for i, app_name in enumerate(app_names_list):
        date_str_list = []
        hours_list = []

        for date_str in days_avg:
            date_str_list.append(date_str)
            hours_list.append(days_avg[date_str][app_name] / 3600)

        plt.bar(range(len(date_str_list)), hours_list, color=app_colors_dict[app_name], label=app_name, width=0.4, align='center')
        plt.xticks(range(len(date_str_list)), date_str_list)
        # ax = plt.gca()
        # ax.xaxis_date()

    plt.xlabel('Date')
    plt.ylabel('Hours')
    plt.legend()


def create_pie(days_avg):
    app_names_list = get_all_app_names()
    app_colors_dict = get_app_colors_dict()

    hours_sum_list = []
    zero_hours_delete_index = []
    for i, app_name in enumerate(app_names_list):
        hours_sum = 0
        for date_str in days_avg:
            hours_sum += days_avg[date_str][app_name] / 3600

        if hours_sum == 0.0:
            zero_hours_delete_index.append(i)
            continue
        hours_sum_list.append(hours_sum)

    for index in sorted(zero_hours_delete_index, reverse=True):
        del app_names_list[index]

    colors_list = [app_colors_dict[app_name] for app_name in app_names_list]
    plt.pie(hours_sum_list, labels=app_names_list, colors=colors_list, autopct='%1.1f%%')


# date format: 21_01_2018
@app.route('/', methods=['GET'])
def homepage():
    from_date = None
    to_date = None
    max_points_in_chart = None
    
    if 'start-date' not in request.args or 'end-date' not in request.args or 'max-datapoints' not in request.args:
        now = datetime.datetime.now()
        from_date = [now.day, now.month, now.year-1]
        to_date = [now.day, now.month, now.year]
        max_points_in_chart = MAX_POINTS_IN_BAR_CHART * 10
    else:
        from_date = request.args['start-date'].split('_')
        to_date = request.args['end-date'].split('_')
        max_points_in_chart = int(request.args['max-datapoints'])
        # Validate date
        if len(from_date) != 3 or len(to_date) != 3:
            abort(404)
      
    # For Graph and Bar-Chart, set average days per point
    total_days = number_of_logged_days(from_date, to_date)
    n_days_avg_per_point = round(total_days / max_points_in_chart)
    if n_days_avg_per_point == 0:
        n_days_avg_per_point = 1

    days = get_days_dict(from_date, to_date)
    days_avg = get_n_days_avg(days, n_days_avg_per_point, from_date, to_date)

    graph_fig = plt.figure(figsize=(12, 8))
    create_graph(days_avg)

    pie_fig = plt.figure(figsize=(12, 8))
    create_pie(days_avg)

    bar_fig = plt.figure(figsize=(12, 8))
    # Set at most 15 bars START
    if max_points_in_chart > MAX_POINTS_IN_BAR_CHART:
        n_days_avg_per_point = round(total_days / MAX_POINTS_IN_BAR_CHART)
        if n_days_avg_per_point == 0:
            n_days_avg_per_point = 1
        days_avg = get_n_days_avg(days, n_days_avg_per_point, from_date, to_date)
    # Set at most 15 bars END
    create_bar(days_avg)

    graph = mpld3.fig_to_html(graph_fig)
    pie = mpld3.fig_to_html(pie_fig)
    bar = mpld3.fig_to_html(bar_fig)

    template_args = {
        'html_graph': graph,
        'html_pie': pie,
        'html_bar': bar,
        'start_date': '_'.join([str(d) for d in from_date]),
        'end_date': '_'.join([str(d) for d in to_date]),
        'max_points': max_points_in_chart
    }
    return render_template('index.html', **template_args)


if __name__ == '__main__':
    p1 = Process(target=log_active_app_per_second)
    p1.start()
    app.run(debug=True, port=5000)
    p1.join()

