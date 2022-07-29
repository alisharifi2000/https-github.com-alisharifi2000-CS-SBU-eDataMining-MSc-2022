import json
from flask import Flask, request
import numpy as np
import pandas as pd
from utils.common import response_message, read_json_time_series
from utils.interpolation_methods import linear_interpolation, shamsi_linear_interpolation

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def isup():
    return response_message('API is active')


@app.route('/service1', methods=['GET', 'POST'])
def interpolation():
    req = request.get_json()
    data = read_json_time_series(req['data'])
    config = req['config']

    
    if config['type'] == 'miladi':
        result = linear_interpolation(data, config)
        result = result.to_json()

    if config['type'] == 'shamsi':
        result = shamsi_linear_interpolation(data, config)
        print(result)
        result = result.to_json(default_handler=str)

    return response_message(dict({"data": result}))

@app.route('/service2', methods=['POST'])
def data_convert_interpolation():
    req = request.get_json()
    config = req['config']
    j_data = json.dumps(req['data'])
    data = pd.read_json(j_data)
    data.time = pd.to_datetime(data.time, yearfirst=True)
    
    result = shamsi_linear_interpolation(data, config)
    result = result.to_json(default_handler=str)

    return response_message(dict({"data": result}))


@app.route('/service3', methods=['POST'])
def outlier():
    req = request.get_json()
    data = req['data']
    config = req['config']
    
    data = read_json_time_series(data)
    methods = config["methods"]
    columns = config["columns"]
    for method in methods:
        method = method.lower()
        if method == "z_score":
        
            
            for column in columns:
                mean_y = np.mean(data[column])
                stdev_y = np.std(data[column])
                for i in data.index:
                    y = data.loc[i, column]
                    z_scores = (y - mean_y) / stdev_y 
                    if abs(z_scores) > 1.5:
                        data.loc[i, "z_score_"+str(column)] = True
                    else:
                        data.loc[i, "z_score_"+str(column)] = False
    


    data = data.drop(columns=columns)
    data = data.to_json()


    return response_message(dict({"data": data}))

@app.route('/service4', methods=['POST'])
def service4():
    data = request.files["file"]
    jsonFile = json.load(data)
    data = jsonFile['data']
    file_data = open("data.json", 'w')
    data = str(data)
    data = data.replace("\'", "\"")
    file_data.write(data)
    file_data.close()
    f = open("data.json", 'r')
    config = jsonFile["config"]
    data = pd.read_json(f)
    data_new = sampling(data, config["method"])
    f = open("json_data.json", "w")
    f.write(data_new.to_json(orient='columns'))
    f.close()
    with open('json_data.json', 'r') as json_file:
        json_object = json.load(json_file)
    result = json.dumps(json_object, indent=1)
    with open("output.json", "w") as outfile:
        outfile.write(json.dumps(json_object, indent=1))
    with open("output.json", "r") as outfile:
        result = outfile.read()  
    result = result.replace('\n', '<br>')
    return response_message(dict({"data": result})) 


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081)
