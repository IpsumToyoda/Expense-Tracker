import datetime
import os

import requests
import streamlit as st


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"


def get_api_base_url():
    try:
        api_base_url = st.secrets.get("API_BASE_URL")
    except Exception:
        api_base_url = None

    return (api_base_url or os.getenv("API_BASE_URL", DEFAULT_API_BASE_URL)).rstrip("/")


def api_request(method, path, **kwargs):
    url = f"{get_api_base_url()}{path}"

    try:
        response = requests.request(method, url, timeout=10, **kwargs)
        response.raise_for_status()
    except requests.RequestException as error:
        st.error(f"API request failed: {error}")
        st.stop()

    if not response.content:
        return None

    return response.json()


def compact_params(params):
    return {
        key: value.isoformat() if isinstance(value, datetime.date) else value
        for key, value in params.items()
        if value is not None
    }


def format_currency(value):
    value = float(value or 0)
    text = f"{value:.2f}"
    return text.rstrip("0").rstrip(".")


def get_categories_from_api():
    return api_request("GET", "/categories")


def get_expenses_from_api(filters):
    return api_request("GET", "/expenses", params=compact_params(filters))


def get_expense_total_from_api(filters):
    result = api_request("GET", "/expenses/total", params=compact_params(filters))
    return result["total"]


def get_expense_by_id_from_api(expense_id):
    return api_request("GET", f"/expenses/{expense_id}")


def add_expense_via_api(title, amount, category, expense_date, notes):
    payload = {
        "title": title,
        "amount": amount,
        "category": category,
        "expense_date": expense_date.isoformat(),
        "notes": notes,
    }
    return api_request("POST", "/expenses", json=payload)


def update_expense_via_api(expense_id, title, amount, category, expense_date, notes):
    payload = {
        "title": title,
        "amount": amount,
        "category": category,
        "expense_date": expense_date.isoformat(),
        "notes": notes,
    }
    return api_request("PUT", f"/expenses/{expense_id}", json=payload)


def delete_expense_via_api(expense_id):
    return api_request("DELETE", f"/expenses/{expense_id}")


def render_add_expense_form():
    with st.expander("Add a new expense"):
        with st.form("expense_form"):
            title = st.text_input("Title", max_chars=100)
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=0.01,
                format="%g",
            )
            category = st.text_input("Category")
            expense_date = st.date_input("Date", value=datetime.date.today())
            notes = st.text_area("Notes", max_chars=300)
            submitted = st.form_submit_button("Save expense")

            if submitted:
                if not title.strip():
                    st.error("Expense title is required.")
                elif amount <= 0:
                    st.error("Amount must be greater than zero.")
                else:
                    add_expense_via_api(
                        title.strip(),
                        amount,
                        category.strip() or None,
                        expense_date,
                        notes.strip() or None,
                    )
                    st.success("Expense saved.")
                    st.rerun()


def build_filters():
    with st.sidebar.expander("Filters", expanded=True):
        category = st.selectbox(
            "Category",
            options=["All"] + get_categories_from_api(),
            index=0,
        )

        enable_start_date = st.checkbox("Filter from date", value=False)
        start_date = None
        if enable_start_date:
            start_date = st.date_input("Start date", value=datetime.date.today(), key="start_date")

        enable_end_date = st.checkbox("Filter until date", value=False)
        end_date = None
        if enable_end_date:
            end_date = st.date_input("End date", value=datetime.date.today(), key="end_date")

        min_amount = st.number_input(
            "Min amount",
            min_value=0.0,
            step=0.01,
            format="%g",
            key="min_amount",
        )
        max_amount = st.number_input(
            "Max amount",
            min_value=0.0,
            step=0.01,
            format="%g",
            key="max_amount",
        )

    return {
        "category": None if category == "All" else category,
        "start_date": start_date,
        "end_date": end_date,
        "min_amount": min_amount if min_amount > 0 else None,
        "max_amount": max_amount if max_amount > 0 else None,
    }


def render_edit_expense_form(expense):
    st.subheader("Edit expense")
    with st.form("edit_expense_form"):
        edit_title = st.text_input("Title", value=expense["title"])
        edit_amount = st.number_input(
            "Amount",
            min_value=0.0,
            step=0.01,
            format="%g",
            value=float(expense["amount"]),
        )
        edit_category = st.text_input("Category", value=expense["category"] or "")
        edit_date = st.date_input(
            "Date",
            value=datetime.date.fromisoformat(expense["expense_date"]),
        )
        edit_notes = st.text_area("Notes", value=expense["notes"] or "")
        update_submitted = st.form_submit_button("Update expense")

        if update_submitted:
            if not edit_title.strip():
                st.error("Expense title is required.")
            elif edit_amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                update_expense_via_api(
                    expense["id"],
                    edit_title.strip(),
                    edit_amount,
                    edit_category.strip() or None,
                    edit_date,
                    edit_notes.strip() or None,
                )
                st.success("Expense updated.")
                st.session_state.editing_id = None
                st.rerun()

    if st.button("Cancel edit", key="cancel_edit"):
        st.session_state.editing_id = None
        st.rerun()


def render_expense_list(expenses):
    if not expenses:
        st.info("No expenses found. Add one using the form above.")
        return

    for expense in expenses:
        st.write(
            f"**{expense['title']}** — {format_currency(expense['amount'])} | "
            f"{expense['expense_date']} | {expense['category'] or 'No category'}"
        )
        if expense["notes"]:
            st.caption(expense["notes"])

        cols = st.columns([1, 1])
        with cols[0]:
            if st.button("Edit", key=f"edit_{expense['id']}"):
                st.session_state.editing_id = expense["id"]
                st.rerun()
        with cols[1]:
            if st.button("Delete", key=f"delete_{expense['id']}"):
                delete_expense_via_api(expense["id"])
                st.rerun()

        st.write("---")


def main():
    st.set_page_config(page_title="Expense Tracker", page_icon="💰")
    st.title("Expense Tracker")
    st.markdown("Track your spending with categories, dates, and notes.")

    render_add_expense_form()

    filters = build_filters()
    if filters["start_date"] and filters["end_date"] and filters["start_date"] > filters["end_date"]:
        st.error("Start date cannot be later than end date.")
        st.stop()

    expenses = get_expenses_from_api(filters)
    total = get_expense_total_from_api(filters)

    editing_id = st.session_state.get("editing_id")
    editing_expense = get_expense_by_id_from_api(editing_id) if editing_id is not None else None

    if editing_expense:
        render_edit_expense_form(editing_expense)

    st.subheader("Recent expenses")
    st.metric("Total spent", format_currency(total))
    render_expense_list(expenses)


if __name__ == "__main__":
    main()
