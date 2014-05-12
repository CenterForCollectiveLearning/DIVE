from flask import Flask, render_template, redirect, url_for, request, make_response, json
from flask.ext.restful import Resource, Api, reqparse

import os
import re
from random import sample
from os import listdir
from os.path import isfile, join
from itertools import combinations
from werkzeug.utils import secure_filename
import numpy as np

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


@app.route('/')
def main():
    return render_template('/main.html')


# File upload handler
class upload_file(Resource):
    def get(self):
        file = request.files.get('dataset')
        if file and allowed_file(file.filename):

            # save file
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # get sample data
            sample, rows, cols, extension, header  = get_sample_data(path)

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
        test_dataset_samples = []
        filenames = [f for f in listdir(app.config['TEST_DATA_FOLDER']) if (isfile(join(app.config['TEST_DATA_FOLDER'], f)) and f[0] is not '.')]

        for filename in filenames:

            path = os.path.join(app.config['TEST_DATA_FOLDER'], filename)

            # TODO Don't try to insert a new one every time
            DAL.insert_dataset(path)
            dataset_id = DAL.get_dataset_id(path)
            column_ids = DAL.get_column_ids(path)

            header, columns = read_file(path)
            unique_cols = [detect_unique_list(col) for col in columns]

            # make response
            sample, rows, cols, extension, header = get_sample_data(path)
            types = get_column_types(path)

            column_attrs = [{'name': header[i], 'type': types[i], 'column_id': i} for i in column_ids]

            json_data = {
                            'dataset_id': dataset_id,
                            'column_ids': column_ids,
                            'column_attrs': column_attrs,
                            'unique_cols': unique_cols,
                            'filename': filename,
                            'sample': sample,
                            'title': filename,
                            'rows': rows,
                            'cols': cols,
                            'filetype': extension,
                        }

            test_dataset_samples.append(json_data)

        result = json.jsonify({'status': 'success', 'samples': test_dataset_samples})
        return result


treemapDataParser = reqparse.RequestParser()
treemapDataParser.add_argument('condition', type=int, required=True)
treemapDataParser.add_argument('aggregate', type=int, required=True)
treemapDataParser.add_argument('groupBy', type=int, required=True)
treemapDataParser.add_argument('query', type=str, required=True)
treemapDataParser.add_argument('aggFn', type=str, default='sum')
class get_treemap_data(Resource):
    def get(self):
        # Get and parse arguments
        args = treemapDataParser.parse_args()
        condition = args.get('condition')
        aggregate = args.get('aggregate')
        by = args.get('groupBy')
        by_id = by
        query = args.get('query').strip('[').strip(']').split(',')
        aggFn = args.get('aggFn')

        # Test
        # http://localhost:5000/get_treemap_data?condition=11&aggregate=2&by=14&query=[USA]
        path = DAL.get_path_from_id(aggregate)
        delim = get_delimiter(path)
        df = pd.read_table(path, sep=delim)

        by = DAL.get_column_name_from_id(aggregate, by)
        condition = DAL.get_column_name_from_id(aggregate, condition)

        if query[0] == '*':
            cond_df = df
        else:
            # Uses column indexing for now
            cond_df = df[df[condition].isin(query)]

        group_obj = cond_df.groupby(by)
        finalSeries = group_obj.size()

        result = []
        for row in finalSeries.iteritems():
            result.append({
                by_id: row[0],
                'count': np.asscalar(np.int16(row[1]))
            })
        print result
        return {'result': result}

