import csv

with open('response_to_loom.csv', mode='rt', newline='') as data, open('response_to_loom_sorted.csv', 'w', newline='') as sorted_data:
    writer = csv.writer(sorted_data, delimiter=',')
    reader = csv.reader(data, delimiter=',')
    writer.writerow(next(reader))
    data = sorted(reader, key=lambda row: (row[0], int(row[3])))        
    for row in data:
        writer.writerow(row)