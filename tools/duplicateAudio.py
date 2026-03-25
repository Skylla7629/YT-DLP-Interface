import os


def get_directory(title="Select Directory"):
    print(title, end=" (path): ")
    return input()


def get_subfolders(directory):
    dirs = os.scandir(directory)

    subfolders = {}

    try:
        for direct in dirs:
            if direct.is_dir() and not os.path.islink(direct.path):
                subfolders[direct.name] = direct.path
                subfolders.update(get_subfolders(direct.path))
    except PermissionError:
        print(f"Permission denied (continue): {directory}")
    except FileNotFoundError:
        print("Internal error: Directory not found.")
        exit(1)
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
    directory = get_directory(title="Select Directory to use as Base")
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

    if not duplicates:
        print("No duplicates found.")
        return

    print(f"Found {len(duplicates)} duplicates:")
    for i, file in enumerate(duplicates):
        print(f"Duplicate: ({i}) {dirToCheck}/{file}")
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
