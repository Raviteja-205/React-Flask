from flask import Flask
import sys
app = Flask(__name__, static_folder="../build", static_url_path='/')

@app.route('/')
def my_index():
    return "Received"

    
app.run(debug=True)