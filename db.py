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
        return str(MongoInstance.client[pID].datasets.insert({'filename': fileStorage.filename}))

    # Dataset Retrieval
    def getData(self, dID, pID):
        if dID:
            return formatObjectIDs('dataset', [ d for d in MongoInstance.client[pID].datasets.find({'_id': dID}) ])
        else:
            return formatObjectIDs('dataset', [ d for d in MongoInstance.client[pID].datasets.find() ])

    # Dataset Deletion
    def deleteData(self, dID, pID):
        resp = MongoInstance.client[pID].datasets.remove({'_id': ObjectId(dID)})
        if resp['n'] and resp['ok']:
            return dID

    # Project Editing
    def getProject(self, pID, user):
        projects_collection = MongoInstance.client['dive'].projects
        if pID:
            return formatObjectIDs('project', [ p for p in projects_collection.find({'user': user, '_id': ObjectId(pID)})])
        else:
            # return projects_collection.find({'user': user})
            return formatObjectIDs('project', [ p for p in projects_collection.find({'user': user})])

    # Project Creation
    def postProject(self, title, description, user):
        print title, description, user
        formatted_title = title.replace(" ", "-").lower()

        projects_collection = MongoInstance.client['dive'].projects
        existing_project = projects_collection.find_one({'formattedTitle': formatted_title, 'user': user})
        if existing_project:
            print "Project Already Exists"
            return str(existing_project['_id']), 409
        else:
            db = MongoInstance.client[formatted_title]
            db['users'].insert({'userName': user, 'uID': ''})
            db.create_collection('datasets')
            db.create_collection('visualizations')
            db.create_collection('properties')
            db.create_collection('ontologies')
            print "Creating new project"
            return {'formatted_title': formatted_title, 'pID': str(projects_collection.insert({'formattedTitle': formatted_title, 'title': title, 'description': description, 'user': user}))}, 200

    # Client corresponding to a single connection
    @property
    def client(self):
        if not hasattr(self, '_client'):
            self._client = pymongo.MongoClient(host='localhost:27017')
        return self._client

# A Singleton Object
MongoInstance = mongoInstance()