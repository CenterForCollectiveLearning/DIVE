import os
import re
from random import sample
from os import listdir
from os.path import isfile, join
from itertools import combinations
from werkzeug.utils import secure_filename
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


# Only one server-side route due to AngularJS SPA Routing
@app.route('/')
def main():
    return render_template('/main.html')


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
api.add_resource(UploadFile, '/api/upload')


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
        print "Get Data", pID, dIDs

        # Specific dIDs
        if dIDs:
            print "Requested specific dIDs:", dIDs
            dataLocations = [ MI.getData({'_id': dID}, pID) for dID in dIDs ] 

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

api.add_resource(Data, '/api/data')

############################
# Get Project ID from Title
############################
projectIDGetParser = reqparse.RequestParser()
projectIDGetParser.add_argument('formattedProjectTitle', type=str, required=True)
class GetProjectID(Resource):
    def get(self):
        args = projectIDGetParser.parse_args()
        formattedProjectTitle = args.get('formattedProjectTitle')
        return MI.getProjectID(formattedProjectTitle)
api.add_resource(GetProjectID, '/api/getProjectID')

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
        pIDs = args.get('pID')
        return [ MI.deleteThing(pID, 'projects', []) for pID in pIDs]
    # The way that angular does http requests is slightly different than in python (or maybe it's a CORS thing)
    # Either way, we need this options to return the following access-control-allow-methods, otherwise delete wasn't working.
    # Will likely have to include for all classes
    def options (self): 
        return {'Allow' : 'PUT, GET, POST, DELETE' }, 200, \
        { 'Access-Control-Allow-Origin': '*', \
          'Access-Control-Allow-Methods' : 'PUT,GET, POST, DELETE' }

api.add_resource(Project, '/api/project')

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
        # TODO Don't reanalyze every single time...make properties persistent and only recalculate if dependent on uploaded datasets
        # Tie into a single function
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
            print df, df.describe()
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
                'headers': header
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
            'hierarchies': hierarchies
        }

        return json.jsonify(all_properties)
api.add_resource(Property, '/api/property')

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
                    'condition': {'index': index_a, 'title': headers[index_a]},
                    'aggregate': {'dID': dID, 'title': dataset_titles[dID]},
                    'groupBy': {'index': index_b, 'title': headers[index_b]},
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

        
        # print 'Properties:', properties
        # print 'Ontologies:', ontologies
        return viz_types
api.add_resource(Specification, '/api/specification')

#####################################################################
# Endpoint returning aggregated visualization data given a specification ID
# INPUT: sID, pID, uID
# OUTPUT: {nested visualization data}
#####################################################################
visualizationDataParser = reqparse.RequestParser()
class Visualization_Data(Resource):
    def get(self):
        return
api.add_resource(Visualization_Data, '/api/visualization_data')

# treemapDataParser = reqparse.RequestParser()
# treemapDataParser.add_argument('condition', type=int, required=True)
# treemapDataParser.add_argument('aggregate', type=int, required=True)
# treemapDataParser.add_argument('groupBy', type=int, required=True)
# treemapDataParser.add_argument('query', type=str, required=True)
# treemapDataParser.add_argument('aggFn', type=str, default='sum')
# class get_treemap_data(Resource):
#     def get(self):
#         # Get and parse arguments
#         args = treemapDataParser.parse_args()
#         condition = args.get('condition')
#         aggregate = args.get('aggregate')
#         by = args.get('groupBy')
#         by_id = by
#         query = args.get('query').strip('[').strip(']').split(',')
#         aggFn = args.get('aggFn')

#         # Test
#         # http://localhost:5000/get_treemap_data?condition=11&aggregate=2&by=14&query=[USA]
#         path = DAL.get_path_from_id(aggregate)
#         delim = get_delimiter(path)
#         df = pd.read_table(path, sep=delim)

#         by = DAL.get_column_name_from_id(aggregate, by)
#         condition = DAL.get_column_name_from_id(aggregate, condition)

#         if query[0] == '*':
#             cond_df = df
#         else:
#             # Uses column indexing for now
#             cond_df = df[df[condition].isin(query)]

#         group_obj = cond_df.groupby(by)
#         finalSeries = group_obj.size()

