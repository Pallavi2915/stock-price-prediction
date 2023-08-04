# Importing flask module in the project is mandatory
# An object of Flask class is our WSGI application.
from flask import Flask, render_template, request, send_from_directory
import utils
import train_models as tm
import os
import pandas as pd

from metrics import Processor
from flask import Flask, render_template, request, send_from_directory
import utils
import train_models as tm
import os
import pandas as pd
from random import randint
from flask import Flask, render_template,request,make_response
from metrics import Processor
import json  #json request
import mysql.connector
from mysql.connector import Error
from random import randint
import random
# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)
#
# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                           'favicon.ico',mimetype='image/vnd.microsoft.icon')


def perform_training(stock_name, df, models_list):
    all_colors = {'SVR_linear': '#FF9EDD',
                  
                  'SVR_rbf': '#FFA646',
                  'linear_regression': '#CC2A1E',
                  'random_forests': '#8F0099',
                  'KNN': '#CCAB43',
                  
                  'DT': '#85CC43',
                  }

    print(df.head())
    dates, prices, ml_models_outputs, prediction_date, test_price = tm.train_predict_plot(stock_name, df, models_list)
    origdates = dates
    if len(dates) > 20:
        dates = dates[-20:]
        prices = prices[-20:]

    all_data = []
    all_data.append((prices, 'false', 'Data', '#000000'))
    for model_output in ml_models_outputs:
        if len(origdates) > 20:
            all_data.append(
                (((ml_models_outputs[model_output])[0])[-20:], "true", model_output, all_colors[model_output]))
        else:
            all_data.append(
                (((ml_models_outputs[model_output])[0]), "true", model_output, all_colors[model_output]))

    all_prediction_data = []
    all_test_evaluations = []
    all_prediction_data.append(("Original", test_price))
    for model_output in ml_models_outputs:
        all_prediction_data.append((model_output, (ml_models_outputs[model_output])[1]))
        all_test_evaluations.append((model_output, (ml_models_outputs[model_output])[2]))

    return all_prediction_data, all_prediction_data, prediction_date, dates, all_data, all_data, all_test_evaluations

all_files = utils.read_all_stock_files('TataMotor_stocks_22-23')
# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
# ‘/’ URL is bound with hello_world() function.
def landing_function():
    # all_files = utils.read_all_stock_files('TataMotor_stocks_22-23')
    # df = all_files['A']
    # # df = pd.read_csv('GOOG_30_days.csv')
    # all_prediction_data, all_prediction_data, prediction_date, dates, all_data, all_data = perform_training('A', df, ['SVR_linear'])
    stock_files = list(all_files.keys())
    print('loaded')

    return render_template('index.html',show_results="false", stocklen=len(stock_files), stock_files=stock_files, len2=len([]),
                           all_prediction_data=[],
                           prediction_date="", dates=[], all_data=[], len=len([]))




@app.route('/gendata', methods=['POST','GET'])
def gendata():
    dataval=Processor.dataload()
    if dataval=="true":            
        stock_name = request.args['stockname']
        print('------------ddd-----------------')
        print(stock_name)
        from datetime import date
        from nsepy import get_history
        import pandas as pd

        todays_date = date.today()
        #sym=input("Enter the symbol :")
        sbin = get_history(symbol=stock_name, start=date(2022,1,1), end=date(todays_date.year,todays_date.month,todays_date.day))
        print(todays_date.year)
        print(todays_date.month)
        print(todays_date.day)
        print(type(sbin))
        print(sbin)
        sbin = pd.DataFrame(sbin)
        #sbin.drop(['Series','Prev Close','Last','VWAP','Turnover','Trades','Deliverable Volume','%Deliverble'], axis = 1)
        sbin.drop(sbin.columns[[1,2,6,8,10,11,12,13]], axis = 1, inplace = True)
        print(sbin)
        sbin = sbin[['Open','High','Low','Close','Volume','Symbol']]
        sbin = sbin.rename(columns = {'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Volume': 'volume', 'Symbol': 'Name','Date':'date'}, inplace = False)
        sbin.index.names = ['date']
        print(sbin)
        print(type(sbin))
        sbin.to_csv('./TataMotor_stocks_22-23/'+str(stock_name)+'_data.csv')
        #sbin.to_csv('./Stock-Prices-ML-Dashboard\TataMotor_stocks_22-23/NSE_data.csv')
        print("Data Saved")
        msg="Success"
        resp = make_response(json.dumps(msg))
        return resp




@app.route('/process', methods=['POST'])
def process():

    stock_file_name = request.form['stockfile']
    ml_algoritms = request.form.getlist('mlalgos')

    # all_files = utils.read_all_stock_files('TataMotor_stocks_22-23')
    df = all_files[str(stock_file_name)]
    # df = pd.read_csv('TataMotor_stocks_22-23')
    all_prediction_data, all_prediction_data, prediction_date, dates, all_data, all_data, all_test_evaluations = perform_training(str(stock_file_name), df, ml_algoritms)
    stock_files = list(all_files.keys())
    print(all_prediction_data)
    
    print(all_prediction_data[len(all_prediction_data)-1][1])
    print(all_prediction_data[len(all_prediction_data)-2][1])
    trend="Neutral"
    diff=all_prediction_data[len(all_prediction_data)-2][1]-all_prediction_data[len(all_prediction_data)-1][1]
    if(diff<=1):
        trend="High"
    else:
        trend="Low"
    diff=diff*-1
    return render_template('index.html',all_test_evaluations=all_test_evaluations, show_results="true", stocklen=len(stock_files), stock_files=stock_files,
                           len2=len(all_prediction_data),
                           all_prediction_data=all_prediction_data,
                           prediction_date=prediction_date, dates=dates, all_data=all_data, len=len(all_data),val1=Processor.accuracy_score("Original"),
                           val2=Processor.accuracy_score("ML"),trend=trend,pre=Processor.accuracy_score("ML"),recal=Processor.accuracy_score("ML"),f1=Processor.accuracy_score("ML"),diff=diff)

# 




# main driver function
if __name__ == '__main__':
    # run() method of Flask class runs the application
    # on the local development server.
    app.run(debug=True)
