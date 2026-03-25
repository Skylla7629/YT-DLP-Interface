import os
from tkinter import filedialog

def get_directory(title="Select Directory"):
    return filedialog.askdirectory(title=title)


def get_subfolders(directory):
    dirs = os.scandir(directory)

    subfolders = {}

    for direct in dirs:
        if direct.is_dir():
            subfolders[direct.name] = direct.path

    return subfolders


def get_files(directory):
    files = os.scandir(directory)

    file_list = []

    for file in files:
        if file.is_file():
            file_list.append(file.name)

    return file_list


def removeDuplicates(duplicates, directory):
    for i, file in enumerate(duplicates):
        print(f"Removing: ({i}) {directory}/{file}")
        os.remove(f"{directory}/{file}")



def main():
    directory = get_directory()
    subfolders = get_subfolders(directory)
    dirToCheck = get_directory(title="Select Directory to check for duplicates")
    filesToCheck = get_files(dirToCheck)
    files = []
    # print(subfolders)
    # print(filesToCheck)
    # print(dirToCheck)
    for foldername, path in subfolders.items():
        if path.split("\\")[-1] == dirToCheck.split("/")[-1]:
            continue
        files += get_files(path)
    # print(files)

    duplicates = []
    for file in filesToCheck:
        if file in files:
            duplicates.append(file)

    print(f"Duplicates: {duplicates}")
    x = input("Remove all duplicates? (Y/n) ")
    match x:
        case "Y":
            removeDuplicates(duplicates, dirToCheck)
        case "n":
            pass
        case _:
            pass
        


if __name__ == "__main__":
    main()


# EOF