from cs50 import SQL
db = SQL("sqlite:///students.db")
from sys import argv, exit
import csv

# CREATE TABLE students (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     first VARCHAR(255),
#     middle VARCHAR(255),
#     last VARCHAR(255),
#     house VARCHAR(10),
#     birth INTEGER
# );

if (len(argv) != 2):
    print("Incorrect format")
    exit(1)

characters = argv[1]
with open (characters) as csvFile:
    file = csv.reader(csvFile)
    for row in file:
        name = row[0]
        splitNames = name.split()
        if (len(splitNames) == 3):
            #there's a middle name
            firstName = splitNames[0]
            middleName = splitNames[1]
            lastName = splitNames[2]
        elif (len(splitNames) == 2):
            #no middle name
            firstName = splitNames[0]
            middleName = None
            lastName = splitNames[1]
        else:
            continue
        db.execute("INSERT INTO students (first, middle, last, house, birth) VALUES (?, ?, ?, ?, ?)", firstName, middleName, lastName, row[1], row[2])
