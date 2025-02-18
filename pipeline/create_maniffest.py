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
