"""Core tools for database interrogation."""

from typing import Any

import aiosqlite
from structlog.stdlib import get_logger

log = get_logger()

DB_PATH = "data/dbs/local_debug.sqlite3"


async def list_tables_and_views() -> dict[str, Any]:
    """Lists all tables and views in the database.

    Returns:
        A dictionary with "tables" and "views" as keys.
    """
    log.info("Listing tables and views")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT type, name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
            results = await cursor.fetchall()
            db_objects: dict[str, Any] = {"tables": [], "views": []}
            for object_type, name in results:
                if "sqlite_" not in name:  # Filter out internal sqlite tables
                    if object_type == "table":
                        db_objects["tables"].append(name)
                    else:
                        db_objects["views"].append(name)
            log.info(
                "Finished listing tables and views",
                db_objects=db_objects,
            )
            return db_objects
    except aiosqlite.Error as e:
        log.error("Failed to list tables and views", error=e)
        return {"error": str(e)}


async def get_object_columns(object_name: str) -> list[dict[str, Any]]:
    """Gets column details for a specified table or view.

    Args:
        object_name: The name of the table or view.

    Returns:
        A list of dictionaries, where each dictionary contains the
        'name' and 'type' of a column, or an error dictionary.
    """
    log.info("Getting object columns", object_name=object_name)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # First, validate the object_name exists
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
            valid_objects = [row[0] for row in await cursor.fetchall()]
            if object_name not in valid_objects:
                log.warning("Object not found for columns", object_name=object_name)
                return [{"error": f"Object '{object_name}' not found."}]

            cursor = await db.execute(
                f"PRAGMA table_info(`{object_name}`)"  # noqa: S608
            )
            columns = await cursor.fetchall()
            column_details = [{"name": col[1], "type": col[2]} for col in columns]
            log.info(
                "Finished getting object columns",
                object_name=object_name,
                columns=column_details,
            )
            return column_details
    except aiosqlite.Error as e:
        log.error(
            "Failed to get object columns",
            object_name=object_name,
            error=e,
        )
        return [{"error": str(e)}]


async def get_object_summary(object_name: str) -> dict[str, Any]:
    """Gets a summary of a specified table or view.

    Args:
        object_name: The name of the table or view.

    Returns:
        A dictionary containing the row count and 3 sample rows,
        or an error dictionary.
    """
    log.info("Getting object summary", object_name=object_name)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # First, validate the object_name exists
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
            valid_objects = [row[0] for row in await cursor.fetchall()]
            if object_name not in valid_objects:
                log.warning("Object not found for summary", object_name=object_name)
                return {"error": f"Object '{object_name}' not found."}

            # Get row count
            cursor = await db.execute(
                f"SELECT COUNT(*) FROM `{object_name}`"  # noqa: S608
            )
            row_count = (await cursor.fetchone())[0]

            # Get sample rows
            cursor = await db.execute(
                f"SELECT * FROM `{object_name}` LIMIT 3"  # noqa: S608
            )
            rows = await cursor.fetchall()
            # Get column names for the sample rows
            column_names = [description[0] for description in cursor.description]
            sample_rows = [dict(zip(column_names, row, strict=False)) for row in rows]

            summary = {"row_count": row_count, "sample_rows": sample_rows}
            log.info(
                "Finished getting object summary",
                object_name=object_name,
                summary=summary,
            )
            return summary
    except aiosqlite.Error as e:
        log.error(
            "Failed to get object summary",
            object_name=object_name,
            error=e,
        )
        return {"error": str(e)}


async def get_view_definition(view_name: str) -> str:
    """Gets the CREATE VIEW statement for a specified view.

    Args:
        view_name: The name of the view.

    Returns:
        The SQL statement for the view, or an error dictionary.
    """
    log.info("Getting view definition", view_name=view_name)
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                "SELECT sql FROM sqlite_master WHERE type='view' AND name=?",
                (view_name,),
            )
            result = await cursor.fetchone()
            if result:
                log.info("Finished getting view definition", view_name=view_name)
                return result[0]
            else:
                log.warning("View not found", view_name=view_name)
                return f"View '{view_name}' not found."
    except aiosqlite.Error as e:
        log.error(
            "Failed to get view definition",
            view_name=view_name,
            error=e,
        )
        return str(e)
