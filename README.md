# ynab_to_monarch
Simple csv converter that converts from ynab exported csv to monarch

## Usage
```
python main.py --ynab_csv=<full-path-to-ynab-csv> --monarch_dir=<full-path-to-monarch-dir>
```

* --monarch_dir defaults to the current directory.
* The output will be a bunch of csv files grouped by accounts. This is just how monarch imports transactions