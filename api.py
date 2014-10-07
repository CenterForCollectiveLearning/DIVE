import os
import re
import json
from random import sample
from os import listdir
from os.path import isfile, join
from itertools import combinations
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import numpy as np
import pandas as pd

from db import MongoInstance as MI

from flask import Flask, render_template, redirect, url_for, request, make_response, json
from flask.ext.restful import Resource, Api, reqparse

from server.data import *
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

@app.before_request
def option_autoreply():
    """ Always reply 200 on OPTIONS request """

    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()

        headers = None
        if 'ACCESS_CONTROL_REQUEST_HEADERS' in request.headers:
            headers = request.headers['ACCESS_CONTROL_REQUEST_HEADERS']

        h = resp.headers

        # Allow the origin which made the XHR
        print request.headers
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
        # Allow the actual method
        h['Access-Control-Allow-Methods'] = request.headers['Access-Control-Request-Method']
        # Allow for 10 seconds
        h['Access-Control-Max-Age'] = "10"

        # We also keep current headers
        if headers is not None:
            h['Access-Control-Allow-Headers'] = headers

        return resp

@app.after_request
def set_allow_origin(resp):
    """ Set origin for GET, POST, PUT, DELETE requests """

    h = resp.headers

    # Allow crossdomain for other HTTP Verbs
    if request.method != 'OPTIONS' and 'Origin' in request.headers:
        h['Access-Control-Allow-Origin'] = request.headers['Origin']
    return resp


# TODO Look into Flask WTForms
# File upload handler
uploadFileParser = reqparse.RequestParser()
uploadFileParser.add_argument('pID', type=str, required=True)
class UploadFile(Resource):
    # Dataflow: 
    # 1. Save file in uploads/pID directory
    # 2. Save file location in project data collection
    # 3. Return sample
    def post(self):
        # TODO Require these parameters
        pID = request.form.get('pID').strip().strip('"')
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            # Save file
            filename = secure_filename(file.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], pID, filename)
            file.save(path)

            # Insert into project's datasets collection
            dID = MI.insertDataset(pID, file)

            # Get sample data
            sample, rows, cols, extension, header = get_sample_data(path)
            types = get_column_types(path)

            header, columns = read_file(path)

            # Make response
            column_attrs = [{'name': header[i], 'type': types[i], 'column_id': i} for i in range(0, len(columns) - 1)]
            json_data = json.jsonify({
                                    'status': "success",
                                    'title': filename,
                                    'filename': filename,
                                    'dID': dID,
                                    'column_attrs': column_attrs,
                                    'filename': filename,
                                    'header': header,
                                    'sample': sample,
                                    'rows': rows,
                                    'cols': cols,
                                    'filetype': extension,
                                    })
            response = make_response(json_data)
            response.set_cookie('file', filename)
            print "Upload response:", response
            return response
        return json.jsonify({'status': "Upload failed"})


# Dataset retrieval, editing, deletion
dataGetParser = reqparse.RequestParser()
dataGetParser.add_argument('dID', type=str, action='append')
dataGetParser.add_argument('pID', type=str, required=True)
dataGetParser.add_argument('sample', type=str, required=True, default='true')

dataDeleteParser = reqparse.RequestParser()
dataDeleteParser.add_argument('dID', type=str, action='append', required=True)
dataDeleteParser.add_argument('pID', type=str, action='append', required=True)
# TODO Eventually give capability to sample more of a dataset
class Data(Resource):
    # Get dataset descriptions or samples
    def get(self):
        args = dataGetParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        dIDs = args.get('dID')
        print "[GET] Data", pID, dIDs

        # Specific dIDs
        if dIDs:
            print "Requested specific dIDs:", dIDs
            dataLocations = [ MI.getData({'_id': ObjectId(dID)}, pID) for dID in dIDs ] 

        # All datasets
        else:
            print "Did not request specific dID. Returning all datasets"
            datasets = MI.getData({}, pID)
            data_list = []
            for d in datasets:
                path = os.path.join(app.config['UPLOAD_FOLDER'], pID, d['filename'])

                types = get_column_types(path)

                header, columns = read_file(path)
                unique_cols = [detect_unique_list(col) for col in columns]
    
                # make response
                sample, rows, cols, extension, header = get_sample_data(path)
                types = get_column_types(path)

                column_attrs = [{'name': header[i], 'type': types[i], 'column_id': i} for i in range(0, len(columns) - 1)]

                # Make response
                json_data = {
                    'title': d['filename'],
                    'filename': d['filename'],
                    'dID': d['dID'],
                    'column_attrs': column_attrs,
                    'header': header,
                    'sample': sample,
                    'rows': rows,
                    'cols': cols,
                    'filetype': extension,
                }
                data_list.append(json_data)
            return json.jsonify({'status': 'success', 'datasets': data_list})
    def delete(self):
        args = dataDeleteParser.parse_args()
        pIDs = args.get('pID')
        dIDs = args.get('dID')

        # TODO Handle this formatting on the client side (or server side for additional safety?)
        pIDs = [ pID.strip().strip('"') for pID in pIDs ]
        dIDs = [ dID.strip().strip('"') for dID in dIDs ]
        params = zip(dIDs, pIDs)
        deleted_dIDs = [ MI.deleteData(dID, pID) for (dID, pID) in params ]
        return deleted_dIDs

