from google.oauth2.credentials import Credentials
from google.cloud.firestore import Client


def firestore_init(user):
    # Use google.oauth2.credentials and the response object to create the correct user credentials
    creds = Credentials(user['idToken'], user['refreshToken'])

    # Use the raw firestore grpc client instead of building one through firebase_admin
    db = Client("hood-control-67b78", creds)
    docs = db.collection('users').get()
    for doc in docs:
        print(doc.to_dict())
    return db



# Et voila! 
# You are now connected to your firestore database and authenticated with the selected firebase user.
# All your firestore security rules now apply on this connection and it will behave like a normal client

# doc_ref = db.collection(u'cities').document(u'SF')

# doc = doc_ref.get()
# if doc.exists:
#     print(u'Document data: {}'.format(doc.to_dict()))
# else:
#     print(u'No such document!')