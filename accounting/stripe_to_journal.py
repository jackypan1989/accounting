from operator import contains

import pandas as pd


# Define the conversion function
def convert_stripe_to_journal(path_to_stripe_csv, path_to_journal_csv):
    # Load the Stripe csv
    stripe_df = pd.read_csv(path_to_stripe_csv)

    # Prepare the Journal DataFrame
    journal_columns = ["Date", "Account", "Debit", "Credit", "Description", "UID"]
    journal_list = []

    # Process each Stripe record and convert it to journal entries
    for index, row in stripe_df.iterrows():
        # Convert Stripe date format to your journal's date format if necessary
        date = row["Created (UTC)"]
        description = row["Description"]
        amount = round(float(row["Amount"]), 2)
        fee = round(float(row["Fee"]), 2)
        net = round(float(row["Net"]), 2)
        transaction_type = row["Type"]
        transaction_id = "stripe_" + row["id"]

        # Handle each transaction type
        if transaction_type in ["charge", "payment"]:
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Stripe Balance",
                    "Debit": net,
                    "Credit": "",
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                },
            )
            if fee > 0:
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Stripe Transaction Fee",
                        "Debit": fee,
                        "Credit": "",
                        "Description": description,
                        "UID": "stripe_" + transaction_id,
                    }
                )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Subscription Revenue",
                    "Debit": "",
                    "Credit": amount,
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )
        elif transaction_type in ["refund", "payment_refund"]:
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Subscription Revenue",
                    "Debit": -amount,
                    "Credit": "",
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Stripe Balance",
                    "Debit": "",
                    "Credit": -amount,
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )
        elif transaction_type == "stripe_fee":
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Stripe Software Fee",
                    "Debit": -amount,
                    "Credit": "",
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Stripe Balance",
                    "Debit": "",
                    "Credit": -amount,
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )
        elif transaction_type == "payout":
            if amount < 0:
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Wise Balance",
                        "Debit": -amount,
                        "Credit": "",
                        "Description": description,
                        "UID": "stripe_" + transaction_id,
                    }
                )
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Stripe Balance",
                        "Debit": "",
                        "Credit": -amount,
                        "Description": description,
                        "UID": "stripe_" + transaction_id,
                    }
                )
            else:
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Stripe Balance",
                        "Debit": amount,
                        "Credit": "",
                        "Description": description,
                        "UID": "stripe_" + transaction_id,
                    }
                )
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Wise Balance",
                        "Debit": "",
                        "Credit": amount,
                        "Description": description,
                        "UID": "stripe_" + transaction_id,
                    }
                )
        elif contains(description, "Chargeback withdrawal"):
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Subscription Revenue",
                    "Debit": -amount,
                    "Credit": "",
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Stripe Transaction Fee",
                    "Debit": fee,
                    "Credit": "",
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Stripe Balance",
                    "Debit": "",
                    "Credit": -amount,
                    "Description": description,
                    "UID": "stripe_" + transaction_id,
                }
            )

        else:
            print(row)

    # Output file
    jorunal_df = pd.DataFrame(journal_list)

    pd.concat(
        [pd.DataFrame(columns=journal_columns), jorunal_df],
        ignore_index=True,
    ).sort_values(
        ["Date", "UID", "Debit", "Credit"], ascending=[True, True, False, False]
    ).to_csv(path_to_journal_csv, index=False)
