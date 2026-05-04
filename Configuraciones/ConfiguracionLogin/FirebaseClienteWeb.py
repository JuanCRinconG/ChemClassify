"""
Public Firebase Web SDK config (same project as Admin SDK).

Values are safe to expose in the browser. Prefer overriding via environment
variables in production; defaults match the ChemClassify web app in Firebase.
"""

from __future__ import annotations

import os
from typing import Any, Dict


def firebase_web_config_dict() -> Dict[str, Any]:
    """Return the object passed to initializeApp() in the browser."""
    cfg: Dict[str, Any] = {
        'apiKey': os.environ.get(
            'CHEMCLASSIFY_FIREBASE_API_KEY',
            'AIzaSyDcpOqOP_NYDto85gJIOyGnXABGybrVc5w',
        ),
        'authDomain': os.environ.get(
            'CHEMCLASSIFY_FIREBASE_AUTH_DOMAIN',
            'chemclassify-d448c.firebaseapp.com',
        ),
        'projectId': os.environ.get(
            'CHEMCLASSIFY_FIREBASE_PROJECT_ID',
            'chemclassify-d448c',
        ),
        'storageBucket': os.environ.get(
            'CHEMCLASSIFY_FIREBASE_STORAGE_BUCKET',
            'chemclassify-d448c.appspot.com',
        ),
        'messagingSenderId': os.environ.get(
            'CHEMCLASSIFY_FIREBASE_MESSAGING_SENDER_ID',
            '11057633097',
        ),
        'appId': os.environ.get(
            'CHEMCLASSIFY_FIREBASE_APP_ID',
            '1:11057633097:web:86ff535e127048b7646c98',
        ),
    }
    mid = os.environ.get('CHEMCLASSIFY_FIREBASE_MEASUREMENT_ID', '').strip()
    if mid:
        cfg['measurementId'] = mid
    return cfg
