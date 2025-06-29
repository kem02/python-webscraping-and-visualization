import sqlite3
import csv


def create_table(cursor, create_sql):
    cursor.execute(create_sql)


def import_csv_to_table(cursor, csv_path, insert_sql, transform_row):
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader)
        for csv_row in csv_reader:
            record_values = transform_row(csv_row)
            if not record_values:
                continue
            try:
                cursor.execute(insert_sql, record_values)
            except Exception as error:
                print(f"Failed to insert record {csv_row}: {error}")


# Open the database connection
connection = sqlite3.connect("mlb_stats.db")
db_cursor = connection.cursor()

# batting_avg table and import
create_table(
    db_cursor,
    """
    CREATE TABLE IF NOT EXISTS batting_avg (
        id INTEGER PRIMARY KEY,
        League TEXT,
        Name TEXT,
        Team TEXT,
        Batting_Average REAL,
        Year INTEGER
    )
""",
)
import_csv_to_table(
    db_cursor,
    "batting_average_records.csv",
    "INSERT INTO batting_avg (League, Name, Team, Batting_Average, Year) VALUES (?, ?, ?, ?, ?)",
    lambda csv_row: (csv_row[1], csv_row[2], csv_row[3], csv_row[4], csv_row[5]),
)

# home_runs table and import
create_table(
    db_cursor,
    """
    CREATE TABLE IF NOT EXISTS home_runs (
        id INTEGER PRIMARY KEY,
        Name TEXT,
        Career_Home_Runs INTEGER
    )
""",
)
import_csv_to_table(
    db_cursor,
    "career_home_run_records.csv",
    "INSERT INTO home_runs (Name, Career_Home_Runs) VALUES (?, ?)",
    lambda csv_row: (csv_row[1], csv_row[2]),
)

# career_strikeouts table and import
create_table(
    db_cursor,
    """
    CREATE TABLE IF NOT EXISTS career_strikeouts (
        id INTEGER PRIMARY KEY,
        League TEXT,
        Name TEXT,
        Career_Strikeouts INTEGER
    )
""",
)


def strikeout_transform(csv_row):
    if not csv_row or len(csv_row) < 4:
        print("Malformed CSV row ignored:", csv_row)
        return None
    return (csv_row[1], csv_row[2], csv_row[3])


import_csv_to_table(
    db_cursor,
    "career_strikeout_records.csv",
    "INSERT INTO career_strikeouts (League, Name, Career_Strikeouts) VALUES (?, ?, ?)",
    strikeout_transform,
)


connection.commit()
connection.close()
print("Import process completed; mlb_stats.db is now populated.")
