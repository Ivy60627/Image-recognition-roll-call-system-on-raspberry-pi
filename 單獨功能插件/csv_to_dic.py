import csv

with open('student_name.csv', mode='r', encoding='utf-8') as inp:
    reader = csv.reader(inp)
    dict_from_csv = {rows[0]:rows[1] for rows in reader}

print(dict_from_csv)
