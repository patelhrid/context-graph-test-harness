# Taskly API

A simple task management REST API.

## Stack
- **Language**: Python 3.11
- **Framework**: Flask
- **Database**: PostgreSQL
- **Auth**: JWT tokens (stateless, 24-hour expiry)
- **Deployment**: AWS EC2 (us-east-1)

## Running the server

```bash
python src/main.py
```

The server starts on **port 3000** by default.

## API Overview

| Method | Endpoint         | Description         |
|--------|-----------------|---------------------|
| POST   | /auth/login     | Get a JWT token     |
| GET    | /tasks/         | List all tasks      |
| POST   | /tasks/         | Create a task       |
| DELETE | /tasks/:id      | Delete a task       |

## Frontend
The frontend is a React SPA living in the `/client` directory.
It communicates with this API over HTTP and stores state locally using Redux.

## Team
Backend owned by @kirill. Frontend owned by @kai.
