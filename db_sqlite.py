import sqlite3


def insert_data(
    account_no, first_name, last_name, phone_no, email, complaint, date, status
):
    sqliteConnection = sqlite3.connect("sql.db")
    cursor = sqliteConnection.cursor()

    table = """CREATE TABLE IF NOT EXISTS complaints( account_no VARCHAR, first_name VARCHAR, last_name VARCHAR, phone_no VARCHAR, email VARCHAR, complaint VARCHAR, date VARCHAR, status VARCHAR)"""

    cursor.execute(table)

    cursor.execute(
        """INSERT INTO complaints(account_no, first_name, last_name, phone_no, email, complaint, date, status) VALUES(?, ?, ?, ?, ?, ?, ?, ?)""",
        (account_no, first_name, last_name, phone_no, email, complaint, date, status),
    )

    sqliteConnection.commit()

    sqliteConnection.close()
