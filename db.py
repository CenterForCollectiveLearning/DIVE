import math
import pymongo
from pymongo import GEO2D
from bson.objectid import ObjectId
import os
import urllib
import random
import time
import json

def formatObjectIDs(collectionName, results):
    for result in results: # For each result is passed, convert the _id to the proper mID, cID, etc.
        result[collectionName[0]+'ID'] = str(result.pop('_id')) # Note the .pop removes the _id from the dict
    return results

class mongoInstance(object):
    # Get Project ID from formattedProjectTitle
    def getProjectID(self, formatted_title):
        return str(MongoInstance.client['dive'].projects.find_one({'formattedTitle': formatted_title})['_id'])

    # Dataset Insertion
    def insertDataset(self, pID, fileStorage):
        return str(MongoInstance.client[pID].datasets.insert({'filename': fileStorage.filename, 'title': fileStorage.filename.split('.')[0]}))

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
        resp = MongoInstance.client[pID].specifications.insert(specs)
        print len([str(sID_obj) for sID_obj in resp])
        return [str(sID_obj) for sID_obj in resp]

    def chooseSpec(self, pID, sID):
        info = MongoInstance.client[pID].specifications.find_and_modify({'sID': sID}, {'$set': {'chosen': True}}, upsert=True, new=True)
        sID = str(info['_id'])
        return sID

    def rejectSpec(self, pID, sID):
        info = MongoInstance.client[pID].specifications.find_and_modify({'sID': sID}, {'$set': {'chosen': False}}, upsert=True, new=True)
        sID = str(info['_id'])
        return sID

    # Project Editing
    def getProject(self, pID, user):
        projects_collection = MongoInstance.client['dive'].projects
        doc = {
            'user': user
        }
        if pID: doc['_id'] = ObjectId(pID)
        return formatObjectIDs('project', [ p for p in projects_collection.find(doc)])

    def deleteProject(self, pID):
        print "In deleteProject", pID
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

    # Project Creation
    def postProject(self, title, description, user):
        formatted_title = title.replace(" ", "-").lower()

        projects_collection = MongoInstance.client['dive'].projects
        existing_project = projects_collection.find_one({'formattedTitle': formatted_title, 'user': user})
        if existing_project:
            print "Project Already Exists"
            return str(existing_project['_id']), 409
        else:
            # Insert project into DIVE project collections
            pID = str(projects_collection.insert({'formattedTitle': formatted_title, 'title': title, 'description': description, 'user': user}))

            # Create user
            # TODO Tie into projects
            MongoInstance.client['dive'].users.insert({'userName': user})

            # Create project DB
            db = MongoInstance.client[pID]
            db.create_collection('datasets')
            db.create_collection('visualizations')
            db.create_collection('properties')
            db.create_collection('ontologies')
            print "Creating new project"
            return {'formatted_title': formatted_title, 'pID': pID}, 200

    # Client corresponding to a single connection
    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = pymongo.MongoClient(host='localhost:27017')
        return self._client

# A Singleton Object
MongoInstance = mongoInstance()