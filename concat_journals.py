from glob import glob

import pandas as pd


def concat_journals(filenames, outfile):
    files = glob(filenames)
    pd.concat(
        (
            pd.read_csv(
                file,
                usecols=[
                    "Date",
                    "Account",
                    "Debit",
                    "Credit",
                    "Description",
                    "UID",
                ],
            )
            for file in files
        ),
        ignore_index=True,
    ).sort_values(
        ["Date", "UID", "Debit", "Credit"], ascending=[True, True, False, False]
    ).to_csv(outfile, index=False)
