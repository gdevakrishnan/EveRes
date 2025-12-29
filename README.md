# EveRes

EveRes is a small Flask app for event scheduling and resource allocation. It provides a simple UI to create events, register resources, allocate resources to events, and generate utilization reports.

## Features
- User registration and login
- Create and list events with start/end times and descriptions
- Add and list resources (e.g. rooms, equipment)
- Allocate resources to events with conflict detection
- Generate a resource utilization report
- Responsive, purple-themed UI with a landing hero page

## Tech Stack
- Python 3.10+
- Flask
- PyMongo (MongoDB)
- Jinja2 templates
- Static CSS in `static/css/style.css`

## Project Structure
```
EveRes/
├─ app.py
├─ templates/
│  ├─ base.html
│  ├─ index.html
│  ├─ login.html
│  └─ ...
├─ static/
│  └─ css/style.css
└─ README.md
```

## Architecture / Workflow Diagram
```mermaid
flowchart TD
    A[Open Application] --> B{Logged In?}

    B -- No --> C[Login / Register]
    C --> D[Authenticate User]
    D --> E[Dashboard]

    B -- Yes --> E[Dashboard]

    E --> F[Create Events]
    E --> G[Add Resources]
    E --> H[Allocate Resource]

    H --> I{Conflict?}
    I -- Yes --> J[Show Error]
    I -- No --> K[Save Allocation]

    E --> L[Generate Report]

    E --> M[Logout]
    M --> C
```

## Quickstart (Windows)
1. Create a venv and activate it:

```cmd
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies (create `requirements.txt` or install directly):

```cmd
pip install flask pymongo werkzeug
```

3. Create a `.env` file in the project root (or set environment variables):

```
FLASK_SECRET_KEY=your-secret-key
MONGODB_URI=mongodb://localhost:27017
```

4. Run the app:

```cmd
python app.py
```

5. Open `http://127.0.0.1:5000/` in your browser.

## Environment variables
- `FLASK_SECRET_KEY` — session secret key
- `MONGODB_URI` — MongoDB connection string

## UI / Styling Notes
- Primary color: **purple** (variables in `static/css/style.css`)
- Landing hero page at `/` (`templates/index.html`)
- Forms and tables are styled consistently via the stylesheet

## Endpoints
- `/` — Landing hero page (redirects signed-in users to `/events`)
- `/register` — Create a new user
- `/login` — Login
- `/events` — Create and list events
- `/resources` — Add and list resources
- `/allocate` — Allocate resource to an event
- `/report` — Generate utilization report

## Contributing
Contributions welcome — create an issue or a PR with fixes or improvements.

## License
MIT License
