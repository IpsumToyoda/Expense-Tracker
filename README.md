# Expense Tracker

A personal expense tracker with a Streamlit frontend, FastAPI backend, and PostgreSQL database.

Target architecture:

```text
Streamlit Cloud -> FastAPI API -> Supabase PostgreSQL
```

## Features

- Add, edit, and delete expenses
- Filter by category, date range, and amount
- Track total spending
- Store categories, dates, and notes
- Access the same data through HTTP API endpoints

## Project Structure

```text
Expense_tracker/
├── main.py              # Streamlit frontend, API client only
├── app_main.py          # FastAPI backend
├── queries.py           # PostgreSQL CRUD queries
├── schema.py            # Database schema creation
├── db.py                # Database connection
├── requirements.txt     # Runtime dependencies
├── requirements-dev.txt # Development dependencies
├── .env.example         # Local environment template
└── README.md
```

## Local Setup

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` for local development. You can use either a single Supabase/PostgreSQL connection string:

```env
DATABASE_URL=postgresql://user:password@host:5432/postgres
API_BASE_URL=http://127.0.0.1:8000
```

Or separate database variables:

```env
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=your_supabase_host
DB_PORT=5432
API_BASE_URL=http://127.0.0.1:8000
```

Start the FastAPI backend:

```bash
uvicorn app_main:app --reload
```

Start the Streamlit frontend in a second terminal:

```bash
streamlit run main.py
```

Open:

- Streamlit app: `http://localhost:8501`
- API docs: `http://127.0.0.1:8000/docs`
- API health: `http://127.0.0.1:8000/health`

## API Endpoints

- `GET /health`
- `GET /categories`
- `GET /expenses`
- `GET /expenses/total`
- `GET /expenses/{expense_id}`
- `POST /expenses`
- `PUT /expenses/{expense_id}`
- `DELETE /expenses/{expense_id}`

Supported filters for `GET /expenses` and `GET /expenses/total`:

- `category`
- `start_date`
- `end_date`
- `min_amount`
- `max_amount`
- `limit` for `/expenses`

## Online Deployment

Since the database is in Supabase and Streamlit Cloud is already available, the missing online piece is publishing FastAPI.

Deploy FastAPI to a service such as Render, Railway, Fly.io, or Google Cloud Run. The FastAPI service needs database secrets:

```env
DATABASE_URL=postgresql://user:password@host:5432/postgres
```

Then set this secret in Streamlit Cloud:

```env
API_BASE_URL=https://your-fastapi-service.example.com
```

The Streamlit app should not receive database credentials in production. Only the FastAPI backend should connect to Supabase.

## Security Notes

- Do not commit `.env`.
- Keep Supabase credentials only in backend deployment secrets.
- Streamlit Cloud should store only `API_BASE_URL`.
- CORS is currently open for simple deployment. Restrict it later to your Streamlit Cloud URL before treating the API as production-ready.
