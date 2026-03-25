
from tkinter import filedialog
import sqlite3
import json




def main():
    path = filedialog.askopenfilename(title="Select Database")
    dbconnection = sqlite3.connect(path)
    cursor = dbconnection.cursor()

    url = input("Enter the url you want to search for: ").replace('"', "")

    query = f"SELECT * FROM titles WHERE url LIKE '%{url}%'"

    cursor.execute(query)

    try:
        with open('row.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = []

    data.append(cursor.fetchone())

    with open('row.json', 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()


# EOF