from datetime import datetime
from operator import contains

import pandas as pd


# Define the conversion function
def convert_wise_to_journal(path_to_wise_csv, path_to_journal_csv, currency_rate):
    # Load the Stripe csv
    wise_df = pd.read_csv(path_to_wise_csv)

    # Prepare the Journal DataFrame
    journal_columns = ["Date", "Account", "Debit", "Credit", "Description", "UID"]
    journal_list = []

    # Process each Stripe record and convert it to journal entries
    for index, row in wise_df.iterrows():
        # Convert Stripe date format to your journal's date format if necessary
        date = datetime.strptime(row["Date"], "%d-%m-%Y").strftime("%Y-%m-%d")
        description = row["Description"]
        amount = round(float(row["Amount"]) * currency_rate, 2)
        uid = "wise_" + row["TransferWise ID"]

        # Handle each transaction type
        if contains(description, "Converted") or contains(description, "STRIPE"):
            continue
        # Wise First
        elif contains(uid, "BANK_DETAILS_ORDER_CHECKOUT"):
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Wise Transaction Fee",
                    "Debit": -amount,
                    "Credit": "",
                    "Description": description,
                    "UID": uid,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Wise Balance",
                    "Debit": "",
                    "Credit": -amount,
                    "Description": description,
                    "UID": uid,
                }
            )
        elif contains(description, "Topped up balance"):
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Wise Balance",
                    "Debit": amount,
                    "Credit": "",
                    "Description": description,
                    "UID": uid,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Owner's Capital",
                    "Debit": "",
                    "Credit": amount,
                    "Description": description,
                    "UID": uid,
                }
            )
        elif (
            contains(description, "Vercel")
            or contains(description, "Lemsqzy")
            or contains(description, "Microsoft")
        ):
            if amount < 0:
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Cost of Goods Sold",
                        "Debit": -amount,
                        "Credit": "",
                        "Description": description,
                        "UID": uid,
                    }
                )
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Wise Balance",
                        "Debit": "",
                        "Credit": -amount,
                        "Description": description,
                        "UID": uid,
                    }
                )
            else:
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Wise Balance",
                        "Debit": amount,
                        "Credit": "",
                        "Description": description,
                        "UID": uid,
                    }
                )
                journal_list.append(
                    {
                        "Date": date,
                        "Account": "Cost of Goods Sold",
                        "Debit": "",
                        "Credit": amount,
                        "Description": description,
                        "UID": uid,
                    }
                )
        elif contains(description, "Wise Charges"):
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Wise Transaction Fee",
                    "Debit": -amount,
                    "Credit": "",
                    "Description": description,
                    "UID": uid,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Wise Balance",
                    "Debit": "",
                    "Credit": -amount,
                    "Description": description,
                    "UID": uid,
                }
            )
        elif contains(description, "Sent money to"):
            journal_list.append(
                {
                    "Date": date,
                    "Account": "General and Administrative Expenses",
                    "Debit": -amount,
                    "Credit": "",
                    "Description": description,
                    "UID": uid,
                }
            )
            journal_list.append(
                {
                    "Date": date,
                    "Account": "Wise Balance",
                    "Debit": "",
                    "Credit": -amount,
                    "Description": description,
                    "UID": uid,
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
