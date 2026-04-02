"""Task management tools for the productivity assistant.

Provides tools to create, list, update, and delete tasks in Firestore.
"""

import logging
import uuid
from datetime import datetime

from google.adk.tools.tool_context import ToolContext

from productivity_assistant.db import get_db

logger = logging.getLogger(__name__)


def create_task(tool_context: ToolContext, title: str, priority: str = "medium", due_date: str = None) -> dict:
    """Create a new task in Firestore.

    Args:
        tool_context: The tool context for state management.
        title: The title of the task.
        priority: The priority level (low, medium, high). Defaults to "medium".
        due_date: Optional due date for the task.

    Returns:
        dict: A dictionary with status and task_id on success, or status and message on error.
    """
    try:
        db = get_db()
        task_id = str(uuid.uuid4())
        task_data = {
            "id": task_id,
            "title": title,
            "priority": priority,
            "due_date": due_date,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat()
        }
        db.collection("tasks").document(task_id).set(task_data)
        logging.info(f"Created task: {task_id} - {title}")
        return {"status": "success", "task_id": task_id, "title": title}
    except Exception as e:
        logging.error(f"Error creating task: {str(e)}")
        return {"status": "error", "message": str(e)}


def list_tasks(tool_context: ToolContext, status_filter: str = None) -> dict:
    """List all tasks from Firestore, optionally filtered by status.

    Args:
        tool_context: The tool context for state management.
        status_filter: Optional status to filter tasks by (e.g., "pending", "completed").

    Returns:
        dict: A dictionary with status and list of tasks on success, or status and message on error.
    """
    try:
        db = get_db()
        tasks_ref = db.collection("tasks")
        if status_filter:
            tasks = tasks_ref.where("status", "==", status_filter).stream()
        else:
            tasks = tasks_ref.stream()

        task_list = [dict(task.to_dict()) for task in tasks]
        logging.info(f"Listed {len(task_list)} tasks")
        return {"status": "success", "tasks": task_list}
    except Exception as e:
        logging.error(f"Error listing tasks: {str(e)}")
        return {"status": "error", "message": str(e)}


def update_task_status(tool_context: ToolContext, task_id: str, new_status: str) -> dict:
    """Update the status of an existing task.

    Args:
        tool_context: The tool context for state management.
        task_id: The ID of the task to update.
        new_status: The new status to set (e.g., "pending", "in_progress", "completed").

    Returns:
        dict: A dictionary with status, task_id, and new_status on success, or status and message on error.
    """
    try:
        db = get_db()
        tasks_ref = db.collection("tasks").where("id", "==", task_id)
        docs = tasks_ref.stream()

        for doc in docs:
            db.collection("tasks").document(doc.id).update({"status": new_status})
            logging.info(f"Updated task {task_id} status to {new_status}")
            return {"status": "success", "task_id": task_id, "new_status": new_status}

        logging.warning(f"Task {task_id} not found")
        return {"status": "error", "message": f"Task {task_id} not found"}
    except Exception as e:
        logging.error(f"Error updating task status: {str(e)}")
        return {"status": "error", "message": str(e)}


def delete_task(tool_context: ToolContext, task_id: str) -> dict:
    """Delete a task from Firestore.

    Args:
        tool_context: The tool context for state management.
        task_id: The ID of the task to delete.

    Returns:
        dict: A dictionary with status and deleted_id on success, or status and message on error.
    """
    try:
        db = get_db()
        tasks_ref = db.collection("tasks").where("id", "==", task_id)
        docs = tasks_ref.stream()

        for doc in docs:
            db.collection("tasks").document(doc.id).delete()
            logging.info(f"Deleted task: {task_id}")
            return {"status": "success", "deleted_id": task_id}

        logging.warning(f"Task {task_id} not found")
        return {"status": "error", "message": f"Task {task_id} not found"}
    except Exception as e:
        logging.error(f"Error deleting task: {str(e)}")
        return {"status": "error", "message": str(e)}
