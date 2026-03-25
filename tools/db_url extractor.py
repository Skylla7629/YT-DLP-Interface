## tool to extract the url from the database

from tkinter import filedialog
import sqlite3
import json




def main():
    path = filedialog.askopenfilename(title="Select Database")
    dbconnection = sqlite3.connect(path)
    cursor = dbconnection.cursor()

    cursor.execute("SELECT url FROM titles")
    data = cursor.fetchall()
    urls = []
    for url in data:
        urls.append(url[0].strip())

    with open('urls.json', 'w') as f:
        json.dump(urls, f, indent=4)


if __name__ == "__main__":
    main()


# EOF