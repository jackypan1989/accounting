import pandas as pd

# Accounts in categories
account_balances = {
    "Assets": {
        "Wise Balance": 0.0,
        "Stripe Balance": 0.0,
    },
    "Liabilities": {"Accounts Payable": 0.0},
    "Equity": {"Owner's Capital": 0.0, "Retained Earnings": 0.0},
    "Revenues": {"Subscription Revenue": 0.0},
    "Expenses": {
        "Cost of Goods Sold": 0.0,
        "Wise Transaction Fee": 0.0,
        "Stripe Transaction Fee": 0.0,
        "Stripe Software Fee": 0.0,
        "General and Administrative Expenses": 0.0,
        "Research and Development Expenses": 0.0,
    },
}


def journal_to_report(
    input_path, output_balance_sheet_path, output_income_statement_path
):
    # Load the journal CSV
    journal_df = pd.read_csv(input_path)

    # Process each journal entry
    for index, row in journal_df.iterrows():
        account = row["Account"]
        debit = row["Debit"] if pd.notna(row["Debit"]) else 0
        credit = row["Credit"] if pd.notna(row["Credit"]) else 0

        # Debit increases or credit decreases in Assets / Expenses
        if account in account_balances["Assets"].keys():
            account_balances["Assets"][account] += debit - credit
        elif account in account_balances["Expenses"].keys():
            account_balances["Expenses"][account] += debit - credit

        # Credit increases or debit decreases in Liabilities / Equity / Revenues
        elif account in account_balances["Liabilities"].keys():
            account_balances["Liabilities"][account] += credit - debit
        elif account in account_balances["Equity"].keys():
            account_balances["Equity"][account] += credit - debit
        elif account in account_balances["Revenues"].keys():
            account_balances["Revenues"][account] += credit - debit

    # Adjust retained earnings for Revenues and Expenses
    total_revenues = sum(account_balances["Revenues"].values())
    total_expenses = sum(account_balances["Expenses"].values())
    account_balances["Equity"]["Retained Earnings"] += total_revenues - total_expenses

    # Generate and output the balance sheet
    balance_sheet_data = [
        ("Assets", ""),
        *[(account, amount) for account, amount in account_balances["Assets"].items()],
        ("Total Assets", sum(account_balances["Assets"].values())),
        ("Liabilities", ""),
        *[
            (account, amount)
            for account, amount in account_balances["Liabilities"].items()
        ],
        ("Total Liabilities", sum(account_balances["Liabilities"].values())),
        ("Equity", ""),
        *[(account, amount) for account, amount in account_balances["Equity"].items()],
        ("Total Equity", sum(account_balances["Equity"].values())),
    ]
    balance_sheet_df = pd.DataFrame(balance_sheet_data, columns=["Account", "Amount"])
    balance_sheet_df.to_csv(output_balance_sheet_path, index=False, float_format="%.2f")

    # Generate and output the income statement
    income_statement_data = [
        ("Revenues", ""),
        *[
            (account, amount)
            for account, amount in account_balances["Revenues"].items()
        ],
        ("Total Revenues", total_revenues),
        ("Expenses", ""),
        *[
            (account, amount)
            for account, amount in account_balances["Expenses"].items()
        ],
        ("Total Expenses", total_expenses),
        ("Net Income", total_revenues - total_expenses),
    ]

    income_statement_df = pd.DataFrame(
        income_statement_data, columns=["Account", "Amount"]
    )
    income_statement_df.to_csv(
        output_income_statement_path, index=False, float_format="%.2f"
    )
