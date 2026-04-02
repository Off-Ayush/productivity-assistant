"""Calendar management tools for the productivity assistant.

Provides tools to create, list, and delete calendar events in Firestore.
"""

import logging
import uuid
from datetime import datetime

from google.adk.tools.tool_context import ToolContext

from productivity_assistant.db import get_db

logger = logging.getLogger(__name__)


def create_event(tool_context: ToolContext, title: str, date: str, time: str, description: str = "") -> dict:
    """Create a new calendar event in Firestore.

    Args:
        tool_context: The tool context for state management.
        title: The title of the event.
        date: The date of the event (YYYY-MM-DD format).
        time: The time of the event (HH:MM format).
        description: Optional description of the event.

    Returns:
        dict: A dictionary with status and event_id on success, or status and message on error.
    """
    try:
        db = get_db()
        event_id = str(uuid.uuid4())
        event_data = {
            "id": event_id,
            "title": title,
            "date": date,
            "time": time,
            "description": description,
            "created_at": datetime.utcnow().isoformat()
        }
        db.collection("events").document(event_id).set(event_data)
        logging.info(f"Created event: {event_id} - {title}")
        return {"status": "success", "event_id": event_id, "title": title}
    except Exception as e:
        logging.error(f"Error creating event: {str(e)}")
        return {"status": "error", "message": str(e)}


def list_events(tool_context: ToolContext, date_filter: str = None) -> dict:
    """List all calendar events from Firestore, optionally filtered by date.

    Args:
        tool_context: The tool context for state management.
        date_filter: Optional date to filter events by (YYYY-MM-DD format).

    Returns:
        dict: A dictionary with status and list of events on success, or status and message on error.
    """
    try:
        db = get_db()
        events_ref = db.collection("events")
        if date_filter:
            events = events_ref.where("date", "==", date_filter).stream()
        else:
            events = events_ref.stream()

        event_list = [dict(event.to_dict()) for event in events]
        logging.info(f"Listed {len(event_list)} events")
        return {"status": "success", "events": event_list}
    except Exception as e:
        logging.error(f"Error listing events: {str(e)}")
        return {"status": "error", "message": str(e)}


def delete_event(tool_context: ToolContext, event_id: str) -> dict:
    """Delete a calendar event from Firestore.

    Args:
        tool_context: The tool context for state management.
        event_id: The ID of the event to delete.

    Returns:
        dict: A dictionary with status and deleted_id on success, or status and message on error.
    """
    try:
        db = get_db()
        events_ref = db.collection("events").where("id", "==", event_id)
        docs = events_ref.stream()

        for doc in docs:
            db.collection("events").document(doc.id).delete()
            logging.info(f"Deleted event: {event_id}")
            return {"status": "success", "deleted_id": event_id}

        logging.warning(f"Event {event_id} not found")
        return {"status": "error", "message": f"Event {event_id} not found"}
    except Exception as e:
        logging.error(f"Error deleting event: {str(e)}")
        return {"status": "error", "message": str(e)}
