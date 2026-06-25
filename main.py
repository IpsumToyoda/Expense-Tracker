import datetime

import streamlit as st

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


def format_currency(value):
    value = float(value or 0)
    text = f"{value:.2f}"
    return text.rstrip("0").rstrip(".")


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
                    add_expense(
                        title.strip(),
                        amount,
                        category.strip() or None,
                        expense_date,
                        notes.strip() or None,
                    )
                    st.success("Expense saved.")
                    st.experimental_rerun()


def build_filters():
    with st.sidebar.expander("Filters", expanded=True):
        category = st.selectbox(
            "Category",
            options=["All"] + get_categories(),
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
        edit_date = st.date_input("Date", value=expense["expense_date"])
        edit_notes = st.text_area("Notes", value=expense["notes"] or "")
        update_submitted = st.form_submit_button("Update expense")

        if update_submitted:
            if not edit_title.strip():
                st.error("Expense title is required.")
            elif edit_amount <= 0:
                st.error("Amount must be greater than zero.")
            else:
                update_expense(
                    expense["id"],
                    edit_title.strip(),
                    edit_amount,
                    edit_category.strip() or None,
                    edit_date,
                    edit_notes.strip() or None,
                )
                st.success("Expense updated.")
                st.session_state.editing_id = None
                st.experimental_rerun()

    if st.button("Cancel edit", key="cancel_edit"):
        st.session_state.editing_id = None
        st.experimental_rerun()


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
                st.experimental_rerun()
        with cols[1]:
            if st.button("Delete", key=f"delete_{expense['id']}"):
                delete_expense(expense["id"])
                st.experimental_rerun()

        st.write("---")


def main():
    create_tables()

    st.set_page_config(page_title="Expense Tracker", page_icon="💰")
    st.title("Expense Tracker")
    st.markdown("Track your spending with categories, dates, and notes.")

    render_add_expense_form()

    filters = build_filters()
    if filters["start_date"] and filters["end_date"] and filters["start_date"] > filters["end_date"]:
        st.error("Start date cannot be later than end date.")

    expenses = get_expenses(**filters)
    total = get_expense_total(**filters)

    editing_id = st.session_state.get("editing_id")
    editing_expense = get_expense_by_id(editing_id) if editing_id is not None else None

    if editing_expense:
        render_edit_expense_form(editing_expense)

    st.subheader("Recent expenses")
    st.metric("Total spent", format_currency(total))
    render_expense_list(expenses)


if __name__ == "__main__":
    main()
