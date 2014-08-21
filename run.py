import os
import re
from random import sample
from os import listdir
from os.path import isfile, join
from itertools import combinations
from werkzeug.utils import secure_filename
import numpy as np

from db import MongoInstance

from flask import Flask, render_template, redirect, url_for, request, make_response, json
from flask.ext.restful import Resource, Api, reqparse

from server.data import *
from server.DAL import DAL
from server.utility import *

PORT = 8888

app = Flask(__name__, static_path='/static')
api = Api(app)

TEST_DATA_FOLDER = os.path.join(os.curdir, 'test_data')
app.config['TEST_DATA_FOLDER'] = TEST_DATA_FOLDER

UPLOAD_FOLDER = os.path.join(os.curdir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['txt', 'csv', 'tsv'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Only one server-side route due to AngularJS SPA Routing
@app.route('/')
def main():
    return render_template('/main.html')


# File upload handler
uploadFileParser = reqparse.RequestParser()
uploadFileParser.add_argument('pID', type=str, required=True)
# uploadFileParser.add_argument('content_type', type=str, action='append', required=True)
# uploadFileParser.add_argument('content_data', type=str, action='append', required=True)
class UploadFile(Resource):
    # Dataflow: 
    # 1. Save file in uploads/pID directory
    # 2. Save file location in project data collection
    # 3. Return sample
    def post(self):
        # TODO Require these parameters
        pID = request.form.get('pID')
        file = request.files.get('file')
        if file and allowed_file(file.filename):

            # Save file
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], pID, filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], pID, filename))

            # Get sample data
            sample, rows, cols, extension, header = get_sample_data(path)

            # Make response
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
        return json.jsonify({'status': "Upload failed"})

        

api.add_resource(UploadFile, '/api/upload')


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


############################
# Projects
############################
projectGetParser = reqparse.RequestParser()
projectGetParser.add_argument('pID', type=str, default='')
projectGetParser.add_argument('user_name', type=str, required=True)

projectPostParser = reqparse.RequestParser()
projectPostParser.add_argument('title', type=str, required=True)
projectPostParser.add_argument('description', type=str, required=True)
projectPostParser.add_argument('user_name', type=str, required=True)

projectDeleteParser = reqparse.RequestParser()

# TODO Return all projects
# Get information for one project
class Project(Resource):
    def get(self):
        args = projectGetParser.parse_args()
        pID = args.get('pID')
        user_name = args.get('user_name')
        print "GET", pID, user_name

        return MongoInstance.getProject(pID, user_name)

    # Create project, initialize directories and collections
    def post(self):
        args = projectPostParser.parse_args()
        title = args.get('title')
        description = args.get('description')
        user_name = args.get('user_name')

        result = MongoInstance.postProject(title, description, user_name)

        # If successful project creation
        if result[1] is 200:
            # Create data upload directory
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], result[0]['pID']))

        return result
        
    # Delete project and all associated data
    def delete(self):
        args = projectDeleteParser.parse_args()
        pIDs = args.get('pID')
        return [ MongoInstance.deleteThing(pID, 'projects', []) for pID in pIDs]
    # The way that angular does http requests is slightly different than in python (or maybe it's a CORS thing)
    # Either way, we need this options to return the following access-control-allow-methods, otherwise delete wasn't working.
    # Will likely have to include for all classes
    def options (self): 
        return {'Allow' : 'PUT, GET, POST, DELETE' }, 200, \
        { 'Access-Control-Allow-Origin': '*', \
          'Access-Control-Allow-Methods' : 'PUT,GET, POST, DELETE' }

api.add_resource(Project, '/api/project')

############################
# Users
############################
userGetParser = reqparse.RequestParser()
userGetParser.add_argument('user_data', type=str, required=True)

userPutParser = reqparse.RequestParser()
userPutParser.add_argument('uID', type=str, action='append', required=True)
userPutParser.add_argument('user_data', type=str, action='append', required=True)
userPutParser.add_argument('pID', type=str, required=True)

