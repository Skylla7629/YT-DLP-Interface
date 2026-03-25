import json

def main():
    with open('row.json', 'r') as f:
        data = json.load(f)

    outDict = {}
    for x in data:
        name = input(f"Enter the name {x[1]}: ")
        outDict[name] = {
            'title': name,
            'url': x[8],
            'description': x[9],
            'releaseDate': x[7]
        }
    
    with open('row_base.json', 'w') as f:
        json.dump(outDict, f, indent=4)
    


if __name__ == "__main__":
    main()



# EOF