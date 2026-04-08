import argparse
import os
from datetime import date, datetime

import runtime_compat
import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert as pg_insert


load_dotenv()

DEFAULT_SQLITE_PATH = os.environ.get(
    "SQLITE_DB_PATH",
    os.path.join(os.path.dirname(__file__), "instance", "vocabai.db"),
)


def normalize_postgres_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def resolve_database_urls(sqlite_url_arg: str | None, postgres_url_arg: str | None) -> tuple[str, str]:
    sqlite_url = sqlite_url_arg or os.environ.get("SQLITE_DATABASE_URL", "").strip()
    if not sqlite_url:
        sqlite_path = os.environ.get("SQLITE_DB_PATH", DEFAULT_SQLITE_PATH)
        sqlite_url = f"sqlite:///{sqlite_path}"

    postgres_url = postgres_url_arg or os.environ.get("POSTGRES_DATABASE_URL", "").strip()
    if not postgres_url:
        postgres_url = os.environ.get("DATABASE_URL", "").strip()
    postgres_url = normalize_postgres_url(postgres_url)

    if not postgres_url:
        raise ValueError(
            "PostgreSQL URL is required. Set POSTGRES_DATABASE_URL or DATABASE_URL, "
            "or pass --postgres-url."
        )

    return sqlite_url, postgres_url


def reflect_database(url: str) -> tuple[sa.Engine, sa.MetaData]:
    engine = sa.create_engine(url, future=True)
    metadata = sa.MetaData()
    with engine.connect() as conn:
        metadata.reflect(bind=conn)
    return engine, metadata


def count_rows(conn: sa.Connection, table: sa.Table) -> int:
    return conn.execute(sa.select(sa.func.count()).select_from(table)).scalar_one()


def normalize_required_value(column: sa.Column, value):
    if value is not None or column.nullable:
        return value

    if isinstance(column.type, sa.Date):
        return date.today()
    if isinstance(column.type, sa.DateTime):
        return datetime.utcnow()
    if isinstance(column.type, sa.Boolean):
        return False
    if isinstance(column.type, sa.Integer):
        return 0
    if isinstance(column.type, (sa.String, sa.Text)):
        return ""
    return value


def normalize_column_value(column: sa.Column, value):
    normalized = normalize_required_value(column, value)
    truncated = False
    if (
        normalized is not None
        and isinstance(normalized, str)
        and isinstance(column.type, sa.String)
        and column.type.length
        and len(normalized) > column.type.length
    ):
        normalized = normalized[: column.type.length]
        truncated = True
    return normalized, truncated


def copy_table_rows(
    src_conn: sa.Connection,
    dst_conn: sa.Connection,
    src_table: sa.Table,
    dst_table: sa.Table,
    chunk_size: int,
) -> tuple[int, int, int]:
    copied_attempts = 0
    truncated_values = 0
    src_count = count_rows(src_conn, src_table)
    pk_columns = [column.name for column in dst_table.primary_key.columns]

    result = src_conn.execute(sa.select(src_table))
    while True:
        batch = result.mappings().fetchmany(chunk_size)
        if not batch:
            break

        payload = []
        for row in batch:
            # Keep values exactly as-is so NULL/empty-string semantics are preserved.
            normalized_row = {}
            for column in dst_table.columns:
                normalized_value, was_truncated = normalize_column_value(column, row.get(column.name))
                normalized_row[column.name] = normalized_value
                if was_truncated:
                    truncated_values += 1
            payload.append(normalized_row)

        if payload:
            if pk_columns:
                stmt = pg_insert(dst_table).values(payload).on_conflict_do_nothing(index_elements=pk_columns)
            else:
                stmt = pg_insert(dst_table).values(payload).on_conflict_do_nothing()
            dst_conn.execute(stmt)
            copied_attempts += len(payload)

    return src_count, copied_attempts, truncated_values


def fix_sequences(dst_conn: sa.Connection, dst_meta: sa.MetaData) -> None:
    inspector = sa.inspect(dst_conn)
    for table in dst_meta.sorted_tables:
        pk = inspector.get_pk_constraint(table.name, schema=table.schema).get("constrained_columns") or []
        if len(pk) != 1:
            continue

        pk_name = pk[0]
        pk_col = table.c.get(pk_name)
        if pk_col is None or not isinstance(pk_col.type, sa.Integer):
            continue

        qualified_name = table.name if table.schema is None else f"{table.schema}.{table.name}"
        sequence_name = dst_conn.execute(
            sa.text("SELECT pg_get_serial_sequence(:table_name, :column_name)"),
            {"table_name": qualified_name, "column_name": pk_name},
        ).scalar_one_or_none()

        if not sequence_name:
            continue

        max_id = dst_conn.execute(sa.select(sa.func.max(pk_col))).scalar_one()
        row_count = count_rows(dst_conn, table)
        next_value = max_id if max_id is not None else 1
        is_called = row_count > 0

        dst_conn.execute(
            sa.text("SELECT setval(:sequence_name, :next_value, :is_called)"),
            {
                "sequence_name": sequence_name,
                "next_value": int(next_value),
                "is_called": is_called,
            },
        )


def migrate(sqlite_url: str, postgres_url: str, chunk_size: int) -> int:
    sqlite_engine, sqlite_meta = reflect_database(sqlite_url)
    postgres_engine, postgres_meta = reflect_database(postgres_url)

    sqlite_tables = {table.name for table in sqlite_meta.sorted_tables}
    postgres_tables = {table.name for table in postgres_meta.sorted_tables}
    missing_tables = sorted(sqlite_tables - postgres_tables)
    if missing_tables:
        raise RuntimeError(
            "PostgreSQL is missing tables. Run Flask migrations first. Missing: "
            + ", ".join(missing_tables)
        )

    table_reports: list[tuple[str, int, int, int]] = []
    with sqlite_engine.connect() as src_conn, postgres_engine.begin() as dst_conn:
        for src_table in sqlite_meta.sorted_tables:
            dst_table = postgres_meta.tables[src_table.key]
            src_count, _, truncated_values = copy_table_rows(src_conn, dst_conn, src_table, dst_table, chunk_size)
            dst_count = count_rows(dst_conn, dst_table)
            table_reports.append((src_table.name, src_count, dst_count, truncated_values))

        fix_sequences(dst_conn, postgres_meta)

    print("Migration summary:")
    missing_data = False
    for table_name, src_count, dst_count, truncated_values in table_reports:
        status = "OK" if dst_count >= src_count else "MISSING_ROWS"
        if status != "OK":
            missing_data = True
        print(
            f" - {table_name}: sqlite={src_count}, postgres={dst_count}, "
            f"truncated_values={truncated_values} [{status}]"
        )

    if missing_data:
        print("Completed with errors: PostgreSQL row count is lower than SQLite for one or more tables.")
        return 1

    print("Completed successfully: PostgreSQL contains all rows from SQLite.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Migrate all data from SQLite to PostgreSQL.")
    parser.add_argument("--sqlite-url", default=None, help="SQLAlchemy URL for SQLite source database")
    parser.add_argument("--postgres-url", default=None, help="SQLAlchemy URL for PostgreSQL target database")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Batch size for inserts")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    source_url, target_url = resolve_database_urls(args.sqlite_url, args.postgres_url)
    # Strip credentials from logs while still showing which DBs are selected.
    print(f"SQLite source: {source_url}")
    print(f"PostgreSQL target host: {sa.engine.url.make_url(target_url).host}")
    raise SystemExit(migrate(source_url, target_url, args.chunk_size))
