from flask import Flask, make_response,render_template, request
import io
from io import StringIO
import csv
import pandas as pd
import numpy as np
import pickle

app = Flask(__name__)

def transform(text_file_contents):
    return text_file_contents.replace("=", ",")
    

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == "POST":
      f = request.files['data_file']
      if not f:
          return "No file"

      stream = io.StringIO(f.stream.read().decode("UTF8"), newline=None)
      csv_input = csv.reader(stream)
      #print("file contents: ", file_contents)
      #print(type(file_contents))
      #print(csv_input)
      #for row in csv_input:
      #    print(row)

      stream.seek(0)
      result = transform(stream.read())

      df = pd.read_csv(StringIO(result))
    
      pmap = {'icmp':0,'tcp':1,'udp':2}
      df['protocol_type'] =df['protocol_type'].map(pmap)

      fmap = {'SF':0,'S0':1,'REJ':2,'RSTR':3,'RSTO':4,'SH':5 ,'S1':6 ,'S2':7,'RSTOS0':8,'S3':9 ,'OTH':10}
      df['flag'] =df['flag'].map(fmap)

      df.drop('service',axis = 1,inplace= True)
      df = df.drop(['label',], axis=1)
    

      # load the model from disk
      loaded_model = pickle.load(open('model1.pkl', 'rb'))
      df['prediction'] = loaded_model.predict(df)
      print(df['prediction'])

      response = make_response(df['prediction'].to_csv())
      response.headers["Content-Disposition"] = "attachment; filename=result.csv"
       # return render_template('index.html')
      return response
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)