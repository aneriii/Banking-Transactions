from __future__ import annotations

import unittest

from payment_reconciliation import (
    BankSettlement,
    PlatformTransaction,
    d,
    find_amount_mismatches,
    find_duplicate_records,
    find_missing_in_bank,
    find_missing_in_platform,
    find_pending_settlements,
    find_refunds_without_original,
    generate_bank_settlements,
    generate_platform_transactions,
    parse_date,
)


def report_transaction_ids(rows: list[dict[str, str]]) -> set[str]:
    return {row["transaction_id"] for row in rows if "transaction_id" in row}


class ReconciliationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.platform_transactions = generate_platform_transactions()
        self.bank_settlements = generate_bank_settlements()

    def test_clean_matching_records_have_no_exceptions(self) -> None:
        platform_transactions = [
            PlatformTransaction("PT-MATCH-001", "TXN-MATCH-001", "USER-001", parse_date("2026-03-10"), d("42.25"), "USD", "PAYMENT"),
            PlatformTransaction("PT-MATCH-002", "TXN-MATCH-002", "USER-002", parse_date("2026-03-10"), d("-5.00"), "USD", "REFUND", "TXN-MATCH-001"),
        ]
        bank_settlements = [
            BankSettlement("BR-MATCH-001", "BATCH-MATCH", "TXN-MATCH-001", parse_date("2026-03-11"), d("42.25"), "USD", "PAYMENT"),
            BankSettlement("BR-MATCH-002", "BATCH-MATCH", "TXN-MATCH-002", parse_date("2026-03-11"), d("-5.00"), "USD", "REFUND", "TXN-MATCH-001"),
        ]

        self.assertEqual([], find_missing_in_bank(platform_transactions, bank_settlements))
        self.assertEqual([], find_missing_in_platform(platform_transactions, bank_settlements))
        self.assertEqual([], find_amount_mismatches(platform_transactions, bank_settlements))
        self.assertEqual([], find_duplicate_records(platform_transactions, bank_settlements))
        self.assertEqual([], find_pending_settlements(platform_transactions, bank_settlements))
        self.assertEqual([], find_refunds_without_original(platform_transactions, bank_settlements))

    def test_missing_in_bank_records_are_reported(self) -> None:
        rows = find_missing_in_bank(self.platform_transactions, self.bank_settlements)

        self.assertEqual({"TXN-1016", "TXN-1023"}, report_transaction_ids(rows))

    def test_missing_in_platform_records_are_reported(self) -> None:
        rows = find_missing_in_platform(self.platform_transactions, self.bank_settlements)

        self.assertEqual({"TXN-9998", "RFND-9001"}, report_transaction_ids(rows))

    def test_transaction_amount_mismatch_is_reported(self) -> None:
        rows = find_amount_mismatches(self.platform_transactions, self.bank_settlements)
        transaction_rows = [row for row in rows if row["reference"] == "TXN-1013"]

        self.assertEqual(
            [
                {
                    "scope": "transaction",
                    "reference": "TXN-1013",
                    "platform_amount": "75.23",
                    "bank_amount": "75.32",
                    "difference": "0.09",
                    "reason": "Single transaction amount differs by more than one cent",
                }
            ],
            transaction_rows,
        )

    def test_partial_settlement_is_reported_as_amount_mismatch(self) -> None:
        rows = find_amount_mismatches(self.platform_transactions, self.bank_settlements)
        partial_rows = [row for row in rows if row["reference"] == "TXN-1024"]

        self.assertEqual(
            [
                {
                    "scope": "transaction",
                    "reference": "TXN-1024",
                    "platform_amount": "15.15",
                    "bank_amount": "10.15",
                    "difference": "-5.00",
                    "reason": "Partial bank settlement: bank settled less than the platform transaction amount",
                }
            ],
            partial_rows,
        )

    def test_batch_rounding_mismatch_is_reported(self) -> None:
        rows = find_amount_mismatches(self.platform_transactions, self.bank_settlements)
        batch_rows = [row for row in rows if row["scope"] == "batch"]

        self.assertEqual(
            [
                {
                    "scope": "batch",
                    "reference": "BATCH-ROUNDING",
                    "platform_amount": "60.02",
                    "bank_amount": "60.00",
                    "difference": "-0.02",
                    "reason": "Rounding difference appears only after summing the batch",
                }
            ],
            batch_rows,
        )

    def test_duplicate_records_are_reported_for_both_datasets(self) -> None:
        rows = find_duplicate_records(self.platform_transactions, self.bank_settlements)

        self.assertEqual(
            [
                {"dataset": "platform_transactions", "transaction_id": "TXN-1014", "duplicate_count": "2"},
                {"dataset": "bank_settlements", "transaction_id": "TXN-1018", "duplicate_count": "2"},
            ],
            rows,
        )

    def test_pending_settlement_is_reported(self) -> None:
        rows = find_pending_settlements(self.platform_transactions, self.bank_settlements)

        self.assertEqual(
            [
                {
                    "transaction_id": "TXN-1015",
                    "platform_paid_at": "2026-03-31",
                    "bank_settled_at": "2026-04-02",
                    "amount": "145.00",
                    "reason": "Paid in reconciliation month but settled in following month",
                }
            ],
            rows,
        )

    def test_refund_without_original_transaction_is_reported(self) -> None:
        rows = find_refunds_without_original(self.platform_transactions, self.bank_settlements)

        self.assertEqual(
            [
                {
                    "bank_record_id": "BR-025",
                    "refund_transaction_id": "RFND-9001",
                    "original_transaction_id": "TXN-NOT-FOUND",
                    "amount": "-19.99",
                    "settled_at": "2026-03-31",
                    "reason": "Refund settlement references an original transaction that does not exist in the platform table",
                }
            ],
            rows,
        )


if __name__ == "__main__":
    unittest.main()
