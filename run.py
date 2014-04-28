from flask import Flask, render_template, redirect, url_for, request, make_response, json

import os
import re
from random import sample
from os import listdir
from os.path import isfile, join
from itertools import combinations
from werkzeug.utils import secure_filename

from server.utility import *

# TODO Get this working
# from flask.ext.scss import Scss
# from flask_cake import Cake

TEST_DATA_FOLDER = os.path.join(os.curdir, 'test_data')
UPLOAD_FOLDER = os.path.join(os.curdir, 'uploads')
ALLOWED_EXTENSIONS = set(['csv'])


app = Flask(__name__, static_path='/static')
# cake = Cake()
# cake.init_app(app)
# Scss(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEST_DATA_FOLDER'] = TEST_DATA_FOLDER


@app.route('/')
def main():
    return render_template('/main.html')


# file upload handler
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('dataset')
    print request.data
    if file and allowed_file(file.filename):

        # save file
        filename = secure_filename(file.filename)
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # get sample data
        sample, rows, cols, extension, header  = get_sample_data(path)
        print header

        # make response
        json_data = json.jsonify({
                                'status': "success",
                                'filename': filename,
                                'header': header,
                                'sample': sample,
                                'rows': rows,
                                'cols': cols,
                                'type': extension,
                                })
        response = make_response(json_data)
        response.set_cookie('file', filename)
        return response

    return json.jsonify({'status': "upload failed"})


# TODO: Combine with previous function
@app.route('/get_test_datasets', methods=['GET'])
def get_test_datasets():
    test_dataset_samples = []
    filenames = [f for f in listdir(app.config['TEST_DATA_FOLDER']) if (isfile(join(app.config['TEST_DATA_FOLDER'], f)) and f[0] is not '.')]
    for filename in filenames:
        path = os.path.join(app.config['TEST_DATA_FOLDER'], filename)
        # make response
        sample, rows, cols, extension, header = get_sample_data(path)
        types = get_column_types(path)
        json_data = {
                        'filename': filename,
                        'header': header,
                        'sample': sample,
                        'rows': rows,
                        'cols': cols,
                        'filetype': extension,
                        'types': types
                    }
        test_dataset_samples.append(json_data)

    result = json.jsonify({'status': "success", 'samples': test_dataset_samples})
    return result


# Utility function to detect possible relationships between datasets
# TODO: Deal with header lines somehow
# TODO: use Pandas for this?
@app.route('/get_relationships', methods=['GET'])
def get_relationships():
    headers_dict = {}
    unique_columns_dict = {}
    paths = [os.path.join(app.config['TEST_DATA_FOLDER'], f) for f in listdir(app.config['TEST_DATA_FOLDER']) if (isfile(join(app.config['TEST_DATA_FOLDER'], f)) and f[0] is not '.')]

    # For each dataset, get unique values in all columns
    for path in paths:
        f = open(path)
        lines = f.readlines()

        # Sample file if it is too large
        # if len(lines) > 1000:
        #     lines = sample(lines, 1000)
        delim = get_delimiter(path)
        header, columns = read_file(path, delim)
        headers_dict[path] = header
        unique_columns_dict[path] = [get_unique(col) for col in columns]

    # Pairwise comparison of columns cross datasets
    for path1, path2 in combinations(paths, 2):
        print "---------------------------------"
        print path1.split('/')[-1], path2.split('/')[-1]
        print "---------------------------------"
        header1 = headers_dict[path1]
        header2 = headers_dict[path2]
        unique_columns1 = unique_columns_dict[path1]
        unique_columns2 = unique_columns_dict[path2]

        for i1, col1 in enumerate(unique_columns1):
            for i2, col2 in enumerate(unique_columns2):
                d = get_distance(col1, col2)
                if d:
                    print d, header1[i1], header2[i2]
    return


# Determine the probability that columns within a table are nested
@app.route('/get_nestedness', methods=['GET'])
def get_nestedness():
    return


@app.route('/tag', methods=['GET'])
def tag_data():
    filename = request.cookies.get('file')
    if filename:
        path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        return '''success'''
    return '''retrive failed'''


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
