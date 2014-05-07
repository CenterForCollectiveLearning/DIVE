from flask import Flask, render_template, redirect, url_for, request, make_response, json
from flask.ext.restful import Resource, Api, reqparse

import os
import re
from random import sample
from os import listdir
from os.path import isfile, join
from itertools import combinations
from werkzeug.utils import secure_filename

from server.data import DAL
from server.utility import *

# TODO Get this working
# from flask.ext.scss import Scss
# from flask_cake import Cake

TEST_DATA_FOLDER = os.path.join(os.curdir, 'test_data')
UPLOAD_FOLDER = os.path.join(os.curdir, 'uploads')
ALLOWED_EXTENSIONS = set(['csv'])


app = Flask(__name__, static_path='/static')
api = Api(app)
# cake = Cake()
# cake.init_app(app)
# Scss(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TEST_DATA_FOLDER'] = TEST_DATA_FOLDER


# TODO Abstract state into a class (see: State Pattern)
NUM_DATASETS = 0


@app.route('/')
def main():
    return render_template('/main.html')


# File upload handler
class upload_file(Resource):
    def get(self):
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
class get_test_datasets(Resource):
    def get(self):
        global NUM_DATASETS  # TODO Don't do this
        test_dataset_samples = []
        filenames = [f for f in listdir(app.config['TEST_DATA_FOLDER']) if (isfile(join(app.config['TEST_DATA_FOLDER'], f)) and f[0] is not '.')]
    
        for filename in filenames:
    
            path = os.path.join(app.config['TEST_DATA_FOLDER'], filename)
    
            canonical_form = get_canonical_form(path)
            canonical_index = NUM_DATASETS
            NUM_DATASETS += 1
    
            delim = get_delimiter(path)
            header, columns = read_file(path, delim)
            unique_cols = [detect_unique_list(col) for col in columns]
    
            # make response
            sample, rows, cols, extension, header = get_sample_data(path)
            types = get_column_types(path)
    
            json_data = {
                            '_id': canonical_index,
                            'canonical_form': canonical_form,
                            'unique_cols': unique_cols,
                            'filename': filename,
                            'header': header,
                            'sample': sample,
                            'rows': rows,
                            'cols': cols,
                            'filetype': extension,
                            'types': types
                        }
    
            test_dataset_samples.append(json_data)
    
        result = json.jsonify({'status': 'success', 'samples': test_dataset_samples})
        return result


treemapDataParser = reqparse.RequestParser()
treemapDataParser.add_argument('condition', type=str, required=True)
treemapDataParser.add_argument('aggregate', type=str, required=True)
treemapDataParser.add_argument('by', type=str, required=True)
treemapDataParser.add_argument('query', type=str, required=True)
treemapDataParser.add_argument('aggFn', type=str, default='sum')
class get_treemap_data(Resource):
    def get(self):

        # Get and parse arguments
        args = treemapDataParser.parse_args()
        condition = args.get('condition')
        aggregate = args.get('aggregate')
        by = args.get('by')
        query = args.get('query').strip('[').strip(']').split(',')
        aggFn = args.get('aggFn')

        # TODO
        # Create a generalized class to access this data
        # Use canonical forms

        # Test
        # http://localhost:5000/get_treemap_data?condition=countryName&aggregate=people.tsv&by=occupation&query=[USA]

        print condition, aggregate, by, query, aggFn
        path = os.path.join(app.config['TEST_DATA_FOLDER'], aggregate)
        delim = get_delimiter(path)

        df = pd.read_table(path, sep=delim)
        cond_df = df[df[condition].isin(query)]
        group_obj = cond_df.groupby(by)
        finalDf = group_obj.size()

        print finalDf
        return


# Utility function to detect possible relationships between datasets
# TODO: Deal with header lines somehow
# TODO: use Pandas for this?
class get_relationships(Resource):
    def get(self):
        headers_dict = {}
        is_unique_dict = {}
        raw_columns_dict = {}
        unique_columns_dict = {}
        filenames = [f for f in listdir(app.config['TEST_DATA_FOLDER']) if (isfile(join(app.config['TEST_DATA_FOLDER'], f)) and f[0] is not '.')]
        paths = [os.path.join(app.config['TEST_DATA_FOLDER'], f) for f in filenames]
    
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
            raw_columns_dict[path] = [list(col) for col in columns]
            unique_columns_dict[path] = [get_unique(col) for col in columns]
    
            # List of booleans -- is a column composed of unique elements?
            is_unique_dict[path] = [detect_unique_list(col) for col in columns]
    
        overlaps = {}
        hierarchies = {}
    
        # Pairwise comparison of columns cross datasets
        # TODO Make this not suck
        for pathA, pathB in combinations(paths, 2):
            fA, fB = pathA.split('/')[-1], pathB.split('/')[-1]
            headerA = headers_dict[pathA]
            headerB = headers_dict[pathB]
            raw_colsA = raw_columns_dict[pathA]
            raw_colsB = raw_columns_dict[pathB]
            unique_colsA = unique_columns_dict[pathA]
            unique_colsB = unique_columns_dict[pathB]
    
            overlaps['%s\t%s' % (fA, fB)] = {}
            hierarchies['%s\t%s' % (fA, fB)] = {}
    
            for indexA, colA in enumerate(raw_colsA):
                for indexB, colB in enumerate(raw_colsB):
                    h1, h2 = headerA[indexA], headerB[indexB]
                    d = get_distance(colA, colB)
                    h = get_hierarchy(colA, colB)
                    if d:
                        hierarchies['%s\t%s' % (fA, fB)]['%s\t%s' % (h1, h2)] = h
    
            for indexA, colA in enumerate(unique_colsA):
                for indexB, colB in enumerate(unique_colsB):
                    h1, h2 = headerA[indexA], headerB[indexB]
                    d = get_distance(colA, colB)
                    h = get_hierarchy(colA, colB)
                    if d:
                        overlaps['%s\t%s' % (fA, fB)]['%s\t%s' % (h1, h2)] = d
    
        return json.jsonify({'overlaps': overlaps, 'hierarchies': hierarchies})


class tag_data(Resource):
    def get(self):
        filename = request.cookies.get('file')
        if filename:
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            return '''success'''
        return '''retrive failed'''


api.add_resource(upload_file, '/upload')
api.add_resource(get_test_datasets, '/get_test_datasets')
api.add_resource(get_relationships, '/get_relationships')
api.add_resource(tag_data, '/tag')

# Visualization Endpoints
api.add_resource(get_treemap_data, '/get_treemap_data')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
