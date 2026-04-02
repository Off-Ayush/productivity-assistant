# Personal Productivity Assistant

A multi-agent AI system built with Google ADK for managing tasks, schedules, and notes. This system coordinates multiple specialized agents to handle user requests and stores structured data in Google Firestore. Deployable as an API on Google Cloud Run.

## Architecture

The system consists of 6 agents working together:

| Agent | Role |
|-------|------|
| **greeter** (root) | Welcomes users, saves prompts to state, routes to workflow |
| **task_agent** | Manages tasks: create, list, update status, delete |
| **calendar_agent** | Manages calendar events: create, list, delete |
| **notes_agent** | Manages notes: create, list, search |
| **formatter_agent** | Synthesizes outputs into clean, friendly responses |
| **productivity_workflow** | Sequential agent orchestrating task → calendar → notes → formatter |

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd productivity_assistant
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create environment file:
   ```bash
   cp .env.example .env
   ```

4. Fill in your GCP values in `.env`:
   ```
   PROJECT_ID=your-gcp-project-id
   PROJECT_NUMBER=your-gcp-project-number
   SA_NAME=productivity-assistant-sa
   SERVICE_ACCOUNT=productivity-assistant-sa@your-gcp-project-id.iam.gserviceaccount.com
   MODEL=gemini-2.0-flash
   ```

5. Run the agent locally:
   ```bash
   adk run productivity_assistant
   ```

## Deployment

Deploy to Google Cloud Run with:

```bash
uvx --from google-adk==1.14.0 \
  adk deploy cloud_run \
    --project=$PROJECT_ID \
    --region=us-central1 \
    --service_name=productivity-assistant \
    --with_ui \
    . \
    -- \
    --service-account=$SERVICE_ACCOUNT
```

## Example Prompts

Try these example prompts:

1. "Add a task to prepare my presentation slides, high priority"
2. "Schedule a team meeting tomorrow at 3pm"
3. "Save a note about the project architecture decisions"
4. "Show me all my pending tasks"
5. "Search my notes for anything about deployment"
