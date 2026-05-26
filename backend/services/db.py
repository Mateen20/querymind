from __future__ import annotations

import pymysql
import pymysql.cursors


def test_connection(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> dict:
    """Attempt a PyMySQL connection. Return success/failure dict."""
    connection: pymysql.connections.Connection | None = None
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5,
        )
        return {"success": True, "message": "Connected successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        if connection:
            connection.close()


def read_schema(
    host: str,
    port: int,
    user: str,
    password: str,
    database: str,
) -> dict:
    """Read INFORMATION_SCHEMA and return structured schema dict."""
    connection: pymysql.connections.Connection | None = None
    try:
        connection = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
            connect_timeout=5,
            cursorclass=pymysql.cursors.DictCursor,
        )
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_KEY
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """,
                (database,),
            )
            rows = cursor.fetchall()

        tables: dict[str, list[dict]] = {}
        total_columns = 0

        for row in rows:
            table = row["TABLE_NAME"]
            if table not in tables:
                tables[table] = []
            tables[table].append(
                {
                    "column_name": row["COLUMN_NAME"],
                    "data_type": row["DATA_TYPE"],
                    "is_nullable": row["IS_NULLABLE"],
                    "column_key": row["COLUMN_KEY"],
                }
            )
            total_columns += 1

        return {
            "tables": tables,
            "table_count": len(tables),
            "total_columns": total_columns,
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        if connection:
            connection.close()


def build_schema_prompt(schema: dict) -> str:
    """Convert schema dict to compact LLM-friendly string."""
    MAX_COLUMNS = 20
    lines: list[str] = []

    tables: dict[str, list[dict]] = schema.get("tables", {})
    for table_name, columns in tables.items():
        col_parts: list[str] = []
        for col in columns[:MAX_COLUMNS]:
            dtype = col["data_type"].upper()
            suffix = ""
            if col["column_key"] == "PRI":
                suffix = " PK"
            elif col["column_key"] == "MUL":
                suffix = " FK"
            elif col["column_key"] == "UNI":
                suffix = " UNI"
            col_parts.append(f"{col['column_name']} {dtype}{suffix}")

        if len(columns) > MAX_COLUMNS:
            col_parts.append(f"... +{len(columns) - MAX_COLUMNS} more")

        lines.append(f"Table: {table_name} ({', '.join(col_parts)})")

    return "\n".join(lines)
