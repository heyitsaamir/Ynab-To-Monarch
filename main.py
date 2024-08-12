import argparse
import datetime
import csv

###
# Date - YYYY-MM-DD
# Merchant
# Category
# Account
# Original Statement
# Notes
# Amount **
###
class Monarch:
    def __init__(self, date, merchant, category, account, original_statement, notes, amount):
        self.date = date
        self.merchant = merchant
        self.category = category
        self.account = account
        self.original_statement = original_statement
        self.notes = notes
        self.amount = amount

class Ynab:
    def __init__(self, account, flag, date, payee, category_group_category, category_group, category, memo, outflow, inflow, cleared):
        self.account = account
        self.flag = flag
        # date format: MM/DD/YYYY
        try:
            self.date = datetime.datetime.strptime(date, '%m/%d/%Y')
        except ValueError as e:
            print('Invalid date format:', date)
            raise e
        self.payee = payee
        self.category_group_category = category_group_category
        self.category_group = category_group
        self.category = category
        self.memo = memo
        try:
            self.outflow = float(outflow.replace('$', '')) if outflow else 0
        except ValueError as e:
            print('Invalid outflow:', outflow)
            raise e
            
        try:
            self.inflow = float(inflow.replace('$', '')) if inflow else 0
        except ValueError as e:
            print('Invalid inflow:', inflow)
            raise e
        self.cleared = cleared
        
    def to_monarch(self):
        return Monarch(
            self.date.strftime('%Y-%m-%d'),
            self.payee,
            self.category,
            self.account,
            self.memo,
            self.category_group_category,
            -1 * self.outflow if self.outflow else self.inflow
        )

def read_ynab_csv(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        rows = []
        did_skip_first_line = False
        spamreader = csv.reader(file, delimiter=',')
        for tokens in spamreader:
            if not did_skip_first_line:
                did_skip_first_line = True
                continue
            # print(tokens)
            row = [token.strip('"').strip().replace('\ufeff', '') for token in tokens]
            try:
                rows.append(Ynab(*row))
            except TypeError as e:
                print('Invalid row:', row)
                raise e
        row_by_account = {}
        for row in rows:
            if row.account not in row_by_account:
                row_by_account[row.account] = []
            row_by_account[row.account].append(row)
        return row_by_account
    
def build_monarch_csv_for_act(key, ynab_rows, output_dir):
    output_dir = output_dir.strip('/')
    with open(f'{output_dir}/monarch_{key}.csv', 'w', newline='') as file:
        for ynab_row in ynab_rows:
            monarch_row = ynab_row.to_monarch()
            csv_writer = csv.writer(file)
            csv_writer.writerow([
                monarch_row.date,
                monarch_row.merchant,
                monarch_row.category,
                monarch_row.account,
                monarch_row.original_statement,
                monarch_row.notes,
                monarch_row.amount
            ])
        print('Done writing csv for account:', key)

def build_monarch_csv(ynab_rows_by_account, output_dir):
    for key, ynab_rows in ynab_rows_by_account.items():
        build_monarch_csv_for_act(key, ynab_rows, output_dir)

def main():
    parser = argparse.ArgumentParser(
                    prog='Ynab to Monarch CSV Converter',
                    description='Converts YNAB CSV to Monarch CSV')
    parser.add_argument('--ynab_csv', help='Path to YNAB CSV file. Do NOT use the budget file. Use the transaction file. Monarch cannot handle the budget file.', required=True)
    parser.add_argument('--monarch_dir', default='.')
    args = parser.parse_args()
    ynab_rows = read_ynab_csv(args.ynab_csv)
    build_monarch_csv(ynab_rows, args.monarch_dir)
    
if __name__ == "__main__":
    main()