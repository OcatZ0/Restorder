from flask import Flask
import os
from endpoint import endpoint

# Get the directory where the script is located
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__, 
            template_folder=os.path.join(basedir, 'templates'),
            static_folder=os.path.join(basedir, 'static'))

# Secret key for session management
app.secret_key = "TRPL-101-A4"

app.register_blueprint(endpoint)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)