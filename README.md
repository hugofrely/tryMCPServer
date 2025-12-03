# Technical Test - CRM Push Refactoring


## Setup

1. Install `uv` if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or using pip: pip install uv
```

2. Sync dependencies (creates virtual environment and installs dependencies):
```bash
uv sync
```

3. Run the application:
```bash
uv run fastapi dev app/main.py
```

## Usage

Create new push job

```bash
curl -X POST http://localhost:8000/push \
  -H "Content-Type: application/json" \
  -d '{
    "profiles": [
      {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "linkedin_id": "john-doe",
        "phone": "+1234567890",
        "company": "Acme Corp"
      },
      {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com"
      }
    ]
  }'
```

Get push job status

```bash
curl http://127.0.0.1:8000/push/2
```


## Notes

- The HubSpot client is mocked and stores data in memory
- The database is SQLite (file: `crm.db`)
- Focus on architecture, not on adding new features
- Keep the API contract the same (same endpoints, same request/response formats)

