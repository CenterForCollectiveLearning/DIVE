from flask import Flask, render_template, redirect, url_for, request, make_response, json

#file upload
import os
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

# function to get sample from data file
def get_sample_data(path):
    f = open(path)
    filename = path.rsplit('/')[-1]
    extension = filename.rsplit('.', 1)[1]
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

    return sample, rows, cols, extension

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
        sample, rows, cols, extension  = get_sample_data(path)

        # make response
        json_data = json.jsonify({
                                'status': "success",
                                'filename': filename,
                                'sample': sample,
                                'rows': rows,
                                'cols': cols,
                                'type': extension,
                                })
        response = make_response(json_data)
        response.set_cookie('file', filename)
        return response

    return json.jsonify({'status': "upload failed"})

@app.route('/get_test_datasets', methods=['GET'])
def get_test_datasets():
    test_dataset_samples = []
    filenames = [f for f in listdir(app.config['TEST_DATA_FOLDER']) if (isfile(join(app.config['TEST_DATA_FOLDER'], f)) and f[0] is not '.')]
    for filename in filenames:
        path = os.path.join(app.config['TEST_DATA_FOLDER'], filename)
        # make response
        sample, rows, cols, extension = get_sample_data(path)
        json_data = {
                        'filename': filename,
                        'sample': sample,
                        'rows': rows,
                        'cols': cols,
                        'type': extension,
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
