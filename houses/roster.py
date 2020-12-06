from sys import argv, exit
from cs50 import SQL
db = SQL("sqlite:///students.db")

if (len(argv) != 2):
    print("incorrect arguments")
    exit(1)

house = argv[1]
returnstatement = db.execute("SELECT first, middle, last, birth FROM students WHERE house = ? ORDER BY last ASC", house)

for obj in returnstatement:
    returnString = obj['first'] + ' '
    if (obj['middle'] != None):
        returnString += obj['middle'] + ' '
    returnString += obj['last'] + ', born ' + str(obj['birth'])
    print (returnString)