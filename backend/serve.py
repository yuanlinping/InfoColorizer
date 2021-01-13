from flask_cors import CORS
from flask import Flask, send_file, request, jsonify, render_template, send_from_directory, Response
from ProcessImage import process_image_api

import json

app = Flask(__name__)
cors = CORS(app)

app.register_blueprint(process_image_api)

# ################################################################################ route

if __name__ == '__main__':
    app.run(debug=True)
