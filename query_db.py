import sqlite3


def print_query_results(cursor):
    # Get column names
    column_names = [description[0] for description in cursor.description]
    # Print header
    print(" | ".join(column_names))
    print("-" * (len(" | ".join(column_names))))
    # Print rows
    for row in cursor.fetchall():
        print(" | ".join(str(value) for value in row))
    print()


def prompt_single_table(cursor):
    table_name = input(
        "Which table? (batting_avg, home_runs, career_strikeouts): "
    ).strip()
    if table_name not in ("batting_avg", "home_runs", "career_strikeouts"):
        print("Unknown table.\n")
        return

    filters = []
    if table_name == "batting_avg":
        year_filter = input("Filter by Year (leave blank for any): ").strip()
        if year_filter:
            filters.append(f"Year = {int(year_filter)}")

    minimum_filter = input("Minimum stat value (leave blank for any): ").strip()
    if minimum_filter:
        stat_column = {
            "batting_avg": "Batting_Average",
            "home_runs": "Career_Home_Runs",
            "career_strikeouts": "Career_Strikeouts",
        }[table_name]
        filters.append(f"{stat_column} >= {float(minimum_filter)}")

    sql = f"SELECT * FROM {table_name}"
    if filters:
        sql += " WHERE " + " AND ".join(filters)

    order_clause = {
        "batting_avg": " ORDER BY Batting_Average DESC",
        "home_runs": " ORDER BY Career_Home_Runs DESC",
        "career_strikeouts": " ORDER BY Career_Strikeouts DESC",
    }[table_name]
    sql += order_clause

    top_n = input("Limit to top N rows (leave blank for all): ").strip()
    if top_n:
        sql += f" LIMIT {int(top_n)}"

    try:
        cursor.execute(sql)
        print_query_results(cursor)
    except Exception as error:
        print(f"Error running query: {error}\n")


def prompt_player_stats(cursor):
    player_name = input("Enter the exact player name: ").strip()
    sql = """
    SELECT
      b.Name,
      b.League,
      b.Team,
      b.Batting_Average,
      b.Year,
      hr.Career_Home_Runs,
      so.Career_Strikeouts
    FROM batting_avg AS b
      LEFT JOIN home_runs         AS hr ON b.Name = hr.Name
      LEFT JOIN career_strikeouts AS so ON b.Name = so.Name
    WHERE b.Name = ?
    """
    try:
        cursor.execute(sql, (player_name,))
        if cursor.description is None:
            print("No data returned.\n")
            return
        print_query_results(cursor)
    except Exception as error:
        print(f"Query error: {error}\n")


def prompt_custom_sql(cursor):
    raw_sql = input("Enter your SQL statement (end with a semicolon):\n")
    try:
        cursor.execute(raw_sql)
        print_query_results(cursor)
    except Exception as error:
        print(f"Custom query failed: {error}\n")


def main():
    connection = sqlite3.connect("mlb_stats.db")
    db_cursor = connection.cursor()

    menu = (
        "1) Query a single table\n"
        "2) Lookup stats by player name\n"
        "3) Run custom SQL\n"
        "4) Exit\n"
        "Choose an option: "
    )

    while True:
        choice = input(menu).strip()
        if choice == "1":
            prompt_single_table(db_cursor)
        elif choice == "2":
            prompt_player_stats(db_cursor)
        elif choice == "3":
            prompt_custom_sql(db_cursor)
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid selection.\n")

    connection.close()


if __name__ == "__main__":
    main()