#         result = []
#         for row in finalSeries.iteritems():
#             result.append({
#                 by_id: row[0],
#                 'count': np.asscalar(np.int16(row[1]))
#             })
#         # print result
#         for r in result:
#             print r, r['count']
#         return {'result': result}

# # TODO Break this up!!!
# vizFromOntParser = reqparse.RequestParser()
# # vizFromOntParser.add_argument('network', type=str, required=True)
# class get_visualizations_from_ontology(Resource):
#     def post(self):
#         visualizations = {
#             "treemap": [],
#             "geomap": [],
#             "barchart": [],
#             "scatterplot": [],
#             "linechart": [],
#             "network": []
#         }

#         # TODO Use regular argument parser
#         network = json.loads(request.data)
#         nodes = network['nodes']
#         edges = network['edges']

#         edge_to_type_dict = {}
#         for edge in edges:
#             source = edge['source']
#             target = edge['target']
#             type = edge['type']

#             edge_to_type_dict[tuple(source)] = type
#             edge_to_type_dict[tuple(target)] = type

#         # SCATTERPLOT
#         # ATTR vs ATTR, optional QUERY and GROUP
#         # for node in nodes:
#         #     attrs = node['attrs']
#         #     for attrA, attrB in combinations(attrs, 2):
#         #         # TODO Don't plot against unique columns
#         #         if (attrA['type'] in ['int', 'float'] or attrB['type'] in ['int', 'float']):
#         #             print attrA['name'], attrB['name']

#         # TODO Detect redundant fields
#         # Detect objects that are attributes of another (count one-to-many edges leading outward)
#         numOutwardOneToManys = dict([(node['model'], 0) for node in nodes])
#         for edge in edges:
#             sourceDataset = edge['source'][0]
#             targetDataset = edge['target'][0]
#             type = edge['type']
#             if type == '1N':
#                 numOutwardOneToManys[targetDataset] += 1
#             if type == 'N1':
#                 numOutwardOneToManys[sourceDataset] += 1

#         # TODO: Detect if an entity is likely geographic

#         # LINE CHART

#         # TREEMAP
#         # CONDITION -> QUERY -> N * GROUP BY
#         for node in nodes:
#             dataset_id = node['model']

#             # Must be a first-order object
#             if numOutwardOneToManys[dataset_id]:
#                 attrs = node['attrs']

#                 for attrA, attrB in combinations(attrs, 2):
#                     unique_A = node['unique_cols'][attrs.index(attrA)]
#                     unique_B = node['unique_cols'][attrs.index(attrB)]
#                     type_A = attrA['type']
#                     type_B = attrB['type']
#                     column_idA = attrA['column_id']
#                     column_idB = attrB['column_id']
#                     name_A = attrA['name']
#                     name_B = attrB['name']

#                     column_relnA = edge_to_type_dict.get(tuple([dataset_id, column_idA]))
#                     column_relnB = edge_to_type_dict.get(tuple([dataset_id, column_idB]))

#                     # Ensure that the condition and grouping attributes map to second-order objects
#                     # Ensure that the conditioning and grouping variables are not floats
#                     # (do we want to do this???)
#                     print name_A, column_relnA
#                     if (not column_relnA) and (not unique_A) and (type_A != 'float') and (type_B != 'float') and (type_B != 'int'):
#                         treemap_spec = {
#                         'condition': column_idA,
#                         'aggregate': dataset_id,
#                         'groupBy': column_idB,
#                         }
#                         visualizations['treemap'].append(treemap_spec)

#                     if (not unique_A) and (name_B == 'countryCode3'):
#                         geomap_spec = {
#                             'condition': column_idA,
#                             'aggregate': dataset_id,
#                             'groupBy': column_idB,
#                         }
#                         visualizations['geomap'].append(geomap_spec)

#         result = {}
#         for vizType, vizSpecs in visualizations.iteritems():
#             if vizSpecs:
#                 result[vizType] = vizSpecs


#         json_data = json.jsonify({
#                                 'status': "success",
#                                 'visualizations': result,
#                                 })
#         response = make_response(json_data)
#         return response

# api.add_resource(get_visualizations_from_ontology, '/get_visualizations_from_ontology')

# Visualization Endpoints
# api.add_resource(get_treemap_data, '/get_treemap_data')

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=PORT)
