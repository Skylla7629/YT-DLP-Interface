import json
from tkinter import filedialog

def main():
    file = filedialog.askopenfilename(title="Select JSON file")
    with open(file, 'r') as f:
        data = json.load(f)

    with open(f"{file[:-5]}-formatted.json", 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == "__main__":
    main()


# EOF