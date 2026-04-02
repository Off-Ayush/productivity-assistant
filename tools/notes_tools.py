"""Notes management tools for the productivity assistant.

Provides tools to create, list, and search notes in Firestore.
"""

import logging
import uuid
from datetime import datetime

from google.adk.tools.tool_context import ToolContext

from productivity_assistant.db import get_db

logger = logging.getLogger(__name__)


def create_note(tool_context: ToolContext, title: str, content: str, tags: list = None) -> dict:
    """Create a new note in Firestore.

    Args:
        tool_context: The tool context for state management.
        title: The title of the note.
        content: The content of the note.
        tags: Optional list of tags for the note.

    Returns:
        dict: A dictionary with status and note_id on success, or status and message on error.
    """
    try:
        db = get_db()
        note_id = str(uuid.uuid4())
        note_data = {
            "id": note_id,
            "title": title,
            "content": content,
            "tags": tags if tags else [],
            "created_at": datetime.utcnow().isoformat()
        }
        db.collection("notes").document(note_id).set(note_data)
        logging.info(f"Created note: {note_id} - {title}")
        return {"status": "success", "note_id": note_id, "title": title}
    except Exception as e:
        logging.error(f"Error creating note: {str(e)}")
        return {"status": "error", "message": str(e)}


def list_notes(tool_context: ToolContext) -> dict:
    """List all notes from Firestore.

    Args:
        tool_context: The tool context for state management.

    Returns:
        dict: A dictionary with status and list of notes on success, or status and message on error.
    """
    try:
        db = get_db()
        notes_ref = db.collection("notes")
        notes = notes_ref.stream()

        note_list = [dict(note.to_dict()) for note in notes]
        logging.info(f"Listed {len(note_list)} notes")
        return {"status": "success", "notes": note_list}
    except Exception as e:
        logging.error(f"Error listing notes: {str(e)}")
        return {"status": "error", "message": str(e)}


def search_notes(tool_context: ToolContext, query: str) -> dict:
    """Search notes by query string in title or content.

    Args:
        tool_context: The tool context for state management.
        query: The search query string.

    Returns:
        dict: A dictionary with status, results, and count on success, or status and message on error.
    """
    try:
        db = get_db()
        notes_ref = db.collection("notes")
        notes = notes_ref.stream()

        query_lower = query.lower()
        results = []
        for note in notes:
            note_data = note.to_dict()
            title = note_data.get("title", "")
            content = note_data.get("content", "")
            if query_lower in title.lower() or query_lower in content.lower():
                results.append(dict(note_data))

        logging.info(f"Search for '{query}' returned {len(results)} results")
        return {"status": "success", "results": results, "count": len(results)}
    except Exception as e:
        logging.error(f"Error searching notes: {str(e)}")
        return {"status": "error", "message": str(e)}
