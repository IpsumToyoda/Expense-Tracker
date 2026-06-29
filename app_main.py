from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

from queries import get_expenses, add_expense, delete_expense, update_expense

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

@app.delete("/expenses/{expense_id}")
def remove_expense(expense_id: int):
    deleted = delete_expense(expense_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Expense not found")
    return {"status": "Expense deleted successfully", "id": expense_id}

@app.put("/expenses/{expense_id}")
def update_expense_endpoint(expense_id: int, expense: ExpenseCreate):
    updated = update_expense(
        expense_id,
        expense.title,
        expense.amount,
        expense.category
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Expense not found")

    return updated
