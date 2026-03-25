import sqlite3
from tkinter import filedialog


def change_flag(c, flag, id=None):
    if id:
        query = f"UPDATE titles SET itunes = ? WHERE id = {id}"
        c.execute(query, (flag,))
    else:
        query = f"UPDATE titles SET itunes = ?"
        c.execute(query, (flag,))



def main():
    db_path = filedialog.askopenfilename(title="Select database")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    change_flag(c, int(input("Flag (0/1): ")))

    conn.commit()
    conn.close()



if __name__ == "__main__":
    main()


# EOF