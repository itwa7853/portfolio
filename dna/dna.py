from cs50 import get_string
from sys import argv, exit
import csv

def main():
    if (len(argv) != 3):
        print("Usage: python dna.py data.csv sequence.txt")
        exit(1)

    people = []
    i = 0
    with open(argv[1], newline='') as databaseFile:
        database = csv.reader(databaseFile, delimiter=',')
        for row in database:
            people.append({
                "Name": row[0],
                "Strand": []
            })
            for j in range(len(row)):
                if (j < 1):
                    continue
                people[i]['Strand'].append(row[j])
            i += 1


    everyPiece = people[0]['Strand']

    with open(argv[2], newline='') as sequenceFile:
        sequence = sequenceFile.read()
        arrayOfAppearances = []
        for piece in everyPiece:
            arrayOfAppearances.append(getMaxTimes(sequence, piece))

        for person in people:
            i = 0
            counter = 0
            while (i < len(arrayOfAppearances)):
                if (str(arrayOfAppearances[i]) == person['Strand'][i]):
                    counter += 1
                if (counter == len(arrayOfAppearances) - 1):
                    print(person['Name'])
                    return
                i += 1
        print("No match")


def getMaxTimes(longDna, piece):
    arrayOfNumbers = [0] * len(longDna)
    for i in range(len(longDna) - len(piece), -1, -1):
        if longDna[i: i + len(piece)] == piece:
            if i + len(piece) > len (longDna) - 1:
                arrayOfNumbers[i] = 1
            else:
                arrayOfNumbers[i] = 1 + arrayOfNumbers[i+ len(piece)]
    return max(arrayOfNumbers)

main()