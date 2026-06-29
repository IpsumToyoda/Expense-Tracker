from fastapi import FastAPI
from pydantic import BaseModel

from queries import get_expenses, add_expense

class ExpenseCreate(BaseModel):
    title: str
    amount: float
    category: str | None = None

app = FastAPI()

@app.get("/")
def root():
    return {"status": "API working"}

@app.get("/hello")
def hello():
    return {
        "message": "Hello from FastAPI!",
        "version": "1.0",
        "author": "Firsty"
    }

@app.get("/expenses")
def expenses(category: str | None = None):
    return get_expenses(category=category)

@app.post("/expenses")
def create_expense(expense: ExpenseCreate):
    return add_expense(
        expense.title,
        expense.amount,
        expense.category
    )