vizFromOntParser = reqparse.RequestParser()
# vizFromOntParser.add_argument('network', type=str, required=True)
class get_visualizations_from_ontology(Resource):
    def post(self):
        visualizations = {
            "treemap": [],
            "geomap": [],
            "barchart": [],
            "scatterplot": []
        }

        # TODO Use regular argument parser
        network = json.loads(request.data)
        nodes = network['nodes']
        edges = network['edges']

        edge_to_type_dict = {}
        for edge in edges:
            source = edge['source']
            target = edge['target']
            type = edge['type']

            edge_to_type_dict[tuple(source)] = type
            edge_to_type_dict[tuple(target)] = type


        # SCATTERPLOT
        # ATTR vs ATTR, optional QUERY and GROUP
        # for node in nodes:
        #     attrs = node['attrs']
        #     for attrA, attrB in combinations(attrs, 2):
        #         # TODO Don't plot against unique columns
        #         if (attrA['type'] in ['int', 'float'] or attrB['type'] in ['int', 'float']):
        #             print attrA['name'], attrB['name']

        # TODO Detect redundant fields
        # Detect objects that are attributes of another (count one-to-many edges leading outward)
        numOutwardOneToManys = dict([(node['model'], 0) for node in nodes])
        for edge in edges:
            sourceDataset = edge['source'][0]
            targetDataset = edge['target'][0]
            type = edge['type']
            if type == '1N':
                numOutwardOneToManys[targetDataset] += 1
            if type == 'N1':
                numOutwardOneToManys[sourceDataset] += 1

        # TREEMAP
        # CONDITION -> QUERY -> N * GROUP BY
        for node in nodes:
            dataset_id = node['model']

            # Must be a first-order object
            if numOutwardOneToManys[dataset_id]:
                attrs = node['attrs']

                for attrA, attrB in combinations(attrs, 2):
                    column_idA = attrA['column_id']
                    column_idB = attrB['column_id']

                    column_relnA = edge_to_type_dict.get(tuple([dataset_id, column_idA]))
                    column_relnB = edge_to_type_dict.get(tuple([dataset_id, column_idB]))

                    # Ensure that the condition and grouping attributes map to second-order objects
                    # (do we want to do this???)
                    if column_relnA or column_relnB:
                        treemap_spec = {
                            'condition': column_idA,
                            'aggregate': dataset_id,
                            'groupBy': column_idB,
                        }
                        visualizations['treemap'].append(treemap_spec)

        json_data = json.jsonify({
                                'status': "success",
                                'visualizations': visualizations,
                                })
        response = make_response(json_data)
        return response

# Utility function to detect possible relationships between datasets
# TODO: Deal with header lines somehow
# TODO: use Pandas for this?
# TODO: CUT THIS DOWN
class get_relationships(Resource):
    def get(self):

        # Data Access
        filenames = [f for f in listdir(app.config['TEST_DATA_FOLDER']) if (isfile(join(app.config['TEST_DATA_FOLDER'], f)) and f[0] is not '.')]
        paths = [os.path.join(app.config['TEST_DATA_FOLDER'], f) for f in filenames]

        dataset_ids = {}
        column_ids = {}
        headers_dict = {}
        is_unique_dict = {}
        raw_columns_dict = {}
        unique_columns_dict = {}

        # For each dataset, get raw and unique values in all columns
        for path in paths:
            dataset_id = DAL.get_dataset_id(path)
            dataset_ids[path] = dataset_id
            column_ids[path] = DAL.get_column_ids(path)

            header, columns = read_file(path)

            headers_dict[dataset_id] = header
            raw_columns_dict[dataset_id] = [list(col) for col in columns]
            unique_columns_dict[dataset_id] = [get_unique(col) for col in columns]

            # List of booleans -- is a column composed of unique elements?
            is_unique_dict[dataset_id] = [detect_unique_list(col) for col in columns]

        overlaps = {}
        hierarchies = {}

        # Pairwise comparison of columns cross datasets
        for dataset_idA, dataset_idB in combinations(dataset_ids.values(), 2):
            raw_colsA = raw_columns_dict[dataset_idA]
            raw_colsB = raw_columns_dict[dataset_idB]
            unique_colsA = unique_columns_dict[dataset_idA]
            unique_colsB = unique_columns_dict[dataset_idB]

            overlaps['%s\t%s' % (dataset_idA, dataset_idB)] = {}
            hierarchies['%s\t%s' % (dataset_idA, dataset_idB)] = {}

            for indexA, colA in enumerate(raw_colsA):
                for indexB, colB in enumerate(raw_colsB):
                    h = get_hierarchy(colA, colB)
                    d = get_distance(colA, colB)
                    if d:
                        hierarchies['%s\t%s' % (dataset_idA, dataset_idB)]['%s\t%s' % (indexA, indexB)] = h

            for indexA, colA in enumerate(unique_colsA):
                for indexB, colB in enumerate(unique_colsB):
                    d = get_distance(colA, colB)
                    if d:
                        overlaps['%s\t%s' % (dataset_idA, dataset_idB)]['%s\t%s' % (indexA, indexB)] = d

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
api.add_resource(get_visualizations_from_ontology, '/get_visualizations_from_ontology')
api.add_resource(tag_data, '/tag')

# Visualization Endpoints
api.add_resource(get_treemap_data, '/get_treemap_data')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
