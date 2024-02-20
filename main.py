import os
import shutil

import concat_journals
import journal_to_report
import stripe_to_journal
import wise_to_journal

source_path = "input"
output_path = "output"

if not os.path.exists(source_path):
    os.mkdir(source_path)

if not os.path.exists(output_path):
    os.mkdir(output_path)

shutil.copyfile(
    f"{source_path}/journal_manual.csv", f"{output_path}/journal_manual.csv"
)

stripe_to_journal.convert_stripe_to_journal(
    f"{source_path}/stripe_own.csv", f"{output_path}/journal_stripe_own.csv"
)
stripe_to_journal.convert_stripe_to_journal(
    f"{source_path}/stripe_preteeth.csv", f"{output_path}/journal_stripe_preteeth.csv"
)

wise_to_journal.convert_wise_to_journal(
    f"{source_path}/wise_cad.csv", f"{output_path}/journal_wise_cad.csv", 0.75
)
wise_to_journal.convert_wise_to_journal(
    f"{source_path}/wise_usd.csv", f"{output_path}/journal_wise_usd.csv", 1
)

concat_journals.concat_journals(
    f"{output_path}/journal_*.csv", f"{output_path}/journal.csv"
)

journal_to_report.journal_to_report(
    f"{output_path}/journal.csv",
    f"{output_path}/balance_sheet.csv",
    f"{output_path}/income_statement.csv",
)
