import sqlite3
import common_functions

DEFAULT_PATH = common_functions.resource_path('database.sqlite3')


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

    slack_msg_query = """
        CREATE TABLE IF NOT EXISTS slack_msg (
        id INTEGER PRIMARY KEY,
        channel_name TEXT NOT NULL,
        subject TEXT NOT NULL,
        body TEXT NOT NULL,
        attachment TEXT,
        is_sent VARCHAR(6) DEFAULT 'False')"""

    external_api_msg_query = """
    CREATE TABLE IF NOT EXISTS external_api_msg (
    id INTEGER PRIMARY KEY,
    json_data TEXT NOT NULL,
    is_sent VARCHAR(6) DEFAULT 'False')"""

    conn = db_connect()
    try:
        cursor = conn.cursor()
        cursor.execute(notables)
        cursor.execute(email_msg_query)
        cursor.execute(slack_msg_query)
        cursor.execute(external_api_msg_query)
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


def insert_slack_msg(msg_dict):
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO slack_msg (channel_name, subject, body, attachment)
            VALUES (?, ?, ?, ?)"""

        cursor.execute(query,
                       (
                           msg_dict["channel_name"],
                           msg_dict["subject"],
                           msg_dict["body"],
                           msg_dict["attachment"]))
        return cursor.lastrowid
    except:
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()


def insert_external_api_msg(msg_json_data64):
    conn = db_connect()
    try:
        cursor = conn.cursor()

        data = (msg_json_data64,)
        cursor.execute('INSERT INTO external_api_msg(json_data) VALUES (?)', data)
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


def delete_slack_msg(msg_id):
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """DELETE FROM slack_msg WHERE id=?"""
        cursor.execute(query, (msg_id,))
        return cursor.rowcount
    except:
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()


def delete_external_api_msg(msg_id):
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """DELETE FROM external_api_msg WHERE id=?"""
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


def get_unsent_slack_messages():
    conn = db_connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM slack_msg WHERE is_sent='False' LIMIT 50")
        rows = cursor.fetchall()
        list_messages = []
        for row in rows:
            msg = {
                "id": row[0],
                "channel_name": row[1],
                "subject": row[2],
                "body": row[3],
                "attachments": row[4],
                "is_sent": row[5]
            }
            list_messages.append(msg)
        return list_messages
    except:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_unsent_external_api_messages():
    conn = db_connect()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM external_api_msg WHERE is_sent='False' LIMIT 50")
        rows = cursor.fetchall()
        list_messages = []
        for row in rows:
            msg = {
                "id": row[0],
                "json_data": row[1],
                "is_sent": row[2]
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


def delete_slack_sent_messages():
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """DELETE FROM slack_msg WHERE is_sent=?"""
        cursor.execute(query, ("True",))
        return cursor.rowcount
    except:
        conn.rollback()
        raise
    finally:
        conn.commit()
        conn.close()


def delete_external_api_sent_messages():
    conn = db_connect()
    try:
        cursor = conn.cursor()
        query = """DELETE FROM external_api_msg WHERE is_sent=?"""
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
