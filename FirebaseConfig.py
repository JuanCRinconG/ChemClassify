import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar Firebase solo si no está ya inicializado
if not firebase_admin._apps:
    cred = credentials.Certificate('CredencialesFirebase/chemclassify-d448c-firebase-adminsdk-fbsvc-333079f7f4.json')
    firebase_admin.initialize_app(cred)

# Instancia global de Firestore
db = firestore.client()