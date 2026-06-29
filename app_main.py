import datetime
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from queries import (
    add_expense,
    delete_expense,
    get_categories,
    get_expense_by_id,
    get_expense_total,
    get_expenses,
    update_expense,
)
from schema import create_tables


class ExpenseIn(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    category: str | None = None
    expense_date: datetime.date | None = None
    notes: str | None = Field(default=None, max_length=300)


app = FastAPI(title="Expense Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    create_tables()


def serialize_expense(expense):
    if expense is None:
        return None

    return {
        "id": expense["id"],
        "title": expense["title"],
        "amount": float(expense["amount"]),
        "category": expense["category"],
        "expense_date": expense["expense_date"].isoformat(),
        "notes": expense["notes"],
        "created_at": expense["created_at"].isoformat() if expense.get("created_at") else None,
    }


def clean_expense(expense: ExpenseIn):
    title = expense.title.strip()
    if not title:
        raise HTTPException(status_code=422, detail="Expense title is required")

    return {
        "title": title,
        "amount": expense.amount,
        "category": expense.category.strip() if expense.category and expense.category.strip() else None,
        "expense_date": expense.expense_date,
        "notes": expense.notes.strip() if expense.notes and expense.notes.strip() else None,
    }


@app.get("/")
def root():
    return {"status": "ok", "service": "Expense Tracker API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/categories")
def categories():
    return get_categories()


@app.get("/expenses")
def expenses(
    category: str | None = None,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    min_amount: float | None = Query(default=None, ge=0),
    max_amount: float | None = Query(default=None, ge=0),
    limit: int = Query(default=200, ge=1, le=500),
):
    rows = get_expenses(
        limit=limit,
        category=category,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
    )
    return [serialize_expense(row) for row in rows]


@app.get("/expenses/total")
def expenses_total(
    category: str | None = None,
    start_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    min_amount: float | None = Query(default=None, ge=0),
    max_amount: float | None = Query(default=None, ge=0),
):
    total = get_expense_total(
        category=category,
        start_date=start_date,
        end_date=end_date,
        min_amount=min_amount,
        max_amount=max_amount,
    )

    if isinstance(total, Decimal):
        total = float(total)

    return {"total": total}


@app.get("/expenses/{expense_id}")
def expense_by_id(expense_id: int):
    expense = get_expense_by_id(expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return serialize_expense(expense)


@app.post("/expenses", status_code=201)
def create_expense(expense: ExpenseIn):
    cleaned = clean_expense(expense)
    created = add_expense(
        cleaned["title"],
        cleaned["amount"],
        cleaned["category"],
        cleaned["expense_date"],
        cleaned["notes"],
    )
    return serialize_expense(created)


@app.put("/expenses/{expense_id}")
def update_expense_endpoint(expense_id: int, expense: ExpenseIn):
    cleaned = clean_expense(expense)
    updated = update_expense(
        expense_id,
        cleaned["title"],
        cleaned["amount"],
        cleaned["category"],
        cleaned["expense_date"],
        cleaned["notes"],
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")

    return serialize_expense(updated)


@app.delete("/expenses/{expense_id}")
def remove_expense(expense_id: int):
    deleted = delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"status": "deleted", "id": expense_id}
