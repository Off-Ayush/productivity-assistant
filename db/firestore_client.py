"""Firestore database client module.

Provides a shared Firestore client with lazy initialization.
"""

import os
from dotenv import load_dotenv
from google.cloud import firestore

load_dotenv()

_db_client = None


def get_db() -> firestore.Client:
    """Get the Firestore database client.

    Returns a shared Firestore client instance, creating it lazily
    on first call. Uses PROJECT_ID from environment variables.

    Returns:
        firestore.Client: The Firestore database client.
    """
    global _db_client
    if _db_client is None:
        project_id = os.getenv("PROJECT_ID")
        _db_client = firestore.Client(project=project_id)
    return _db_client
