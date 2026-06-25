# Deployment Guide: Running Without Hosting a Database

This document explains how the published Expense Tracker application works when you don't host your database.

## The Problem

If you publish only the code to GitHub **without** hosting a database:

- ✗ Users clone the repo
- ✗ Users run `streamlit run main.py`
- ✗ **App crashes** with: `psycopg2.OperationalError: could not connect to server`

**Why?** The app expects a PostgreSQL database to be running and accessible. Without it, the connection fails immediately.

---

## Solution 1: Streamlit Cloud + Cloud Database (Recommended for Beginners)

This is the **easiest** approach to share your app with others.

### Step 1: Set Up a Cloud Database

Choose one:

**AWS RDS (PostgreSQL)**
- Go to [AWS RDS Console](https://console.aws.amazon.com/rds/)
- Create a new PostgreSQL database
- Get the endpoint: `your-db.c1234567890.us-east-1.rds.amazonaws.com`
- Note the username and password

**DigitalOcean Managed Database**
- Go to [DigitalOcean Console](https://cloud.digitalocean.com/)
- Create a managed PostgreSQL database
- Get the connection string
- Simple and affordable (~$15/month)

**Heroku Postgres** (simpler, but Heroku is paid now)
- Historically used, but now requires paid plans

**Supabase** (free tier available)
- Go to [supabase.com](https://supabase.com)
- Create a new project (free)
- PostgreSQL is included
- Very beginner-friendly

### Step 2: Push Code to GitHub

```bash
git init
git add .
git commit -m "Initial Expense Tracker"
git push origin main
```

**Important:** `.env` is in `.gitignore`, so your passwords won't be committed.

### Step 3: Deploy to Streamlit Cloud

1. Go to [streamlit.io/cloud](https://streamlit.io/cloud)
2. Sign up with GitHub
3. Click "New app"
4. Connect your repository
5. **Add Secrets** (this is where credentials go instead of `.env`):
   - Click "Advanced settings" → "Secrets"
   - Add each variable:
     ```
     DB_NAME = my_expense_db
     DB_USER = postgres
     DB_PASSWORD = my_secure_password
     DB_HOST = my-db.c1234567890.us-east-1.rds.amazonaws.com
     DB_PORT = 5432
     ```

### Step 4: Done!

Your app is now live at:
```
https://my-expense-tracker.streamlit.app
```

**Everyone can use it** by visiting that URL. It connects to your cloud database.

---

## Solution 2: Docker + Cloud Hosting

For more control and customization.

### Step 1: Create Dockerfile

File: `Dockerfile` (in project root)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY Expense_tracker/ ./Expense_tracker/
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "Expense_tracker/main.py"]
```

### Step 2: Create .dockerignore

```
venv/
.env
__pycache__/
*.pyc
.git
.gitignore
```

### Step 3: Build & Push to Docker Hub

```bash
# Build image
docker build -t your-username/expense-tracker:latest .

# Push to Docker Hub (requires account)
docker push your-username/expense-tracker:latest
```

### Step 4: Deploy to Cloud

**Heroku** (if you have credits):
```bash
heroku login
heroku container:push web
heroku container:release web
```

**Google Cloud Run** (free tier):
```bash
gcloud run deploy expense-tracker \
  --image gcr.io/PROJECT-ID/expense-tracker \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**AWS ECS**:
- Go to AWS ECS Console
- Create a task definition pointing to your Docker image
- Set environment variables for database secrets

---

## Solution 3: Tell Users to Use Their Own Database

For **open-source projects**, document clearly:

### In README.md:

```markdown
## For Users: How to Run Locally

1. **Install PostgreSQL:**
   - Download from [postgresql.org](https://www.postgresql.org/download/)
   - Create a database: `createdb expense_tracker`

2. **Clone and setup:**
   ```bash
   git clone <repo>
   cd Expense_tracker
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

3. **Create `.env` file:**
   ```
   cp .env.example .env
   ```

4. **Edit `.env` with your local credentials:**
   ```
   DB_NAME=expense_tracker
   DB_USER=postgres
   DB_PASSWORD=your_local_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

5. **Run:**
   ```bash
   streamlit run Expense_tracker/main.py
   ```
```

---

## Comparison of Solutions

| Solution | Cost | Difficulty | Who Can Use | Setup Time |
|----------|------|------------|-----------|-----------|
| **Streamlit Cloud + Cloud DB** | $0-30/mo* | ⭐ Easy | Anyone with URL | 15 min |
| **Docker + Cloud Hosting** | $5-50/mo | ⭐⭐ Medium | Developers | 30 min |
| **User's Own Database** | $0 | ⭐⭐⭐ Hard | Technical users | Variable |

*Free tier available for Supabase or small workloads

---

## Security Best Practices

### ✅ DO:

- ✓ Store passwords in `.env` (locally) or Streamlit Secrets (on cloud)
- ✓ Never commit `.env` to Git
- ✓ Use strong database passwords
- ✓ Rotate credentials periodically
- ✓ Use HTTPS for cloud connections
- ✓ Restrict database access by IP (if possible)

### ❌ DON'T:

- ✗ Hardcode passwords in `main.py` or other files
- ✗ Share `.env` files
- ✗ Commit `.env` to GitHub
- ✗ Use the same password everywhere
- ✗ Run database on a public IP without auth

---

## Example: Streamlit Cloud Deployment in 5 Minutes

### Prerequisites:
- GitHub account
- Supabase account (free)

### Steps:

1. **Create Supabase project:**
   - Visit [supabase.com](https://supabase.com)
   - Click "New Project"
   - Copy connection string

2. **Update code:**
   ```python
   # In db.py, no changes needed! Just use .env variables
   ```

3. **Push to GitHub:**
   ```bash
   git push origin main
   ```

4. **Deploy to Streamlit Cloud:**
   - Visit [streamlit.io/cloud](https://streamlit.io/cloud)
   - Connect your repo
   - Add Supabase credentials in Secrets
   - ✅ Live!

---

## FAQ

### Q: Do I have to host a database?

**A:** No. Users can run locally with their own database. But hosting a database lets anyone use your app without setup.

### Q: Is Streamlit Cloud free?

**A:** Yes, for public apps with moderate traffic. Private apps or heavy usage require a paid tier.

### Q: Can I use SQLite instead of PostgreSQL?

**A:** Yes! Modify `db.py` and `queries.py` to use `sqlite3`. SQLite doesn't need a separate server. But you'll need to handle file storage carefully on cloud platforms.

### Q: How do I backup my database?

**A:** Use your cloud provider's built-in backup:
- AWS RDS: Automated snapshots
- DigitalOcean: Managed backups
- Supabase: Automatic backups

### Q: What if my Streamlit Cloud app crashes?

**A:** Check logs:
1. Go to Streamlit Cloud dashboard
2. Click "Manage app"
3. View "Logs"
4. Usually it's a database connection issue

---

## Next Steps

1. **Choose your deployment method** (Streamlit Cloud recommended)
2. **Set up a cloud database** (Supabase is easiest)
3. **Test locally** with cloud database credentials
4. **Deploy to Streamlit Cloud**
5. **Share the URL** with friends

---

For questions or issues, refer to:
- [Streamlit Docs](https://docs.streamlit.io)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Supabase Docs](https://supabase.com/docs)
