from flask import Flask, render_template, redirect, url_for, request, make_response, json

#file upload
import os
import re
from os import listdir
from os.path import isfile, join
from werkzeug.utils import secure_filename

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

# function to filter uploaded files
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

INT_REGEX = "^-?[0-9]+$"
FLOAT_REGEX = "[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?"


# Utility function to get the type of a variable
# TODO: Parse dates
def get_variable_type(v):
    if re.match(INT_REGEX, v): r = "int"
    elif re.match(FLOAT_REGEX, v): r = "float"
    else: r = "str"
    return r

# Utility function to get a list of column types in a dataset given a file path
# TODO Check if header
# TODO Use some scheme of parsing such that they aren't all strings
def get_column_types(path):
    f = open(path)
    header = f.readline()
    sample_line = f.readline()
    extension = path.rsplit('.', 1)[1]
    if extension == 'csv':
      delim = ','
    elif extension == 'tsv':
      delim = '\t'

    types = [get_variable_type(v) for v in sample_line.split(delim)]
    return types

# function to get sample from data file
def get_sample_data(path):
    f = open(path)
    filename = path.rsplit('/')[-1]
    extension = filename.rsplit('.', 1)[1]
    header = f.readline()
    rows = 0
    cols = 0

    sample = {}
    for i in range(5):
        line = f.readline()
        if not line:
            break
        else:
            if extension == 'csv':
              delim = ','
            elif extension == 'tsv':
              delim = '\t'

            sample[i] = [item.strip() for item in line.split(delim)]
            cols = max(cols, len(sample[i]))

    with open(path) as f:
        for rows, l in enumerate(f):
            pass
    rows += 1

    # Parse header
    header = header.split(delim)

    return sample, rows, cols, extension, header

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
