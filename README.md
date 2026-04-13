# Payment Reconciliation Test Data

This project creates two reconciliation tables:

- `data/platform_transactions.csv`: platform transactions recorded instantly when the customer paid.
- `data/bank_settlements.csv`: bank settlement records recorded later in daily batches.

The generated data includes these month-end reconciliation scenarios:

- A March platform transaction that settles in April.
- A rounding issue that only appears after summing a bank batch.
- Duplicate entries in both the platform and bank datasets.
- A refund that has no matching original platform transaction.
- Bank records missing from the platform table.
- Platform records missing from the bank table.
- A partial bank settlement where only part of the platform amount settled.

Run it with:

```bash
python payment_reconciliation.py
```

The script prints readable exception tables and writes CSV outputs to `output/`:

- `missing_in_bank.csv`
- `missing_in_platform.csv`
- `amount_mismatches.csv`
- `duplicate_records.csv`
- `pending_settlements.csv`
- `refunds_without_original.csv`

## Streamlit Dashboard

Run the one-page frontend with:

```bash
streamlit run app.py
```

If Streamlit is not installed yet:

```bash
pip install -r requirements.txt
```

## Tests

Run the reconciliation test suite with:

```bash
python -m unittest discover
```