############################
# Get Project ID from Title
############################
projectIDGetParser = reqparse.RequestParser()
projectIDGetParser.add_argument('formattedProjectTitle', type=str, required=True)
class GetProjectID(Resource):
    def get(self):
        args = projectIDGetParser.parse_args()
        formattedProjectTitle = args.get('formattedProjectTitle')
        print "GET projectID", formattedProjectTitle
        res = MI.getProjectID(formattedProjectTitle)
        print "projectID result", res
        return res


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
projectDeleteParser.add_argument('pID', type=str, default='')

# TODO Return all projects
# Get information for one project
class Project(Resource):
    def get(self):
        args = projectGetParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        user_name = args.get('user_name')
        print "GET", pID, user_name

        return MI.getProject(pID, user_name)

    # Create project, initialize directories and collections
    def post(self):
        args = projectPostParser.parse_args()
        title = args.get('title')
        description = args.get('description')
        user_name = args.get('user_name')

        result = MI.postProject(title, description, user_name)

        # If successful project creation
        if result[1] is 200:
            # Create data upload directory
            print "Created upload directory for pID:", result[0]['pID']
            os.mkdir(os.path.join(app.config['UPLOAD_FOLDER'], result[0]['pID']))

        return result
        
    # Delete project and all associated data
    def delete(self):
        args = projectDeleteParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        print "DELETE", pID

        MI.deleteProject(pID)
        return



############################
# Property (begins processing on first client API call)
# Determine: types, hierarchies, uniqueness (subset of distributions), ontology, distributions
# INPUT: pID
# OUTPUT: {types: types_dict, uniques: is_unique_dict, overlaps: overlaps, hierarchies: hierarchies}
############################
propertyGetParser = reqparse.RequestParser()
propertyGetParser.add_argument('pID', type=str, required=True)
class Property(Resource):
    def get(self):
        print "[GET] Properties"
        args = propertyGetParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        datasets = MI.getData(None, pID)
        dIDs = [d['dID'] for d in datasets]

        types_dict = {}
        headers_dict = {}
        raw_columns_dict = {}
        is_unique_dict = {}
        uniqued_columns_dict = {}
        stats_dict = {}
        # TODO Don't reanalyze every single time...make properties persistent and only recalculate if dependent on uploaded datasets
        # Single-column functions
        # Create a pipeline of functions
        for dataset in datasets:
            dID = dataset['dID']
            filename = dataset['filename']
            path = os.path.join(app.config['UPLOAD_FOLDER'], pID, filename)
            header, columns = read_file(path)
            delim = get_delimiter(path)
            is_unique_dict[dID] = [detect_unique_list(col) for col in columns]

            headers_dict[dID] = header
            raw_columns_dict[dID] = [list(col) for col in columns]
            uniqued_columns_dict[dID] = [get_unique(col) for col in columns]

            # Statistical properties
            df = pd.read_table(path, sep=delim)
            df_stats = df.describe()
            df_stats_dict = json.loads(df_stats.to_json())
            stats_dict[dID] = df_stats_dict
            print df_stats_dict

            # Replace nan
            # entropy 
            # gini

            # List of booleans -- is a column composed of unique elements?
            is_unique = [detect_unique_list(col) for col in columns]
            is_unique_dict[dID] = is_unique

            types = get_column_types(path)
            types_dict[dID] = types

            # Save properties into collection
            dataset_properties = {
                'types': types,
                'uniques': is_unique,
                'headers': header,
                'stats': df_stats_dict
            }
            tID = MI.upsertProperty(dID, pID, dataset_properties)

        overlaps = {}
        hierarchies = {}
        # Compute cross-dataset overlaps
        # TODO Create a tighter loop to avoid double computes
        # TODO Make agnostic to ordering of pair
        for dID_a, dID_b in combinations(dIDs, 2):
            raw_cols_a = raw_columns_dict[dID_a]
            raw_cols_b = raw_columns_dict[dID_b]
            uniqued_cols_a = uniqued_columns_dict[dID_a]
            uniqued_cols_b = uniqued_columns_dict[dID_b]
            overlaps['%s\t%s' % (dID_a, dID_b)] = {}
            hierarchies['%s\t%s' % (dID_a, dID_b)] = {}

            for index_a, col_a in enumerate(raw_cols_a):
                for index_b, col_b in enumerate(raw_cols_b):
                    h = get_hierarchy(col_a, col_b)
                    d = get_distance(col_a, col_b)
                    if d:
                        overlaps['%s\t%s' % (dID_a, dID_b)]['%s\t%s' % (index_a, index_b)] = d
                        hierarchies['%s\t%s' % (dID_a, dID_b)]['%s\t%s' % (index_a, index_b)] = h

                        # TODO How do you store this?
                        ontology = {
                            'source_dID': dID_a,
                            'target_dID': dID_b,
                            'source_index': index_a,
                            'target_index': index_b,
                            'distance': d,
                            'hierarchy': h
                        }
                        oID = MI.upsertOntology(pID, ontology)

        all_properties = {
            'types': types_dict, 
            'uniques': is_unique_dict, 
            'overlaps': overlaps, 
            'hierarchies': hierarchies,
            'stats': stats_dict
        }

        print all_properties

        return json.jsonify(all_properties)


