import sqlite3
from typing import List


class SqlOperations:
    """
    A class that provides methods for performing SQL operations on a SQLite database.
    """

    def __init__(self, db_file: str):
        """
        :param db_file: The path to the SQLite database file.
        """
        self.db_file = db_file

    def create_table(self, table_name: str, columns: List[str]):
        """
        Creates a new table in the database.

        :param table_name: The name of the table to create.
        :param columns: The names of the columns in the table.
        """
        columns_str = ', '.join(columns)
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})")
            conn.commit()

    def insert_row(self, table_name: str, values: List):
        """
        Inserts a new row into a table in the database.

        :param table_name: The name of the table to insert the row into.
        :param values: The values to insert into the row.
        """
        placeholders = ', '.join(['?' for _ in values])
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", values)
            conn.commit()
