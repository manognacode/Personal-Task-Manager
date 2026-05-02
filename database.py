"""
Database layer for Task Manager
Handles all SQLite operations with parameterized queries to prevent SQL injection
"""
import sqlite3
import os
from datetime import datetime

DEFAULT_DB_NAME = 'database.db'


def load_env():
    """Load environment variables from .env file"""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    if key not in os.environ:
                        os.environ[key] = value


load_env()


def get_db_path():
    """Get database path from environment or use default"""
    db_folder = os.path.dirname(os.path.abspath(__file__))
    db_name = os.environ.get('DB_NAME', DEFAULT_DB_NAME)
    return os.path.join(db_folder, db_name)


DB_PATH = get_db_path()


def get_db_connection():
    """Create and return a database connection with row factory"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database with schema"""
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')

    conn = get_db_connection()
    cursor = conn.cursor()

    with open(schema_path, 'r') as f:
        schema = f.read()
        cursor.executescript(schema)

    conn.commit()
    conn.close()


def get_all_tasks(status=None, priority=None, search=None, sort_by=None):
    """
    Get all tasks with optional filtering, searching, and sorting
    Uses parameterized queries to prevent SQL injection
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM tasks WHERE 1=1"
    params = []

    if status and status != 'all':
        query += " AND status = ?"
        params.append(status)

    if priority and priority != 'all':
        query += " AND priority = ?"
        params.append(priority)

    if search:
        query += " AND title LIKE ?"
        params.append(f'%{search}%')

    if sort_by:
        if sort_by == 'due_date_asc':
            query += " ORDER BY due_date ASC"
        elif sort_by == 'due_date_desc':
            query += " ORDER BY due_date DESC"
        elif sort_by == 'priority_high':
            query += " ORDER BY CASE priority WHEN 'High' THEN 1 WHEN 'Medium' THEN 2 WHEN 'Low' THEN 3 END"
        elif sort_by == 'priority_low':
            query += " ORDER BY CASE priority WHEN 'Low' THEN 1 WHEN 'Medium' THEN 2 WHEN 'High' THEN 3 END"
    else:
        query += " ORDER BY created_at DESC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_task_by_id(task_id):
    """Get a single task by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def create_task(title, description, due_date, status, priority):
    """Create a new task"""
    conn = get_db_connection()
    cursor = conn.cursor()

    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute("""
        INSERT INTO tasks (title, description, due_date, status, priority, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title, description, due_date, status, priority, created_at))

    task_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def update_task(task_id, title, description, due_date, status, priority):
    """Update an existing task"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE tasks
        SET title = ?, description = ?, due_date = ?, status = ?, priority = ?
        WHERE id = ?
    """, (title, description, due_date, status, priority, task_id))

    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def delete_task(task_id):
    """Delete a task by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    conn.commit()
    conn.close()

    return True


def update_task_status(task_id, status):
    """Update only the status of a task (for quick toggle)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))

    conn.commit()
    conn.close()

    return get_task_by_id(task_id)


def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM tasks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) as pending FROM tasks WHERE status = 'Pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) as done FROM tasks WHERE status = 'Done'")
    done = cursor.fetchone()[0]

    today = datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT COUNT(*) as overdue FROM tasks WHERE due_date < ? AND status != 'Done'", (today,))
    overdue = cursor.fetchone()[0]

    conn.close()

    return {
        'total': total,
        'pending': pending,
        'done': done,
        'overdue': overdue
    }


if __name__ == '__main__':
    init_database()
    print("Database initialized successfully!")