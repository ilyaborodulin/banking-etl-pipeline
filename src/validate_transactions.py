import pandas as pd



transactions = pd.read_csv('data/transactions.csv')
accounts = pd.read_csv('data/accounts.csv')

valid_account_ids = set(accounts['account_id'])


def validate_row(row):
    errors = []

    if row['amount'] <= 0:
        errors.append('INVALID_AMOUNT')

    if row['account_id'] not in valid_account_ids:
        errors.append('ACCOUNT_NOT_FOUND')

    return errors

transactions['reject_reasons'] = transactions.apply(validate_row,axis=1)
valid_transactions = transactions[transactions['reject_reasons'].apply(len) == 0].copy()
rejected_transactions = transactions[transactions['reject_reasons'].apply(len) > 0].copy()

assert (len(valid_transactions) + len(rejected_transactions)== len(transactions))

valid_transactions.drop(columns=['reject_reasons']).to_csv(
    'data/valid_transactions.csv',
    index=False
)
rejected_transactions.to_csv('data/rejected_transactions.csv',index=False)

print(f'Input rows: {len(transactions)}')
print(f'Valid rows: {len(valid_transactions)}')
print(f'Rejected rows: {len(rejected_transactions)}')
print()
print(rejected_transactions[['transaction_id', 'account_id', 'amount', 'reject_reasons']])

