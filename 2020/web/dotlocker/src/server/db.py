import os
import re

from pymongo import MongoClient
from bson.objectid import ObjectId

client = MongoClient()
db = client.db

def get_or_add_user(_id=None, name=None):
    x = None
    if _id is not None:
        try:
            _id = ObjectId(_id)
            x = db.users.find_one({'_id': _id})
        except:
            pass
    if x is None:
        u = {
            'dotfiles': {},
            'name': name if name else 'guest_'+os.urandom(5).encode('hex'),
            'csrf': os.urandom(32).encode('hex'),
        }
        res = db.users.insert_one(u)
        u['_id'] = res.inserted_id
        return u
    return x

def safe_name(name):
    return re.sub(r'[^\w]','_',name)

def add_dotfile(user, name, file, overwrite_public=False):
    file['name'] = str(name)
    key = safe_name(name)
    if (not overwrite_public and key in user['dotfiles'] and 
            user['dotfiles'][key].get('protected',False)):
        return False
    db.users.update({'_id':user['_id']},{'$set':{'dotfiles.'+key:file}})
    return True

def get_user(_id):
    try:
        _id = ObjectId(_id)
    except:
        return None
    return db.users.find_one({'_id':_id})

def get_user_by_name(name):
    return db.users.find_one({'name':name})


def valid_csrf(token, _id):
    try:
        _id = ObjectId(_id)
    except:
        return False
    return db.users.find_one({'csrf':token, '_id':_id}) is not None


