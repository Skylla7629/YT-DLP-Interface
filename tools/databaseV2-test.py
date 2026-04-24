import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from database_v2 import Database


def main():
    db = Database()
    db.main_table_init()


if __name__ == "__main__":
    main()


# EOF
