import os
from flask import Flask, request
from flask_restful import Resource, Api
from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient('mongodb://' + os.environ['MONGODB_HOSTNAME'], 27017)
db = client.brevetdb

#Converts database records to csv
#Returned as brevet_dist, km, open, close, km, open, close,...
def _db_data_to_csv(data):
    csv_data = ""
    print(data)
    for brevet in data:
        line = ""
        line += brevet['brevet_dist']
        for control in brevet['controls']:
            line += ',' + control['km']
            if 'open' in control: 
                line += ',' + control['open']
            if 'close' in control: 
                line += ',' + control['close']
        csv_data += line + '\n'
    return csv_data

#Strips a brevets controls down to the 'top_n'
def _top_n_list(items, top_n):
    len_items = len(items)
    if top_n > len_items:
        return items

    top_items = items[:top_n]
    return top_items

#applies _top_n_list to each individual brevet
def _top_n_brevet_list(brevets, top_n):
    new_brevets = []
    for brevet in brevets:
        new_brevet = brevet
        new_brevet['controls'] = _top_n_list(brevet['controls'], top_n)
        new_brevets.append(new_brevet)
    return new_brevets

#Strips fields like '_id' from database records
def _strip_database_records(data):
    brevets = []
    for record in data:
        brevet = {'brevet_dist' : record['brevet_dist']}
        controls = []
        for control in record['controls']:
            new_control = {'km': control['km'], 'open': control['open'], 'close': control['close']}
            controls.append(new_control)
        brevet['controls'] = controls
        brevets.append(brevet)
    return brevets


#Resource for handling listAll requests
class ListAll(Resource):
    def get(self, fmt='json'): 
        #Remove database specific key,value pairs
        brevets = _strip_database_records(list(db.brevets.find()))

        #Remove all controls other than the 'top_n', if applicable
        top_n = request.args.get('top', type=int)
        if top_n != None:
            brevets = _top_n_brevet_list(brevets, top_n)

        #Return either json or csv
        if fmt == 'json':
            return brevets
        elif fmt == 'csv':
            return _db_data_to_csv(brevets)
        else:
            return 'INVALID FORMAT DIRECTIVE'

#used to remove 'open' or 'closed' from the retrieved database records
def _rm_from_brevets_controls(brevets, key):
    for brevet in brevets:
        for control in brevet['controls']:
            del control[key]
    return brevets

#Resource for handling listOpenOnly requests
class ListOpenOnly(Resource):
    def get(self, fmt='json'):
        brevets = _strip_database_records(list(db.brevets.find()))
        top_n = request.args.get('top', type=int)
        if top_n != None:
            brevets = _top_n_brevet_list(brevets, top_n)

        brevets = _rm_from_brevets_controls(brevets, 'close')
        if fmt == 'json':
            return brevets
        elif fmt == 'csv':
            return _db_data_to_csv(brevets)
        else:
            return 'INVALID FORMAT DIRECTIVE'

#Resource for handling listCloseOnly requests
class ListCloseOnly(Resource):
    def get(self, fmt='json'):
        brevets = _strip_database_records(list(db.brevets.find()))
        top_n = request.args.get('top', type=int)
        if top_n != None:
            brevets = _top_n_brevet_list(brevets, top_n)

        brevets = _rm_from_brevets_controls(brevets, 'open')
        if fmt == 'json':
            return brevets
        elif fmt == 'csv':
            return _db_data_to_csv(brevets)
        else:
            return 'INVALID FORMAT DIRECTIVE'

#Different possible urls to use for queries
api.add_resource(ListAll, '/listAll', '/listAll/<string:fmt>')
api.add_resource(ListOpenOnly, '/listOpenOnly', '/listOpenOnly/<string:fmt>')
api.add_resource(ListCloseOnly, '/listCloseOnly', '/listCloseOnly/<string:fmt>')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


