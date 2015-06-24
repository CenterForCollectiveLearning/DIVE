
import math
import pymongo
from pymongo import GEO2D
from bson.objectid import ObjectId
import os
import urllib
import random
import time
import json

# TODO: Use a SON manipulator?
def remove_dots(data):
    for k, d in data.iteritems():
        if type(d) is dict: d = remove_dots(d)
        if '.' in k and isinstance(k, basestring):
            data[k.replace('.', '\uff0E')] = data[k]
            del data[k]
    return data

def formatObjectIDs(collectionName, results):
    for result in results: # For each result is passed, convert the _id to the proper mID, cID, etc.
        result[collectionName[0]+'ID'] = str(result.pop('_id')) # Note the .pop removes the _id from the dict
    return results


class mongoInstance(object):
    # Get Project ID from formattedProjectTitle
    def getProjectID(self, formatted_title, userName):
        print "TITLE: ", formatted_title
        find_doc = {
            "formattedTitle" : formatted_title,
            "user" : userName
        }
        return str(MongoInstance.client['dive'].projects.find_one(find_doc)['_id'])

    # Dataset Insertion
    def insertDataset(self, pID, path, filename):

        title = filename.rsplit('.', 1)[0]
        file_type = filename.rsplit('.', 1)[1]

        dataset_doc = {
            'path': path,
            'filename': filename, 
            'title': title,
            'type': file_type
        }

        return str(MongoInstance.client[pID].datasets.insert(dataset_doc))

    # Dataset Retrieval
    def getData(self, find_doc, pID):
        return formatObjectIDs('dataset', [ d for d in MongoInstance.client[pID].datasets.find(find_doc) ])

    # Dataset Deletion
    def deleteData(self, dID, pID):
        MongoInstance.client[pID].properties.remove({'dID': dID})
        resp = MongoInstance.client[pID].datasets.remove({'_id': ObjectId(dID)})
        if resp['n'] and resp['ok']:
            return dID

    def postSpecs(self, pID, specs):
        specs = [ remove_dots(s) for s in specs ]
        resp = MongoInstance.client[pID].specifications.insert(specs)
        return [str(sID_obj) for sID_obj in resp]


    def getSpecs(self, pID, find_doc):
        return formatObjectIDs('specification', [s for s in MongoInstance.client[pID].specifications.find(find_doc) ])

    # Using preloaded datasets
    def usePublicDataset(self, find_doc, pID):
        publicDatasets = MongoInstance.client['dive'].datasets.find(find_doc)
        new_dIDs = []
        for d in publicDatasets:
            d['original_dID'] = str(d['_id'])
            del d['_id']
            new_dID = MongoInstance.client[pID].datasets.insert(d)
            new_dIDs.append(new_dID)
        return new_dIDs

    # Exported visualizations
    def getExportedSpecs(self, find_doc, pID):
        exported_specs = [ e for e in MongoInstance.client[pID].exported.find(find_doc)]
        return formatObjectIDs('exported', exported_specs)

    def addExportedSpec(self, pID, spec, conditional):
        d = {}
        d['spec']  = spec
        d['conditional'] = conditional
        return str(MongoInstance.client[pID].exported.insert(d))

    def chooseSpec(self, pID, sID, conditional, stats):
        MongoInstance.client[pID].specifications.find_and_modify(
            {'_id': ObjectId(sID)}, 
            {'$set': {'chosen': True, 'conditional': conditional, 'stats' : stats }}, upsert=True, new=True)
        return sID

    def rejectSpec(self, pID, sID):
        MongoInstance.client[pID].specifications.find_and_modify({'_id': ObjectId(sID)}, {'$set': {'chosen': False}}, upsert=True, new=True)
        return sID

    # Project Editing
    def getProject(self, pID, user):
        projects_collection = MongoInstance.client['dive'].projects
        doc = {
            'user': user
        }
        # if pID: doc['_id'] = ObjectId(pID)
        return formatObjectIDs('project', [ p for p in projects_collection.find(doc)])

    def deleteProject(self, pID):
        # Drop top-level DB
        MongoInstance.client.drop_database(pID)

        # Drop DB document in DIVE DB
        MongoInstance.client['dive'].projects.remove({'_id': ObjectId(pID)})
        return

    def upsertProperty(self, dID, pID, properties):
        info = MongoInstance.client[pID].properties.find_and_modify({'dID': dID}, {'$set': properties}, upsert=True, new=True)
        tID = str(info['_id'])
        return tID

    def getProperty(self, find_doc, pID):
        return formatObjectIDs('t', [ t for t in MongoInstance.client[pID].properties.find(find_doc) ])

    def getOntology(self, find_doc, pID):
        return formatObjectIDs('ontology', [ o for o in MongoInstance.client[pID].ontologies.find(find_doc) ])

    def upsertOntology(self, pID, ontology):
        o = ontology
        find_doc = {
            'source_dID': o['source_dID'],
            'target_dID': o['target_dID'],
            'source_index': o['source_index'],
            'target_index': o['target_index']
        }
        info = MongoInstance.client[pID].ontologies.find_and_modify(find_doc, {'$set': ontology}, upsert=True, new=True)
        if info:
            oID = str(info['_id'])
            return oID
        else:
            print o

    def resetOntology(self, pID) :
        return MongoInstance.client[pID].ontologies.remove({})


    # Project Creation
    def postProject(self, title, description, user, anonymous):
        formatted_title = title.replace(" ", "-").lower()

        projects_collection = MongoInstance.client['dive'].projects
        existing_project = projects_collection.find_one({'formattedTitle': formatted_title, 'user': user})
        if existing_project:
            print "Project Already Exists"
            return str(existing_project['_id']), 409
        else:
            # Insert project into DIVE project collections
            pID = str(projects_collection.insert({
                'formattedTitle': formatted_title,
                'title': title,
                'description': description,
                'user': user,
                'anonymous': anonymous
            }))

            # Create user
            # TODO Tie into projects
            # MongoInstance.client['dive'].users.insert({'userName': user})

            # Create project DB
            db = MongoInstance.client[pID]
            db.create_collection('datasets')
            db.create_collection('visualizations')
            db.create_collection('properties')
            db.create_collection('ontologies')
            db.create_collection('exported')
            print "Creating new project"
            return {'formatted_title': formatted_title, 'pID': pID}, 200

    # User Creation
    def postNewUser(self, userName, displayName, password) :
        user = {
            'userName' : userName,
            'displayName' : displayName,
            'password' : password
        }
        # str(MongoInstance.client[pID].datasets.insert(dataset_doc))
        return str(MongoInstance.client['dive'].users.insert(user))

    def getUser(self, find_doc) :
        return formatObjectIDs('users', [u for u in MongoInstance.client['dive'].users.find(find_doc).limit(1) ])
                # return formatObjectIDs('ontology', [ o for o in MongoInstance.client[pID].ontologies.find(find_doc) ])

    # Client corresponding to a single connection
    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = pymongo.MongoClient(host='localhost:27017')
        return self._client

# A Singleton Object
MongoInstance = mongoInstance()
