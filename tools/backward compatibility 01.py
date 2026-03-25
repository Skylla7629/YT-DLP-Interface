## make old json compatible

import json
from tkinter import filedialog


def load_json(file):
    try:
        with open(file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data


def save_json(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)


def reformat(data_old):
    data_new = {}
    for key in data_old:
        date = data_old[key][1].split(".")
        date = f"{date[2]}-{date[1]}-{date[0]}"
        data_new[key] = {
            "title": key,
            "url": data_old[key][0],
            "description": data_old[key][2],
            "releaseDate": date
        } 
    return data_new


def main():
    file = filedialog.askopenfilename(title="Select old file")
    data = load_json(file)
    data_new = reformat(data)
    save_json(file, data_new)




if __name__ == "__main__":
    main()