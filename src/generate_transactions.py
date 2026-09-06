import pandas as pd 
import random 


transactions = []
accounts = pd.read_csv('data/accounts.csv')

for i in range(100): 
    random_account = accounts.sample(n=1).iloc[0]
    account_id = random_account['account_id']
    if random.random() < 0.05:
        account_id = 999
    transaction_type = random.choice(['purchase', 'transfer', 'withdrawal'])
    amount = round(random.uniform(100, 10000), 2)
    if random.random() < 0.05:
        amount = -amount
    opened_at = pd.to_datetime(random_account['opened_at'])
    days_after_open = random.randint(0, 120)
    transaction_ts = opened_at + pd.Timedelta(days=days_after_open, hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))

    transaction = {
          'transaction_id': i + 1,
          'account_id': account_id,
          'currency': random_account['currency'],
          'transaction_type': transaction_type,
          'amount': amount,
          'transaction_ts': transaction_ts
}
    transactions.append(transaction)
df = pd.DataFrame(transactions)
df.to_csv('data/transactions.csv', index=False)
print(df.head(3))
