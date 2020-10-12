import sqlite3
import os


DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


def get_db_path():
    global DEFAULT_PATH
    return DEFAULT_PATH


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def create_tables():

    notables = """
    CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id TEXT NOT NULL UNIQUE ON CONFLICT IGNORE)"""

    email_msg_query = """
    CREATE TABLE IF NOT EXISTS email_msg (
    id INTEGER PRIMARY KEY,
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    attachment TEXT,
    is_sent VARCHAR(6) DEFAULT 'False')"""

    conn = db_connect()
    try:
        cursor = conn.cursor()
        cursor.execute(notables)
        cursor.execute(email_msg_query)
    except:
        pass
    finally:
        conn.commit()
        conn.close()


def is_event_already_processed(event_id):
    conn = db_connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM events WHERE event_id=? LIMIT 1", (event_id,))

        rows = cursor.fetchall()
        return len(rows) > 0
    except:
        conn.rollback()
    finally:
        conn.close()


def insert_event_info(event_info_dict):
    conn = db_connect()
    try:
        cursor = conn.cursor()

        event_id = (event_info_dict['event_id'],)
        cursor.execute('INSERT INTO events(event_id) VALUES (?)', event_id)
        return cursor.lastrowid
    except:
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()


def insert_email_msg(email_msg_dict):
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO email_msg (subject, body, attachment)
            VALUES (?, ?, ?)"""

        cursor.execute(query,
                       (
                           email_msg_dict["subject"],
                           email_msg_dict["body"],
                           email_msg_dict["attachment"]))
        return cursor.lastrowid
    except:
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()


def delete_msg(msg_id):
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """DELETE FROM email_msg WHERE id=?"""
        cursor.execute(query, (msg_id,))
        return cursor.rowcount
    except:
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()


def get_unsent_messages():
    conn = db_connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM email_msg WHERE is_sent='False' LIMIT 15")
        rows = cursor.fetchall()
        list_messages = []
        for row in rows:
            msg = {
                "id": row[0],
                "subject": row[1],
                "body": row[2],
                "attachments": row[3],
                "is_sent": row[4]
            }
            list_messages.append(msg)

        return list_messages
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_sent_messages():
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """DELETE FROM email_msg WHERE is_sent=?"""
        cursor.execute(query, ("True",))
        return cursor.rowcount
    except:
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()



# init the database, if no db file or tables, it will be created here
create_tables()