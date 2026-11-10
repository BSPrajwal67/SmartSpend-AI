
let expenseChart = null;

const money = value =>
    "₹" + Number(value || 0).toLocaleString("en-IN", {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

// Load financial summary
async function loadSummary() {
    const response = await fetch("/api/summary");
    const data = await response.json();

    document.getElementById("balance").textContent = money(data.balance);
    document.getElementById("income").textContent = money(data.income);
    document.getElementById("expenses").textContent = money(data.expenses);

    document.getElementById("summary-income").textContent = money(data.income);
    document.getElementById("summary-expenses").textContent = money(data.expenses);
    document.getElementById("summary-balance").textContent = money(data.balance);
}

// Load transactions
async function loadTransactions() {
    const response = await fetch("/api/transactions");
    const transactions = await response.json();

    const list = document.getElementById("transaction-list");

    if (!transactions.length) {
        list.innerHTML = `
            <tr>
                <td colspan="6">No transactions yet. Add your first transaction!</td>
            </tr>`;
        return;
    }

    list.innerHTML = transactions.slice(0, 10).map(t => `
        <tr>
            <td>${escapeHTML(t.title)}</td>
            <td>${escapeHTML(t.category)}</td>
            <td>${escapeHTML(t.date)}</td>
            <td>${escapeHTML(t.transaction_type)}</td>
            <td class="${t.transaction_type === "income" ? "income-text" : "expense-text"}">
                ${t.transaction_type === "income" ? "+" : "-"}${money(t.amount)}
            </td>
            <td>
                <button class="delete-btn" data-id="${Number(t.id)}">Delete</button>
            </td>
        </tr>
    `).join("");

    list.querySelectorAll(".delete-btn").forEach(button => {
        button.addEventListener("click", () => deleteTransaction(button.dataset.id));
    });

    updateChart(transactions);
}

// Prevent HTML injection in transaction descriptions
function escapeHTML(value) {
    return String(value).replace(/[&<>"']/g, char => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[char]);
}

// Add transaction
document.getElementById("transaction-form").addEventListener("submit", async event => {
    event.preventDefault();

    const message = document.getElementById("form-message");

    const payload = {
        title: document.getElementById("title").value.trim(),
        amount: document.getElementById("amount").value,
        transaction_type: document.getElementById("transaction_type").value,
        date: document.getElementById("date").value
    };

    try {
        const response = await fetch("/api/transactions", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to add transaction");
        }

        message.textContent = `Success! AI categorized this as: ${data.category}`;
        message.style.color = "green";

        event.target.reset();
        document.getElementById("date").value = new Date().toISOString().slice(0, 10);

        await refreshDashboard();

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
});

// Delete transaction
async function deleteTransaction(id) {
    if (!confirm("Are you sure you want to delete this transaction?")) return;

    const response = await fetch(`/api/transactions/${id}`, {
        method: "DELETE"
    });

    if (response.ok) {
        await refreshDashboard();
    } else {
        alert("Could not delete transaction.");
    }
}

// AI recommendations
async function loadRecommendations() {
    const response = await fetch("/api/recommendations");
    const data = await response.json();

    const container = document.getElementById("recommendations");

    container.innerHTML = data.recommendations.map(item =>
        `<p>💡 ${escapeHTML(item)}</p>`
    ).join("");
}

// Expense chart
function updateChart(transactions) {
    const totals = {};

    transactions
        .filter(t => t.transaction_type === "expense")
        .forEach(t => {
            totals[t.category] = (totals[t.category] || 0) + Number(t.amount);
        });

    const canvas = document.getElementById("expenseChart");

    if (expenseChart) expenseChart.destroy();

    expenseChart = new Chart(canvas, {
        type: "doughnut",
        data: {
            labels: Object.keys(totals),
            datasets: [{
                data: Object.values(totals),
                backgroundColor: [
                    "#6c63ff", "#ff8c69", "#36b99a",
                    "#ffca58", "#5799e8", "#d77de5",
                    "#72c6d9", "#ef6b91"
                ],
                borderWidth: 2,
                borderColor: "#ffffff"
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}

// Refresh all dashboard data
async function refreshDashboard() {
    await Promise.all([
        loadSummary(),
        loadTransactions(),
        loadRecommendations()
    ]);
}

document.addEventListener("DOMContentLoaded", async () => {
    document.getElementById("date").value =
        new Date().toISOString().slice(0, 10);

    document.getElementById("refresh-ai").addEventListener(
        "click",
        loadRecommendations
    );

    try {
        await refreshDashboard();
    } catch (error) {
        console.error("Dashboard loading failed:", error);
    }
});
