from flask import Flask, render_template, request

from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE

from alpha_vantage.timeseries import TimeSeries
import pandas as pd
import numpy as np

app = Flask(__name__)


def datetime(x):
    return np.array(x, dtype=np.datetime64)


def get_data(name):
    API_KEY = 'YPF546IZOMDCD9DD'
    ts = TimeSeries(key=API_KEY, output_format='pandas')
    data, meta_data = ts.get_intraday(
        symbol=name, interval='1min', outputsize='full')
    return data


def create_figure(mydata, name):
    p = figure(x_axis_type="datetime", title="Intraday Time Series for the %s stock (1 min)" %
               name, x_axis_label="Date", y_axis_label="Price")
    # p.varea(mydata.index.values, mydata['3. low'], mydata['2. high'], fill_alpha=0.5, color = 'blue')
    p.circle(mydata.index.values, mydata['1. open'],
             color='green', alpha=0.5, legend_label="Open", size=2)
    p.circle(mydata.index.values, mydata['4. close'],
             color='red', alpha=0.5, legend_label="Close", size=1)
    p.legend.location = "top_left"
    return p


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        stock_name = request.form.get('stock')
        stock_data = get_data(stock_name)
        stock_plot = create_figure(stock_data, stock_name)
    else:
        # init a basic bar chart:
        # http://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html#bars
        stock_plot = figure(plot_width=600, plot_height=600)
        stock_plot.vbar(
            x=[1, 2, 3, 4],
            width=0.5,
            bottom=0,
            top=[1.7, 2.2, 4.6, 3.9],
            color='navy'
        )

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(stock_plot)

    # # render template
    html = render_template(
        'result.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources
    )

    return html


if __name__ == '__main__':
    app.run(port=33507)
