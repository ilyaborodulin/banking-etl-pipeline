# Banking ETL Pipeline

Небольшой ETL-пайплайн для обработки банковских транзакций.

Проект сделал, чтобы на практике разобраться с типичным путём данных: от получения сырых записей и проверки их качества до загрузки в PostgreSQL и оркестрации через Airflow.

## Что делает пайплайн

Пайплайн состоит из трёх основных этапов:

```text
generate_transactions
        ↓
validate_transactions
        ↓
load_to_postgres
```

Сначала Python-скрипт генерирует тестовые банковские транзакции. Затем данные проходят проверки качества. Валидные и ошибочные записи разделяются, после чего результат загружается в PostgreSQL.

Последовательность запуска задач контролирует Apache Airflow.

## Архитектура

```text
                 Генератор транзакций
                        Python
                          │
                          ▼
                  transactions.csv
                          │
                          ▼
                   DQ-валидация
                   Python / pandas
                          │
                ┌─────────┴─────────┐
                │                   │
                ▼                   ▼
              valid              rejected
                │                   │
                ▼                   ▼
             staging             rejected
                │                   │
                └─────────┬─────────┘
                          │
                          ▼
                     PostgreSQL
```

Инфраструктура запускается через Docker Compose:

```text
Docker Compose
├── PostgreSQL
└── Apache Airflow
```

## Стек

- Python
- SQL
- PostgreSQL
- pandas
- psycopg2
- Apache Airflow
- Docker
- Docker Compose
- Git

## Данные

В проекте используются три основных сущности:

- клиенты;
- банковские счета;
- транзакции.

Для тестирования пайплайна транзакции генерируются автоматически.

Генератор создаёт 100 записей и специально добавляет небольшое количество некорректных данных. Например, транзакцию с отрицательной суммой или ссылкой на несуществующий счёт.

Это позволяет проверить не только успешную загрузку, но и обработку плохих записей.

## Слои PostgreSQL

### Raw

```text
raw_customers
raw_accounts
raw_transactions
```

Raw хранит входные данные до фильтрации.

На этом уровне намеренно нет жёстких ограничений, которые могли бы не дать сохранить плохую запись. Если источник прислал некорректные данные, их сначала нужно сохранить и увидеть, а уже затем обработать.

### Staging

```text
stg_transactions
```

Здесь находятся транзакции, которые прошли проверки качества.

Для staging используются более строгие ограничения. Например, `transaction_id` является первичным ключом, а сумма транзакции должна быть положительной.

### Rejected

```text
rejected_transactions
```

Сюда попадают записи, которые не прошли валидацию.

Вместе с исходными полями сохраняется `reject_reasons`, поэтому можно понять причину отклонения записи.

Например:

```text
INVALID_AMOUNT
ACCOUNT_NOT_FOUND
```

У одной транзакции может быть сразу несколько причин отклонения.

## Проверки качества данных

Сейчас реализованы две основные проверки.

### Сумма транзакции

Сумма должна быть больше нуля:

```text
amount > 0
```

Если условие нарушено, запись получает:

```text
INVALID_AMOUNT
```

### Существование счёта

`account_id` транзакции должен существовать среди банковских счетов.

Если счёт не найден:

```text
ACCOUNT_NOT_FOUND
```

После разделения данных дополнительно проверяется инвариант:

```text
raw_transactions =
stg_transactions +
rejected_transactions
```

То есть каждая входная транзакция должна оказаться либо среди валидных, либо среди отклонённых.

## Загрузка в PostgreSQL

Для массовой загрузки используется PostgreSQL `COPY` через `psycopg2`.

```text
customers.csv
        → raw_customers

accounts.csv
        → raw_accounts

transactions.csv
        → raw_transactions

valid_transactions.csv
        → stg_transactions

rejected_transactions.csv
        → rejected_transactions
```

Загрузка выполняется внутри одной транзакции.

Если все этапы завершились успешно:

```text
COMMIT
```

Если во время загрузки возникает ошибка:

```text
ROLLBACK
```

Поэтому неуспешный запуск не должен оставлять базу в частично загруженном состоянии.

Для повторного полного запуска таблицы очищаются через `TRUNCATE`, после чего данные загружаются заново.

## Airflow

Airflow отвечает за порядок выполнения Python-скриптов.

DAG:

```text
generate_transactions
        ↓
validate_transactions
        ↓
load_to_postgres
```

`validate_transactions` запускается только после успешной генерации данных, а загрузка в PostgreSQL — только после успешной валидации.

## Структура проекта

```text
banking-etl-pipeline/
├── dags/
│   └── banking_pipeline_dag.py
│
├── data/
│   ├── customers.csv
│   ├── accounts.csv
│   ├── transactions.csv
│   ├── valid_transactions.csv
│   └── rejected_transactions.csv
│
├── src/
│   ├── generate_transactions.py
│   ├── validate_transactions.py
│   └── load_to_postgres.py
│
├── sql/
│   └── 001_create_tables.sql
│
├── tests/
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Запуск

Поднять контейнеры:

```bash
docker compose up -d
```

Проверить состояние:

```bash
docker compose ps
```

Создать таблицы PostgreSQL:

```bash
docker compose exec -T postgres \
psql -U banking_user -d banking \
< sql/001_create_tables.sql
```

После запуска Airflow интерфейс доступен на порту `8080`.

В Airflow нужно запустить DAG:

```text
banking_pipeline
```

После выполнения можно проверить результат в PostgreSQL:

```sql
SELECT COUNT(*) FROM raw_transactions;
SELECT COUNT(*) FROM stg_transactions;
SELECT COUNT(*) FROM rejected_transactions;
```

Количество строк в `stg_transactions` и `rejected_transactions` в сумме должно совпадать с количеством исходных транзакций.

## Что я отработал в этом проекте

На проекте я практически разобрал:

- построение простого ETL-пайплайна;
- разделение данных на raw, staging и rejected;
- проверки Data Quality;
- обработку некорректных записей;
- загрузку CSV в PostgreSQL;
- `COPY`;
- транзакции, `COMMIT` и `ROLLBACK`;
- повторный batch-запуск;
- зависимости между задачами в Airflow;
- запуск PostgreSQL и Airflow через Docker Compose;
- взаимодействие контейнеров через Docker network.
