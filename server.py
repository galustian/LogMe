from flask import Flask, request, render_template
import matplotlib.pyplot as plt
import mpld3
from datetime import date, datetime
import json
from utils import read_log_only

app = Flask(__name__)

MAX_POINTS_IN_CHART = 180

'''
@app.route('/pie/<years>', methods=['GET', 'POST'])
def pie_chart(years):
    pass
'''


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


def get_available_days_in_ordered_list(days, from_date, to_date):
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


def get_n_days_avg(days, n_days_avg, from_date, to_date):
    avg_days = {}


# format: 21_01_2018-16_09_2018
@app.route('/<date_range>', methods=['GET', 'POST'])
def homepage(date_range):
    dates = date_range.split('-')

    from_date = dates[0].split('_')
    to_date = dates[1].split('_')
    
    total_days = total_days_of_difference(from_date, to_date)
    n_days_avg_per_point = round(total_days / MAX_POINTS_IN_CHART)

    years_list = [y for y in range(int(from_date[2]), int(to_date[2]) + 1)]
    
    logs = {}
    for y in years_list:
        logs[y] = read_log_only(year=y)
    
    days = get_days_dict_from_years_log(logs, from_date, to_date)
    days_avg = get_n_days_avg(days, n_days_avg_per_point, from_date, to_date)

    fig = plt.figure()
    '''
    da1 = date(2001, 2, 24)
    da2 = date(2001, 3, 25)
    da3 = date(2001, 4, 27)
  
    plt.plot_date([da1, da2, da3], [1, 3, 6], color='green', label='Terminal', linestyle='-')
    plt.plot_date([da1, da2, da3], [4, 1, 0], color='red', label='Visual Studio Code', linestyle='-')
    '''
    
    plt.xlabel('Date')
    plt.ylabel('Hours')
    plt.legend()

    graph = mpld3.fig_to_html(fig)

    return render_template('index.html', html_graph=graph)


if __name__ == '__main__':
    app.run(debug=True, port=5000)