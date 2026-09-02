# PW Vision

An independent educational learning platform built with Python and Flask.

## Features
- Responsive learning homepage
- Course catalogue API
- Registration and login
- Password hashing and sessions
- SQLite database
- Course enrollment
- Progress tracking
- Test-result storage
- Health endpoint

## Run locally

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000`.

## API
- `GET /api/courses`
- `POST /api/register`
- `POST /api/login`
- `POST /api/logout`
- `GET /api/me`
- `GET /api/dashboard`
- `POST /api/enroll/<course_id>`
- `PATCH /api/progress/<course_id>`
- `POST /api/tests`
- `GET /health`

The UI is an original PW Vision design inspired by common modern education-platform patterns, not an exact copy of another company's website or branding.
