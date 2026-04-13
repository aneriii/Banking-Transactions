from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Iterable


DATA_DIR = Path("data")
OUTPUT_DIR = Path("output")
RECONCILIATION_MONTH = "2026-03"
PENNY = Decimal("0.01")


@dataclass(frozen=True)
class PlatformTransaction:
    platform_row_id: str
    transaction_id: str
    user_id: str
    paid_at: date
    amount: Decimal
    currency: str
    transaction_type: str
    original_transaction_id: str = ""


@dataclass(frozen=True)
class BankSettlement:
    bank_record_id: str
    batch_id: str
    transaction_id: str
    settled_at: date
    amount: Decimal
    currency: str
    settlement_type: str
    original_transaction_id: str = ""


def d(value: str) -> Decimal:
    return Decimal(value)


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def money(value: Decimal) -> str:
    return f"{value.quantize(PENNY, rounding=ROUND_HALF_UP)}"


def is_in_reconciliation_month(value: date) -> bool:
    return value.strftime("%Y-%m") == RECONCILIATION_MONTH


def generate_platform_transactions() -> list[PlatformTransaction]:
    return [
        PlatformTransaction("PT-001", "TXN-1001", "USER-001", parse_date("2026-03-01"), d("120.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-002", "TXN-1002", "USER-002", parse_date("2026-03-02"), d("45.50"), "USD", "PAYMENT"),
        PlatformTransaction("PT-003", "TXN-1003", "USER-003", parse_date("2026-03-03"), d("88.10"), "USD", "PAYMENT"),
        PlatformTransaction("PT-004", "TXN-1004", "USER-004", parse_date("2026-03-04"), d("250.75"), "USD", "PAYMENT"),
        PlatformTransaction("PT-005", "TXN-1005", "USER-005", parse_date("2026-03-06"), d("18.20"), "USD", "PAYMENT"),
        PlatformTransaction("PT-006", "TXN-1006", "USER-006", parse_date("2026-03-07"), d("300.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-007", "TXN-1007", "USER-007", parse_date("2026-03-09"), d("64.35"), "USD", "PAYMENT"),
        PlatformTransaction("PT-008", "TXN-1008", "USER-008", parse_date("2026-03-10"), d("99.99"), "USD", "PAYMENT"),
        PlatformTransaction("PT-009", "TXN-1009", "USER-009", parse_date("2026-03-11"), d("500.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-010", "TXN-1010", "USER-010", parse_date("2026-03-12"), d("10.005"), "USD", "PAYMENT"),
        PlatformTransaction("PT-011", "TXN-1011", "USER-011", parse_date("2026-03-12"), d("20.005"), "USD", "PAYMENT"),
        PlatformTransaction("PT-012", "TXN-1012", "USER-012", parse_date("2026-03-12"), d("30.005"), "USD", "PAYMENT"),
        PlatformTransaction("PT-013", "TXN-1013", "USER-013", parse_date("2026-03-13"), d("75.23"), "USD", "PAYMENT"),
        PlatformTransaction("PT-014", "TXN-1014", "USER-014", parse_date("2026-03-14"), d("41.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-015", "TXN-1014", "USER-014", parse_date("2026-03-14"), d("41.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-016", "TXN-1015", "USER-015", parse_date("2026-03-31"), d("145.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-017", "TXN-1016", "USER-016", parse_date("2026-03-20"), d("210.40"), "USD", "PAYMENT"),
        PlatformTransaction("PT-018", "TXN-1017", "USER-017", parse_date("2026-03-21"), d("-12.00"), "USD", "REFUND", "TXN-1005"),
        PlatformTransaction("PT-019", "TXN-1018", "USER-018", parse_date("2026-03-22"), d("60.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-020", "TXN-1019", "USER-019", parse_date("2026-03-24"), d("33.33"), "USD", "PAYMENT"),
        PlatformTransaction("PT-021", "TXN-1020", "USER-020", parse_date("2026-03-25"), d("125.25"), "USD", "PAYMENT"),
        PlatformTransaction("PT-022", "TXN-1021", "USER-021", parse_date("2026-03-26"), d("89.90"), "USD", "PAYMENT"),
        PlatformTransaction("PT-023", "TXN-1022", "USER-022", parse_date("2026-03-27"), d("10.00"), "USD", "PAYMENT"),
        PlatformTransaction("PT-024", "TXN-1023", "USER-023", parse_date("2026-03-28"), d("72.72"), "USD", "PAYMENT"),
        PlatformTransaction("PT-025", "TXN-1024", "USER-024", parse_date("2026-03-29"), d("15.15"), "USD", "PAYMENT"),
    ]


def generate_bank_settlements() -> list[BankSettlement]:
    return [
        BankSettlement("BR-001", "BATCH-2026-03-02-A", "TXN-1001", parse_date("2026-03-02"), d("120.00"), "USD", "PAYMENT"),
        BankSettlement("BR-002", "BATCH-2026-03-04-A", "TXN-1002", parse_date("2026-03-04"), d("45.50"), "USD", "PAYMENT"),
        BankSettlement("BR-003", "BATCH-2026-03-05-A", "TXN-1003", parse_date("2026-03-05"), d("88.10"), "USD", "PAYMENT"),
        BankSettlement("BR-004", "BATCH-2026-03-05-A", "TXN-1004", parse_date("2026-03-05"), d("250.75"), "USD", "PAYMENT"),
        BankSettlement("BR-005", "BATCH-2026-03-08-A", "TXN-1005", parse_date("2026-03-08"), d("18.20"), "USD", "PAYMENT"),
        BankSettlement("BR-006", "BATCH-2026-03-09-A", "TXN-1006", parse_date("2026-03-09"), d("300.00"), "USD", "PAYMENT"),
        BankSettlement("BR-007", "BATCH-2026-03-10-A", "TXN-1007", parse_date("2026-03-10"), d("64.35"), "USD", "PAYMENT"),
        BankSettlement("BR-008", "BATCH-2026-03-12-A", "TXN-1008", parse_date("2026-03-12"), d("99.99"), "USD", "PAYMENT"),
        BankSettlement("BR-009", "BATCH-2026-03-13-A", "TXN-1009", parse_date("2026-03-13"), d("500.00"), "USD", "PAYMENT"),
        BankSettlement("BR-010", "BATCH-ROUNDING", "TXN-1010", parse_date("2026-03-14"), d("10.00"), "USD", "PAYMENT"),
        BankSettlement("BR-011", "BATCH-ROUNDING", "TXN-1011", parse_date("2026-03-14"), d("20.00"), "USD", "PAYMENT"),
        BankSettlement("BR-012", "BATCH-ROUNDING", "TXN-1012", parse_date("2026-03-14"), d("30.00"), "USD", "PAYMENT"),
        BankSettlement("BR-013", "BATCH-2026-03-15-A", "TXN-1013", parse_date("2026-03-15"), d("75.32"), "USD", "PAYMENT"),
        BankSettlement("BR-014", "BATCH-2026-03-16-A", "TXN-1014", parse_date("2026-03-16"), d("41.00"), "USD", "PAYMENT"),
        BankSettlement("BR-015", "BATCH-2026-04-02-A", "TXN-1015", parse_date("2026-04-02"), d("145.00"), "USD", "PAYMENT"),
        BankSettlement("BR-016", "BATCH-2026-03-23-A", "TXN-1017", parse_date("2026-03-23"), d("-12.00"), "USD", "REFUND", "TXN-1005"),
        BankSettlement("BR-017", "BATCH-2026-03-24-A", "TXN-1018", parse_date("2026-03-24"), d("60.00"), "USD", "PAYMENT"),
        BankSettlement("BR-018", "BATCH-2026-03-24-A", "TXN-1018", parse_date("2026-03-24"), d("60.00"), "USD", "PAYMENT"),
        BankSettlement("BR-019", "BATCH-2026-03-26-A", "TXN-1019", parse_date("2026-03-26"), d("33.33"), "USD", "PAYMENT"),
        BankSettlement("BR-020", "BATCH-2026-03-27-A", "TXN-1020", parse_date("2026-03-27"), d("125.25"), "USD", "PAYMENT"),
        BankSettlement("BR-021", "BATCH-2026-03-28-A", "TXN-1021", parse_date("2026-03-28"), d("89.90"), "USD", "PAYMENT"),
        BankSettlement("BR-022", "BATCH-2026-03-30-A", "TXN-1022", parse_date("2026-03-30"), d("10.00"), "USD", "PAYMENT"),
        BankSettlement("BR-023", "BATCH-2026-03-31-A", "TXN-9998", parse_date("2026-03-31"), d("44.44"), "USD", "PAYMENT"),
        BankSettlement("BR-024", "BATCH-2026-03-31-PARTIAL", "TXN-1024", parse_date("2026-03-31"), d("10.15"), "USD", "PAYMENT"),
        BankSettlement("BR-025", "BATCH-2026-03-31-R", "RFND-9001", parse_date("2026-03-31"), d("-19.99"), "USD", "REFUND", "TXN-NOT-FOUND"),
    ]


def platform_to_row(transaction: PlatformTransaction) -> dict[str, str]:
    return {
        "platform_row_id": transaction.platform_row_id,
        "transaction_id": transaction.transaction_id,
        "user_id": transaction.user_id,
        "paid_at": transaction.paid_at.isoformat(),
        "amount": str(transaction.amount),
        "currency": transaction.currency,
        "transaction_type": transaction.transaction_type,
        "original_transaction_id": transaction.original_transaction_id,
    }


def bank_to_row(settlement: BankSettlement) -> dict[str, str]:
    return {
        "bank_record_id": settlement.bank_record_id,
        "batch_id": settlement.batch_id,
        "transaction_id": settlement.transaction_id,
        "settled_at": settlement.settled_at.isoformat(),
        "amount": str(settlement.amount),
        "currency": settlement.currency,
        "settlement_type": settlement.settlement_type,
        "original_transaction_id": settlement.original_transaction_id,
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def one_to_many_by_transaction_id(records: Iterable) -> dict[str, list]:
    grouped: dict[str, list] = defaultdict(list)
    for record in records:
        grouped[record.transaction_id].append(record)
    return grouped


def find_duplicate_records(platform_transactions: list[PlatformTransaction], bank_settlements: list[BankSettlement]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    platform_counts = Counter(transaction.transaction_id for transaction in platform_transactions)
    bank_counts = Counter(settlement.transaction_id for settlement in bank_settlements)

    for transaction_id, count in sorted(platform_counts.items()):
        if count > 1:
            rows.append({"dataset": "platform_transactions", "transaction_id": transaction_id, "duplicate_count": str(count)})

    for transaction_id, count in sorted(bank_counts.items()):
        if count > 1:
            rows.append({"dataset": "bank_settlements", "transaction_id": transaction_id, "duplicate_count": str(count)})

    return rows


def find_missing_in_bank(platform_transactions: list[PlatformTransaction], bank_settlements: list[BankSettlement]) -> list[dict[str, str]]:
    bank_transaction_ids = {settlement.transaction_id for settlement in bank_settlements}
    return [
        {
            "platform_row_id": transaction.platform_row_id,
            "transaction_id": transaction.transaction_id,
            "paid_at": transaction.paid_at.isoformat(),
            "amount": str(transaction.amount),
            "reason": "Platform transaction has no matching bank settlement",
        }
        for transaction in platform_transactions
        if transaction.transaction_id not in bank_transaction_ids
    ]


def find_missing_in_platform(platform_transactions: list[PlatformTransaction], bank_settlements: list[BankSettlement]) -> list[dict[str, str]]:
    platform_transaction_ids = {transaction.transaction_id for transaction in platform_transactions}
    return [
        {
            "bank_record_id": settlement.bank_record_id,
            "transaction_id": settlement.transaction_id,
            "settled_at": settlement.settled_at.isoformat(),
            "amount": str(settlement.amount),
            "settlement_type": settlement.settlement_type,
            "original_transaction_id": settlement.original_transaction_id,
            "reason": "Bank settlement has no matching platform transaction",
        }
        for settlement in bank_settlements
        if settlement.transaction_id not in platform_transaction_ids
    ]


def find_pending_settlements(platform_transactions: list[PlatformTransaction], bank_settlements: list[BankSettlement]) -> list[dict[str, str]]:
    bank_by_transaction_id = one_to_many_by_transaction_id(bank_settlements)
    rows: list[dict[str, str]] = []

    for transaction in platform_transactions:
        if not is_in_reconciliation_month(transaction.paid_at):
            continue

        matching_settlements = bank_by_transaction_id.get(transaction.transaction_id, [])
        next_month_settlements = [
            settlement
            for settlement in matching_settlements
            if settlement.settled_at > transaction.paid_at and not is_in_reconciliation_month(settlement.settled_at)
        ]

        for settlement in next_month_settlements:
            rows.append(
                {
                    "transaction_id": transaction.transaction_id,
                    "platform_paid_at": transaction.paid_at.isoformat(),
                    "bank_settled_at": settlement.settled_at.isoformat(),
                    "amount": str(transaction.amount),
                    "reason": "Paid in reconciliation month but settled in following month",
                }
            )

    return rows


def find_amount_mismatches(platform_transactions: list[PlatformTransaction], bank_settlements: list[BankSettlement]) -> list[dict[str, str]]:
    platform_by_transaction_id = one_to_many_by_transaction_id(platform_transactions)
    bank_by_transaction_id = one_to_many_by_transaction_id(bank_settlements)
    rows: list[dict[str, str]] = []

    for transaction_id in sorted(set(platform_by_transaction_id) & set(bank_by_transaction_id)):
        platform_rows = platform_by_transaction_id[transaction_id]
        bank_rows = bank_by_transaction_id[transaction_id]

        if len(platform_rows) != 1 or len(bank_rows) != 1:
            continue

        platform_amount = platform_rows[0].amount
        bank_amount = bank_rows[0].amount
        difference = bank_amount - platform_amount

        if abs(difference) > PENNY:
            reason = "Single transaction amount differs by more than one cent"
            if platform_amount > 0 and Decimal("0") < bank_amount < platform_amount:
                reason = "Partial bank settlement: bank settled less than the platform transaction amount"

            rows.append(
                {
                    "scope": "transaction",
                    "reference": transaction_id,
                    "platform_amount": str(platform_amount),
                    "bank_amount": str(bank_amount),
                    "difference": str(difference),
                    "reason": reason,
                }
            )

    platform_unique = {transaction.transaction_id: transaction for transaction in platform_transactions if Counter(t.transaction_id for t in platform_transactions)[transaction.transaction_id] == 1}
    bank_batch_totals: dict[str, Decimal] = defaultdict(Decimal)
    platform_batch_totals: dict[str, Decimal] = defaultdict(Decimal)

    for settlement in bank_settlements:
        if settlement.transaction_id in platform_unique:
            bank_batch_totals[settlement.batch_id] += settlement.amount
            platform_batch_totals[settlement.batch_id] += platform_unique[settlement.transaction_id].amount

    for batch_id in sorted(bank_batch_totals):
        raw_platform_total = platform_batch_totals[batch_id]
        rounded_platform_total = raw_platform_total.quantize(PENNY, rounding=ROUND_HALF_UP)
        bank_total = bank_batch_totals[batch_id].quantize(PENNY, rounding=ROUND_HALF_UP)
        difference = bank_total - rounded_platform_total

        if difference and abs(difference) <= PENNY * 2:
            rows.append(
                {
                    "scope": "batch",
                    "reference": batch_id,
                    "platform_amount": str(rounded_platform_total),
                    "bank_amount": str(bank_total),
                    "difference": str(difference),
                    "reason": "Rounding difference appears only after summing the batch",
                }
            )

    return rows


def find_refunds_without_original(platform_transactions: list[PlatformTransaction], bank_settlements: list[BankSettlement]) -> list[dict[str, str]]:
    known_transaction_ids = {transaction.transaction_id for transaction in platform_transactions}
    rows: list[dict[str, str]] = []

    for settlement in bank_settlements:
        if settlement.settlement_type != "REFUND":
            continue

        if settlement.original_transaction_id not in known_transaction_ids:
            rows.append(
                {
                    "bank_record_id": settlement.bank_record_id,
                    "refund_transaction_id": settlement.transaction_id,
                    "original_transaction_id": settlement.original_transaction_id,
                    "amount": str(settlement.amount),
                    "settled_at": settlement.settled_at.isoformat(),
                    "reason": "Refund settlement references an original transaction that does not exist in the platform table",
                }
            )

    return rows


def print_section(title: str, rows: list[dict[str, str]]) -> None:
    print(f"\n{title}")
    print("-" * len(title))

    if not rows:
        print("No records found.")
        return

    headers = list(rows[0])
    widths = {header: max(len(header), *(len(row[header]) for row in rows)) for header in headers}
    print(" | ".join(header.ljust(widths[header]) for header in headers))
    print("-+-".join("-" * widths[header] for header in headers))

    for row in rows:
        print(" | ".join(row[header].ljust(widths[header]) for header in headers))


def main() -> None:
    platform_transactions = generate_platform_transactions()
    bank_settlements = generate_bank_settlements()

    platform_rows = [platform_to_row(transaction) for transaction in platform_transactions]
    bank_rows = [bank_to_row(settlement) for settlement in bank_settlements]

    reports = {
        "missing_in_bank": find_missing_in_bank(platform_transactions, bank_settlements),
        "missing_in_platform": find_missing_in_platform(platform_transactions, bank_settlements),
        "amount_mismatches": find_amount_mismatches(platform_transactions, bank_settlements),
        "duplicate_records": find_duplicate_records(platform_transactions, bank_settlements),
        "pending_settlements": find_pending_settlements(platform_transactions, bank_settlements),
        "refunds_without_original": find_refunds_without_original(platform_transactions, bank_settlements),
    }

    write_csv(DATA_DIR / "platform_transactions.csv", platform_rows)
    write_csv(DATA_DIR / "bank_settlements.csv", bank_rows)

    for report_name, rows in reports.items():
        if rows:
            write_csv(OUTPUT_DIR / f"{report_name}.csv", rows)

    print(f"Reconciliation month: {RECONCILIATION_MONTH}")
    print(f"Platform transactions table: {DATA_DIR / 'platform_transactions.csv'} ({len(platform_rows)} records)")
    print(f"Bank settlements table: {DATA_DIR / 'bank_settlements.csv'} ({len(bank_rows)} records)")

    print_section("Missing in bank", reports["missing_in_bank"])
    print_section("Missing in platform", reports["missing_in_platform"])
    print_section("Amount mismatch", reports["amount_mismatches"])
    print_section("Duplicate record", reports["duplicate_records"])
    print_section("Pending settlement", reports["pending_settlements"])
    print_section("Refund with no matching original transaction", reports["refunds_without_original"])

    print(f"\nCSV reports written to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
