
import re
import math
from collections import Counter, defaultdict


# Training dataset for financial transactions
TRAINING_DATA = [
    ("swiggy food order", "Food"),
    ("zomato restaurant dinner", "Food"),
    ("pizza burger coffee", "Food"),
    ("grocery supermarket vegetables", "Food"),
    ("hotel breakfast lunch", "Food"),

    ("uber cab ride", "Transport"),
    ("ola taxi booking", "Transport"),
    ("petrol diesel fuel", "Transport"),
    ("bus ticket metro", "Transport"),
    ("train railway ticket", "Transport"),

    ("amazon shopping purchase", "Shopping"),
    ("flipkart online order", "Shopping"),
    ("clothes shoes shopping", "Shopping"),
    ("mobile phone accessories", "Shopping"),

    ("college tuition fees", "Education"),
    ("school university payment", "Education"),
    ("books stationery course", "Education"),

    ("electricity bill payment", "Utilities"),
    ("water bill internet recharge", "Utilities"),
    ("mobile phone bill", "Utilities"),

    ("movie cinema ticket", "Entertainment"),
    ("netflix subscription", "Entertainment"),
    ("concert game ticket", "Entertainment"),

    ("hospital doctor medicine", "Healthcare"),
    ("pharmacy medical expenses", "Healthcare"),
    ("health checkup treatment", "Healthcare"),

    ("monthly salary income", "Income"),
    ("freelance payment received", "Income"),
    ("business profit earnings", "Income")
]


class TransactionClassifier:

    def __init__(self):
        self.word_counts = defaultdict(Counter)
        self.category_counts = Counter()
        self.vocabulary = set()
        self.total_samples = 0

        self.train()

    def tokenize(self, text):
        return re.findall(r"[a-z]+", text.lower())

    def train(self):

        for text, category in TRAINING_DATA:

            words = self.tokenize(text)

            self.category_counts[category] += 1
            self.total_samples += 1

            for word in words:
                self.word_counts[category][word] += 1
                self.vocabulary.add(word)

    def predict(self, text):

        words = self.tokenize(text)

        if not words:
            return "Other"

        best_category = None
        best_score = float("-inf")

        for category in self.category_counts:

            category_total = self.category_counts[category]

            # Calculate category probability
            score = math.log(
                category_total / self.total_samples
            )

            total_words = sum(
                self.word_counts[category].values()
            )

            vocabulary_size = len(self.vocabulary)

            # Calculate word probabilities with smoothing
            for word in words:

                word_count = self.word_counts[category][word]

                probability = (
                    word_count + 1
                ) / (
                    total_words + vocabulary_size + 1
                )

                score += math.log(probability)

            if score > best_score:
                best_score = score
                best_category = category

        return best_category or "Other"


# Create AI classifier
classifier = TransactionClassifier()


def categorize_transaction(description):
    """Predict the category of a financial transaction."""
    return classifier.predict(description)


if __name__ == "__main__":

    print("SMARTSPEND AI - TRANSACTION CLASSIFIER")
    print("--------------------------------------")

    test_transactions = [
        "Swiggy food delivery",
        "Uber cab payment",
        "Amazon shopping",
        "College tuition fees",
        "Electricity bill",
        "Netflix subscription",
        "Hospital medicine",
        "Monthly salary"
    ]

    for transaction in test_transactions:

        category = categorize_transaction(transaction)

        print(f"{transaction} --> {category}")

    print("--------------------------------------")
    print("AI MODEL TEST COMPLETED SUCCESSFULLY!")