def is_numeric(x):
    if (x == 'int') or (x == 'float'):
        return True
    return False

#####################################################################
# 1. GROUP every entity by a non-unique attribute (for factors, group by factors but score by number of distinct. For continuous, discretize the range) 
#   1b. If attribute represents another object, also add aggregation by that object's attributes
# 2. AGGREGATE by some function (could be count)
# 3. QUERY by another non-unique attribute
#####################################################################

# TODO Incorporate ontologies
def getTreemapSpecs(datasets, properties, ontologies):
    specs = []
    dataset_titles = dict([(d['dID'], d['filename']) for d in datasets])

    for p in properties:
        print p
        dID = p['dID']
        # TODO Perform this as a database query with a specific document?
        relevant_ontologies = [ o for o in ontologies if ((o['source_dID'] == dID) or (o['target_dID'] == dID))]

        types = p['types']
        uniques = p['uniques']
        headers = p['headers']
        non_uniques = [i for (i, unique) in enumerate(uniques) if not unique]

        for (index_a, index_b) in combinations(non_uniques, 2):
            type_a = types[index_a]
            type_b = types[index_b]
            if not (is_numeric(type_a) or is_numeric(type_b)):
                specs.append({
                    'viz_type': 'treemap',
                    'condition': {'index': index_a, 'title': headers[index_a]},
                    'aggregate': {'dID': dID, 'title': dataset_titles[dID]},
                    'groupBy': {'index': index_b, 'title': headers[index_b]},
                    'chosen': False
                })
    return specs

#####################################################################
# Endpoint returning all inferred visualization specifications for a specific project
# INPUT: pID, uID
# OUTPUT: {visualizationType: [visualizationSpecification]}
#####################################################################
specificationDataGetParser = reqparse.RequestParser()
specificationDataGetParser.add_argument('pID', type=str, required=True)
specificationDataGetParser.add_argument('sID', type=str, action='append')
class Specification(Resource):
    def get(self):
        args = specificationDataGetParser.parse_args()
        pID = args.get('pID').strip().strip('"')

        d = MI.getData(None, pID)
        p = MI.getProperty(None, pID)
        o = MI.getOntology(None, pID)

        viz_types = {
            "treemap": getTreemapSpecs(d, p, o),
            # "geomap": getGeomapSpecs(p, o),
            # "barchart": getBarchartSpecs(p, o),
            # "scatterplot": getScatterplotSpecs(p, o),
            # "linechart": getLineChartSpecs(p, o),
            # "network": getNetworkSpecs(p, o)
        }

        for viz_type, specs in viz_types.iteritems():
            sIDs = MI.postSpecs(pID, specs) 
            for i, spec in enumerate(specs):
                spec['sID'] = sIDs[i]
                del spec['_id']
        return viz_types


vizToRequiredParams = {
    'treemap': ['aggregate', 'condition', 'groupBy']
}

# Utility functio n to make sure all fields needed to create visualization type are passed
def requiredParams(type, spec):
    for requiredParam in vizToRequiredParams[type]:
        if requiredParam not in spec:
            return False
    return True


