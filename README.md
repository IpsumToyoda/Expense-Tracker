# Expense Tracker

A simple web application for tracking personal expenses. Built with **Streamlit** (frontend) and **PostgreSQL** (database).

## Features

- ✅ Add, edit, and delete expenses
- ✅ Filter by category, date range, and amount
- ✅ Track spending totals
- ✅ Categorize expenses
- ✅ Add notes to expenses

## Prerequisites

- Python 3.8 or later
- PostgreSQL database (local or remote)
- Virtual environment (recommended)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Expense_tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:
- **Windows**: `venv\Scripts\activate`
- **Mac/Linux**: `source venv/bin/activate`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure database connection

Create a `.env` file in the `Expense_tracker/` directory:

```bash
cp .env.example .env
```

Edit `.env` and fill in your PostgreSQL credentials:

```
DB_NAME=your_database_name
DB_USER=your_postgres_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 5. Run the application

```bash
streamlit run main.py
```

The app will open in your browser at `http://localhost:8501`.

## Project Structure

```
Expense_tracker/
├── main.py              # Streamlit UI and main application logic
├── queries.py           # Database queries (CRUD operations)
├── schema.py            # Database schema creation
├── db.py                # Database connection
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Database Schema

The application uses a single `expenses` table:

```sql
CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount >= 0),
    category TEXT,
    expense_date DATE NOT NULL DEFAULT CURRENT_DATE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);
```

## How to Use

### Add an Expense

1. Click on the "Add a new expense" expander
2. Fill in the title, amount, category, date, and notes
3. Click "Save expense"

### Filter Expenses

1. Open the "Filters" panel in the sidebar
2. Select a category, date range, and/or amount range
3. Filters are applied automatically as you change them

### Edit an Expense

1. Click the "Edit" button next to an expense
2. Modify the fields in the edit form
3. Click "Update expense"

### Delete an Expense

1. Click the "Delete" button next to an expense
2. The expense will be removed immediately

## Deployment

### Local Deployment

The application is designed to run locally and connect to a local PostgreSQL database:

```bash
streamlit run main.py
```

### How the Published App Works (Without Hosting the Database)

**Important:** If you publish the code without publishing the database, the app **will not work out of the box** for other users.

Here are your options:

#### Option 1: Cloud Database + Cloud App Hosting (Recommended)

This is the best approach for sharing your app:

1. **Set up a cloud database:**
   - AWS RDS (PostgreSQL)
   - DigitalOcean Managed Database
   - Heroku Postgres
   - MongoDB Atlas
   - Google Cloud SQL

2. **Deploy to Streamlit Cloud (free):**
   - Push code to GitHub (`.env` is in `.gitignore`, so it won't be committed)
   - Go to [streamlit.io/cloud](https://streamlit.io/cloud)
   - Connect your GitHub repository
   - Add your database secrets in the Streamlit Cloud dashboard:
     ```
     DB_NAME = your_db_name
     DB_USER = your_user
     DB_PASSWORD = your_password
     DB_HOST = cloud-db-host.com
     DB_PORT = 5432
     ```

3. **Your app will work for everyone!**
   - Users visit the Streamlit Cloud URL
   - App connects to your cloud database
   - Everyone can use the same data

#### Option 2: Docker + Container Registry

1. Create `Dockerfile`:
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY . .
   RUN pip install -r requirements.txt
   EXPOSE 8501
   CMD ["streamlit", "run", "main.py"]
   ```

2. Deploy to:
   - Docker Hub
   - AWS ECS
   - Google Cloud Run
   - Azure Container Instances

#### Option 3: Tell Users to Use Their Own Database

If you don't want to host a database, document this clearly in the README:

```markdown
## For Users

To run this app locally:
1. Set up PostgreSQL locally
2. Create a `.env` file with your credentials
3. Run `streamlit run main.py`
```

### Important: What Happens Without a Database

If someone clones your project without a database set up:

- The app will **crash** with a connection error
- PostgreSQL must be running and accessible
- The `.env` file must have valid credentials
- The database must exist

### ⚠️ Security Notes

**NEVER commit `.env` to version control!**

- `.gitignore` already excludes `.env`
- Use `.env.example` as a template
- Store sensitive data only in environment variables
- On cloud platforms (Streamlit Cloud, Heroku, etc.), use their secrets management tools

## Project Structure

```
Expense_tracker/
├── main.py              # Streamlit UI and main application logic
├── queries.py           # Database queries (CRUD operations)
├── schema.py            # Database schema creation
├── db.py                # Database connection
├── requirements.txt     # Python dependencies (pinned versions)
├── requirements-dev.txt # Development dependencies (optional)
├── .env.example         # Example environment variables
├── .gitignore           # Git ignore rules
└── README.md            # This file
```

## Troubleshooting

### Connection refused

- Ensure PostgreSQL is running
- Check `.env` values: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`
- Verify the database exists

### Module not found

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

### Port 8501 already in use

- Run on a different port: `streamlit run main.py --server.port=8502`

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to submit issues or pull requests to improve this project!