userPostParser = reqparse.RequestParser()
userPostParser.add_argument('user_data', type=str, required=True)

userDeleteParser = reqparse.RequestParser()
userDeleteParser.add_argument('uID', type=str, action='append', required=True)
userDeleteParser.add_argument('pID', type=str, required=True)


class User(Resource):
    # Currently used for logging in (maybe should have its own endpoint)
    def get(self):
        args = userGetParser.parse_args()
        user_data = args.get('user_data')
        print "GET", user_data

        return MongoInstance.getThing('', 'users', user_data)
    def put(self):
        args = userPutParser.parse_args()
        uIDs = args.get('uID')
        user_datas = args.get('user_data')
        pID = args.get('pID')
        return MongoInstance.postThing(pID, 'users', uIDs=uIDS, user_data=user_datas)
    def post(self):
        args = userPostParser.parse_args()
        user_data = args.get('user_data')

        return MongoInstance.postThing('', 'users', user_data=user_data)
    def delete(self):
        args = userDeleteParser.parse_args()
        uIDs = args.get('uID')
        pID = args.get('pID')
        return MongoInstance.deleteThing(pID, 'users', uIDs)

api.add_resource(User, '/api/user')

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
        # print result
        for r in result:
            print r, r['count']
        return {'result': result}

# TODO Break this up!!!
vizFromOntParser = reqparse.RequestParser()
# vizFromOntParser.add_argument('network', type=str, required=True)
class get_visualizations_from_ontology(Resource):
    def post(self):
        visualizations = {
            "treemap": [],
            "geomap": [],
            "barchart": [],
            "scatterplot": [],
            "linechart": [],
            "network": []
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

        # TODO: Detect if an entity is likely geographic

        # LINE CHART

        # TREEMAP
        # CONDITION -> QUERY -> N * GROUP BY
        for node in nodes:
            dataset_id = node['model']

            # Must be a first-order object
            if numOutwardOneToManys[dataset_id]:
                attrs = node['attrs']

                for attrA, attrB in combinations(attrs, 2):
                    unique_A = node['unique_cols'][attrs.index(attrA)]
                    unique_B = node['unique_cols'][attrs.index(attrB)]
                    type_A = attrA['type']
                    type_B = attrB['type']
                    column_idA = attrA['column_id']
                    column_idB = attrB['column_id']
                    name_A = attrA['name']
                    name_B = attrB['name']

                    column_relnA = edge_to_type_dict.get(tuple([dataset_id, column_idA]))
                    column_relnB = edge_to_type_dict.get(tuple([dataset_id, column_idB]))

                    # Ensure that the condition and grouping attributes map to second-order objects
                    # Ensure that the conditioning and grouping variables are not floats
                    # (do we want to do this???)
                    print name_A, column_relnA
                    if (not column_relnA) and (not unique_A) and (type_A != 'float') and (type_B != 'float') and (type_B != 'int'):
                        treemap_spec = {
                        'condition': column_idA,
                        'aggregate': dataset_id,
                        'groupBy': column_idB,
                        }
                        visualizations['treemap'].append(treemap_spec)

                    if (not unique_A) and (name_B == 'countryCode3'):
                        geomap_spec = {
                            'condition': column_idA,
                            'aggregate': dataset_id,
                            'groupBy': column_idB,
                        }
                        visualizations['geomap'].append(geomap_spec)

        result = {}
        for vizType, vizSpecs in visualizations.iteritems():
            if vizSpecs:
                result[vizType] = vizSpecs


        json_data = json.jsonify({
                                'status': "success",
                                'visualizations': result,
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

# Other end-points
# POST Dataset changes
# POST Ontology changes
# POST Visualization Selections


api.add_resource(get_test_datasets, '/get_test_datasets')
api.add_resource(get_relationships, '/get_relationships')
api.add_resource(get_visualizations_from_ontology, '/get_visualizations_from_ontology')
api.add_resource(tag_data, '/tag')

# Visualization Endpoints
api.add_resource(get_treemap_data, '/get_treemap_data')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=PORT)
