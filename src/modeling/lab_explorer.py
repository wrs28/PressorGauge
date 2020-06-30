import os
import pandas as pd
import sys


mimic_dir = "/Volumes/gaia/mimic"
d_items = pd.read_csv(os.path.join(mimic_dir,"D_LABITEMS.csv"))


def find_label(label, category=None):
    if not category:
        return d_items[d_items.LABEL.str.contains(label,na=False)]
    else:
        return d_items[d_items.LABEL.str.contains(label,na=False) & d_items.CATEGORY.str.contains(category,na=False)]


def main():
    label = sys.argv[0]
    if len(sys.argv) < 3:
        category = sys.argv[2]
    else:
        category = None
    print(find_label(label, category))


# execute only if run as a script
if __name__ == "__main__":
    main()
