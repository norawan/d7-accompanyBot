from zipfile import ZipFile

def clearpath(inputStr):
    L = inputStr.split("/")
    return L[-1]

# unzips an mxl file string to an output xml
def unzip(fileString, outputString):
    name = clearpath(fileString).replace(".mxl", ".xml", 1)
    with ZipFile(fileString, 'r') as zObject:
        zObject.extract(member=name, path=outputString)


# example usage
'''unzip("C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/Outputs/Charlie_Brown_Theme_copy/Charlie_Brown_Theme_copy.mxl",
        "C:/Users/khand/OneDrive/Documents/GitHub/d7-accompanyBot/Outputs/Charlie_Brown_Theme_copy")'''