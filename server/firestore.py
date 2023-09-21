from google.oauth2.credentials import Credentials
from google.cloud.firestore import Client

'''fire store python service

This module expects a user object that has been authenticated already.
No python sdk is provided by google for the fire store database, so this will
load an admin level account from their sdk, yet with only user
level access'''

def firestore_init(user,projectId=None):
    # Use google.oauth2.credentials and the response object to create the correct user credentials
    creds = Credentials(user['idToken'], user['refreshToken'])

    # Use the raw firestore grpc client instead of building one through firebase_admin
    db = Client(project=projectId,credentials=creds)
    return db

# def 
#     users_ref = db.collection('users')
#     users_listener=users_ref.on_snapshot(lambda *docs:print(docs))