def getTreemapData(spec, pID):
    # Parse specification
    condition = spec['condition']['title']
    groupby = spec['groupBy']['title']
    dID = spec['aggregate']['dID']
    aggFn = 'sum'  # TODO: get this from an argument

    # Load dataset (GENERALIZE THIS)
    filename = MI.getData({'_id': ObjectId(dID)}, pID)[0]['filename']
    path = os.path.join(app.config['UPLOAD_FOLDER'], pID, filename)
    delim = get_delimiter(path)
    df = pd.read_table(path, sep=delim)

    cond_df = df
    group_obj = cond_df.groupby(groupby)
    finalSeries = group_obj.size()

    result = []
    for row in finalSeries.iteritems():
        result.append({
            groupby: row[0],
            'count': np.asscalar(np.int16(row[1]))
        })
    return {'result': result}

    # Compute
    #         if query[0] == '*':
    #             cond_df = df
    #         else:
    #             # Uses column indexing for now
    #             cond_df = df[df[condition].isin(query)]

    return

#####################################################################
# Endpoint returning aggregated visualization data given a specification ID
# INPUT: sID, pID, uID
# OUTPUT: {nested visualization data}
#####################################################################
visualizationDataGetParser = reqparse.RequestParser()
visualizationDataGetParser.add_argument('pID', type=str, required=True)
visualizationDataGetParser.add_argument('type', type=str, required=True)
visualizationDataGetParser.add_argument('spec', type=str, required=True)
class Visualization_Data(Resource):
    def get(self):
        print "Getting viz data"
        args = visualizationDataGetParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        type = args.get('type')
        spec = json.loads(args.get('spec'))
        if requiredParams(type, spec):
            print getTreemapData(spec, pID)
            return getTreemapData(spec, pID)
        return


def getConditionalData(spec, pID):
    # Parse specification
    condition = spec['condition']['title']
    dID = spec['aggregate']['dID']

    # Load dataset (GENERALIZE THIS)
    filename = MI.getData({'_id': ObjectId(dID)}, pID)[0]['filename']
    path = os.path.join(app.config['UPLOAD_FOLDER'], pID, filename)
    delim = get_delimiter(path)
    df = pd.read_table(path, sep=delim)

    unique_elements = [{condition: e} for e in pd.Series(df[condition]).unique()]

    return {'result': unique_elements}

#####################################################################
# Endpoint returning data to populate dropdowns for given specification
# INPUT: sID, pID, uID
# OUTPUT: [conditional elements]
#####################################################################
chooseSpecParser = reqparse.RequestParser()
chooseSpecParser.add_argument('pID', type=str, required=True)
chooseSpecParser.add_argument('sID', type=str, required=True)
class Choose_Spec(Resource):
    def get(self):
        args = chooseSpecParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        sID = args.get('sID')
        MI.chooseSpec(pID, sID)
        return

rejectSpecParser = reqparse.RequestParser()
rejectSpecParser.add_argument('pID', type=str, required=True)
rejectSpecParser.add_argument('sID', type=str, required=True)
class Reject_Spec(Resource):
    def get(self):
        args = rejectSpecParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        sID = args.get('sID')
        MI.rejectSpec(pID, sID)
        return

#####################################################################
# Endpoint returning data to populate dropdowns for given specification
# INPUT: sID, pID, uID
# OUTPUT: [conditional elements]
#####################################################################
visualizationDataGetParser = reqparse.RequestParser()
visualizationDataGetParser.add_argument('pID', type=str, required=True)
visualizationDataGetParser.add_argument('type', type=str, required=True)
visualizationDataGetParser.add_argument('spec', type=str, required=True)
class Conditional_Data(Resource):
    def get(self):
        args = visualizationDataGetParser.parse_args()
        pID = args.get('pID').strip().strip('"')
        type = args.get('type')
        spec = json.loads(args.get('spec'))
        if requiredParams(type, spec):
            return getConditionalData(spec, pID)
        return


api.add_resource(UploadFile, '/api/upload')
api.add_resource(Data, '/api/data')
api.add_resource(GetProjectID, '/api/getProjectID')
api.add_resource(Project, '/api/project')
api.add_resource(Property, '/api/property')
api.add_resource(Specification, '/api/specification')
api.add_resource(Choose_Spec, '/api/choose_spec')
api.add_resource(Reject_Spec, '/api/reject_spec')
api.add_resource(Visualization_Data, '/api/visualization_data')
api.add_resource(Conditional_Data, '/api/conditional_data')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=PORT)
