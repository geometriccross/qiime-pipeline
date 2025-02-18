import csv
from pathlib import Path

bat_csv = Path("meta/bat_fleas.csv")
cat_csv = Path("meta/cat_fleas.csv")
lip_csv = Path("meta/lip_cervi.csv")
mky_csv = Path("meta/mky_louse.csv")

try:
    bat = open(bat_csv, "r")
    cat = open(cat_csv, "r")
    lip = open(lip_csv, "r")
    mky = open(mky_csv, "r")

    csvs = [bat, cat, lip, mky]
    readers = [csv.reader(obj) for obj in csvs]

    # Get header and restore the moved seek
    master_header = bat.readline().replace("\n", "")
    bat.seek(0)

    master_list = []
    for reader in readers:
        header_removed = [row for row in reader][1:]
        for row in header_removed:
            master_list.append(row)

    print(master_header)
    for row in master_list:
        print(", ".join(row))

finally:
    bat.close()
    cat.close()
    lip.close()
    mky.close()
