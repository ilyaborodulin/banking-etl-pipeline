import psycopg2
from io import StringIO

conn = psycopg2.connect(
    host="postgres",
    port=5432,
    dbname="banking",
    user="banking_user",
    password="banking_password"
)

cur = conn.cursor()


def copy_csv_to_table(file_path, table_name, columns):
    with open(file_path, "r", encoding="utf-8") as file:
        clean_data = "".join(line for line in file if line.strip())

    cur.copy_expert(
        f"""
        COPY {table_name} ({columns})
        FROM STDIN
        WITH (FORMAT CSV, HEADER TRUE)
        """,
        StringIO(clean_data)
    )


try:
    cur.execute("""
        TRUNCATE TABLE
            raw_customers,
            raw_accounts,
            raw_transactions,
            stg_transactions,
            rejected_transactions;
    """)

    copy_csv_to_table(
        "data/customers.csv",
        "raw_customers",
        "customer_id, full_name, city, created_at"
    )

    copy_csv_to_table(
        "data/accounts.csv",
        "raw_accounts",
        "account_id, customer_id, account_type, currency, opened_at, status"
    )

    copy_csv_to_table(
        "data/transactions.csv",
        "raw_transactions",
        "transaction_id, account_id, currency, transaction_type, amount, transaction_ts"
    )

    copy_csv_to_table(
        "data/valid_transactions.csv",
        "stg_transactions",
        "transaction_id, account_id, currency, transaction_type, amount, transaction_ts"
    )

    copy_csv_to_table(
        "data/rejected_transactions.csv",
        "rejected_transactions",
        "transaction_id, account_id, currency, transaction_type, amount, transaction_ts, reject_reasons"
    )

    cur.execute("SELECT COUNT(*) FROM raw_transactions")
    raw_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM stg_transactions")
    valid_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM rejected_transactions")
    rejected_count = cur.fetchone()[0]

    if raw_count != valid_count + rejected_count:
        raise ValueError(
            f"raw={raw_count}, valid={valid_count}, rejected={rejected_count}"
        )

    conn.commit()

    print("Data loaded successfully")
    print(f"Raw transactions: {raw_count}")
    print(f"Valid transactions: {valid_count}")
    print(f"Rejected transactions: {rejected_count}")

except Exception:
    conn.rollback()
    raise

finally:
    cur.close()
    conn.close()