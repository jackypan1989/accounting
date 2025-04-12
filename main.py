import os

from accounting.concat_journals import concat_journals
from accounting.journal_to_report import journal_to_report
from accounting.stripe_to_journal import convert_stripe_to_journal
from accounting.wise_to_journal import convert_wise_to_journal

prefix = "us_2024"
source_path = f"input/{prefix}"
output_path = f"output/{prefix}"

if not os.path.exists(source_path):
    os.mkdir(source_path)

if not os.path.exists(output_path):
    os.mkdir(output_path)

# shutil.copyfile(
#     f"{source_path}/journal_manual.csv", f"{output_path}/journal_manual.csv"
# )

convert_stripe_to_journal(
    f"{source_path}/stripe_own.csv", f"{output_path}/journal_stripe_own.csv"
)
convert_stripe_to_journal(
    f"{source_path}/stripe_preteeth.csv", f"{output_path}/journal_stripe_preteeth.csv"
)
convert_wise_to_journal(
    f"{source_path}/wise_usd.csv", f"{output_path}/journal_wise_usd.csv", 1
)

concat_journals(f"{output_path}/journal_*.csv", f"{output_path}/journal.csv")

journal_to_report(
    f"{output_path}/journal.csv",
    f"{output_path}/balance_sheet.csv",
    f"{output_path}/income_statement.csv",
)
