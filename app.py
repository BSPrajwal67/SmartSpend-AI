
from flask import Flask, render_template, request, jsonify
from datetime import date
import database
from ai_engine import categorize_transaction

app = Flask(__name__)

# Initialize database
database.init_db()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/transactions")
def transactions_page():
    return render_template("transactions.html")


# Get all transactions
@app.route("/api/transactions", methods=["GET"])
def get_all_transactions():
    transactions = database.get_transactions()
    return jsonify(transactions)


# Add a new transaction
@app.route("/api/transactions", methods=["POST"])
def create_transaction():

    data = request.get_json(silent=True) or {}

    title = str(data.get("title", "")).strip()

    try:
        amount = float(data.get("amount", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid amount"}), 400

    transaction_type = data.get("transaction_type", "expense")

    if not title:
        return jsonify({"error": "Title is required"}), 400

    if amount <= 0:
        return jsonify({"error": "Amount must be positive"}), 400

    if transaction_type not in ["income", "expense"]:
        return jsonify({"error": "Invalid transaction type"}), 400

    # AI automatic categorization
    if transaction_type == "income":
        category = "Income"
    else:
        category = categorize_transaction(title)

    transaction_date = data.get("date") or date.today().isoformat()

    try:
        date.fromisoformat(transaction_date)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date"}), 400

    database.add_transaction(
        title,
        amount,
        transaction_type,
        category,
        transaction_date
    )

    return jsonify({
        "message": "Transaction added successfully",
        "category": category
    }), 201


# Delete a transaction
@app.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
def remove_transaction(transaction_id):

    database.delete_transaction(transaction_id)

    return jsonify({
        "message": "Transaction deleted successfully"
    })


# Financial summary
@app.route("/api/summary")
def financial_summary():

    summary = database.get_summary()

    return jsonify(summary)


# AI financial recommendations
@app.route("/api/recommendations")
def recommendations():

    transactions = database.get_transactions()
    summary = database.get_summary()

    expenses = [
        t for t in transactions
        if t["transaction_type"] == "expense"
    ]

    category_totals = {}

    for transaction in expenses:
        category = transaction["category"]

        category_totals[category] = (
            category_totals.get(category, 0)
            + transaction["amount"]
        )

    suggestions = []

    if not expenses:
        suggestions.append(
            "Start adding expenses to receive personalized financial advice."
        )

    else:
        if summary["income"] > 0:
            savings_rate = (
                summary["balance"] / summary["income"]
            ) * 100

            if savings_rate < 20:
                suggestions.append(
                    "Your savings rate is below 20%. "
                    "Try reducing non-essential expenses."
                )
            else:
                suggestions.append(
                    "Great! Your savings rate is "
                    f"{savings_rate:.1f}%. Keep it up."
                )

        if category_totals:
            highest_category = max(
                category_totals,
                key=category_totals.get
            )

            highest_amount = category_totals[highest_category]

            suggestions.append(
                f"Your highest spending category is "
                f"{highest_category} (Rs. {highest_amount:.2f}). "
                "Review this category for possible savings."
            )

    return jsonify({
        "recommendations": suggestions,
        "category_spending": category_totals
    })


if __name__ == "__main__":
    print("SmartSpend AI server starting...")
    app.run(debug=True)
