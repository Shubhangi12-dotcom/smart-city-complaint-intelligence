import sqlite3
from datetime import datetime


DATABASE_NAME = "complaints.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            complaint TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("PRAGMA table_info(complaints)")
    existing_columns = {
        row["name"]
        for row in cursor.fetchall()
    }

    new_columns = {
        "citizen_name": "TEXT",
        "contact": "TEXT",
        "location": "TEXT",
        "department": "TEXT",
        "response_time": "TEXT"
    }

    for column_name, column_type in new_columns.items():

        if column_name not in existing_columns:

            cursor.execute(
                f"ALTER TABLE complaints ADD COLUMN {column_name} {column_type}"
            )

    connection.commit()
    connection.close()


def add_complaint(
    complaint,
    category,
    priority,
    citizen_name,
    contact,
    location,
    department,
    response_time
):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO complaints
        (
            complaint,
            category,
            priority,
            status,
            created_at,
            citizen_name,
            contact,
            location,
            department,
            response_time
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        complaint,
        category,
        priority,
        "Pending",
        created_at,
        citizen_name,
        contact,
        location,
        department,
        response_time
    ))

    complaint_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return complaint_id


def get_all_complaints():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM complaints
        ORDER BY id DESC
    """)

    complaints = cursor.fetchall()

    connection.close()

    return complaints


def get_filtered_complaints(
    search="",
    category="",
    priority="",
    status=""
):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT *
        FROM complaints
        WHERE 1 = 1
    """

    parameters = []

    if search:

        query += """
            AND (
                LOWER(complaint) LIKE ?
                OR LOWER(location) LIKE ?
                OR LOWER(citizen_name) LIKE ?
                OR LOWER(category) LIKE ?
            )
        """

        search_value = f"%{search.lower()}%"

        parameters.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    if category:

        query += """
            AND category = ?
        """

        parameters.append(category)

    if priority:

        query += """
            AND priority = ?
        """

        parameters.append(priority)

    if status:

        query += """
            AND status = ?
        """

        parameters.append(status)

    query += """
        ORDER BY id DESC
    """

    cursor.execute(query, parameters)

    complaints = cursor.fetchall()

    connection.close()

    return complaints


def get_statistics():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM complaints
    """)

    total = cursor.fetchone()["count"]


    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE status = 'Pending'
    """)

    pending = cursor.fetchone()["count"]


    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE status = 'In Progress'
    """)

    in_progress = cursor.fetchone()["count"]


    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE status = 'Resolved'
    """)

    resolved = cursor.fetchone()["count"]


    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE priority = 'High'
    """)

    high_priority = cursor.fetchone()["count"]


    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE priority = 'Medium'
    """)

    medium_priority = cursor.fetchone()["count"]


    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM complaints
        WHERE priority = 'Low'
    """)

    low_priority = cursor.fetchone()["count"]


    cursor.execute("""
        SELECT category, COUNT(*) AS count
        FROM complaints
        GROUP BY category
        ORDER BY count DESC
    """)

    category_rows = cursor.fetchall()

    categories = {
        row["category"]: row["count"]
        for row in category_rows
    }


    connection.close()


    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "resolved": resolved,
        "high_priority": high_priority,
        "medium_priority": medium_priority,
        "low_priority": low_priority,
        "categories": categories
    }


def get_dashboard_insights():

    connection = get_connection()
    cursor = connection.cursor()


    # Most reported category

    cursor.execute("""
        SELECT category, COUNT(*) AS count
        FROM complaints
        GROUP BY category
        ORDER BY count DESC
        LIMIT 1
    """)

    category_row = cursor.fetchone()

    top_category = (
        category_row["category"]
        if category_row
        else "No data"
    )

    top_category_count = (
        category_row["count"]
        if category_row
        else 0
    )


    # Most reported location

    cursor.execute("""
        SELECT location, COUNT(*) AS count
        FROM complaints
        WHERE location IS NOT NULL
          AND TRIM(location) != ''
        GROUP BY location
        ORDER BY count DESC
        LIMIT 1
    """)

    location_row = cursor.fetchone()

    top_location = (
        location_row["location"]
        if location_row
        else "No data"
    )

    top_location_count = (
        location_row["count"]
        if location_row
        else 0
    )


    connection.close()


    return {
        "top_category": top_category,
        "top_category_count": top_category_count,
        "top_location": top_location,
        "top_location_count": top_location_count
    }


def update_status(complaint_id, new_status):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE complaints
        SET status = ?
        WHERE id = ?
    """, (
        new_status,
        complaint_id
    ))

    connection.commit()
    connection.close()