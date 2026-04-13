from __future__ import annotations

import csv
from io import StringIO
from decimal import Decimal

import streamlit as st

from payment_reconciliation import (
    RECONCILIATION_MONTH,
    bank_to_row,
    find_amount_mismatches,
    find_duplicate_records,
    find_missing_in_bank,
    find_missing_in_platform,
    find_pending_settlements,
    find_refunds_without_original,
    generate_bank_settlements,
    generate_platform_transactions,
    platform_to_row,
)


def csv_download(rows: list[dict[str, str]]) -> str:
    if not rows:
        return ""

    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def total_amount(rows: list[dict[str, str]]) -> Decimal:
    return sum(Decimal(row["amount"]) for row in rows)


def render_table(title: str, rows: list[dict[str, str]], file_name: str, note: str) -> None:
    st.subheader(title)
    st.caption(note)

    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
        st.download_button(
            label=f"Download {title}",
            data=csv_download(rows),
            file_name=file_name,
            mime="text/csv",
        )
    else:
        st.success("No records found.")


def main() -> None:
    st.set_page_config(page_title="Payment Reconciliation", layout="wide")

    platform_transactions = generate_platform_transactions()
    bank_settlements = generate_bank_settlements()
    platform_rows = [platform_to_row(transaction) for transaction in platform_transactions]
    bank_rows = [bank_to_row(settlement) for settlement in bank_settlements]

    reports = {
        "Missing in bank": {
            "rows": find_missing_in_bank(platform_transactions, bank_settlements),
            "file_name": "missing_in_bank.csv",
            "note": "Platform transactions that do not have a matching bank settlement.",
        },
        "Missing in platform": {
            "rows": find_missing_in_platform(platform_transactions, bank_settlements),
            "file_name": "missing_in_platform.csv",
            "note": "Bank settlements that do not have a matching platform transaction.",
        },
        "Amount mismatch": {
            "rows": find_amount_mismatches(platform_transactions, bank_settlements),
            "file_name": "amount_mismatches.csv",
            "note": "Transactions, partial settlements, or settlement batches where the amounts differ.",
        },
        "Duplicate record": {
            "rows": find_duplicate_records(platform_transactions, bank_settlements),
            "file_name": "duplicate_records.csv",
            "note": "Transaction IDs appearing more than once in either dataset.",
        },
        "Pending settlement": {
            "rows": find_pending_settlements(platform_transactions, bank_settlements),
            "file_name": "pending_settlements.csv",
            "note": "Transactions paid in the reconciliation month but settled after month end.",
        },
        "Refund with no matching original": {
            "rows": find_refunds_without_original(platform_transactions, bank_settlements),
            "file_name": "refunds_without_original.csv",
            "note": "Refund settlements that point to an original transaction missing from the platform table.",
        },
    }

    total_exceptions = sum(len(report["rows"]) for report in reports.values())

    st.title("Payment Reconciliation")
    st.write(f"Reconciliation month: **{RECONCILIATION_MONTH}**")

    summary_columns = st.columns(5)
    summary_columns[0].metric("Platform records", len(platform_rows))
    summary_columns[1].metric("Bank records", len(bank_rows))
    summary_columns[2].metric("Total exceptions", total_exceptions)
    summary_columns[3].metric("Platform total", f"${total_amount(platform_rows):,.2f}")
    summary_columns[4].metric("Bank total", f"${total_amount(bank_rows):,.2f}")

    exception_tab, source_tab = st.tabs(["Exceptions", "Source data"])

    with exception_tab:
        for title, report in reports.items():
            render_table(
                title=title,
                rows=report["rows"],
                file_name=report["file_name"],
                note=report["note"],
            )
            st.divider()

    with source_tab:
        render_table(
            title="Platform transactions",
            rows=platform_rows,
            file_name="platform_transactions.csv",
            note="Payments and refunds recorded instantly by the platform.",
        )
        st.divider()
        render_table(
            title="Bank settlements",
            rows=bank_rows,
            file_name="bank_settlements.csv",
            note="Funds settled by the bank in batches after a delay.",
        )


if __name__ == "__main__":
    main()
