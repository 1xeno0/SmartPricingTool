from src.database.database import *
import pandas as pd

from config import *
import chardet
import itertools
from pprint import pprint


def create_alphabet_labels(n):
    """Generate a list of column names based on the alphabet for n columns."""
    labels = []
    length = 1
    while len(labels) < n:
        # Generate labels of the current length using itertools.product
        possible_combinations = [''.join(combination) for combination in itertools.product(string.ascii_uppercase, repeat=length)]
        labels.extend(possible_combinations)
        length += 1
    return labels[:n]    

def sync_prices():
    all_prices = fetch_prices()

    data_df = pd.DataFrame([i[1:] for i in get_all_data()], columns=['price_id', 'list_id']+DEFAULT_COLUMNS_EN)
    data_df_list = data_df.values.tolist()
    new_elements = pd.DataFrame(columns=['price_id', 'list_id']+DEFAULT_COLUMNS_EN)
    all_new_rows = []
                
    name_index = DEFAULT_COLUMNS_EN.index("NAME")
    sku_index = DEFAULT_COLUMNS_EN.index("SKU")

    for price_id, price_name, price_path, price_type, activity in all_prices:
        for list_id, price_id, list_name in fetch_lists(price_id):
            final_df = pd.DataFrame([], columns=['price_id', 'list_id']+DEFAULT_COLUMNS_EN)

            settings = select_data(f"SELECT * FROM settings WHERE list_id={list_id}")[0]
            fields = select_data(f"SELECT * FROM fields WHERE list_id={list_id}")
            settings = [element if element is not None else '' for element in settings]
            fields = [[element if element is not None else '' for element in inner_list] for inner_list in fields]

            # Read the file as binary
            with open(price_path, 'rb') as file:
                raw_data = file.read()

            # Detect encoding
            encoding = chardet.detect(raw_data)['encoding']

            if price_path.rsplit('.',1)[1] in ['xls','xlsx']:
                if settings[1] or settings[1] == 0:
                    start_row = settings[1]
                if settings[2]:
                    end_row = settings[2]
                    df = pd.read_excel(price_path, engine='openpyxl', skiprows=lambda x: x < start_row, nrows=end_row - start_row)
                else:
                    df = pd.read_excel(price_path, engine='openpyxl', skiprows=lambda x: x < start_row)
            else:
                if settings[1] or settings[1] == 0:
                    start_row = settings[1]
                if settings[2]:
                    end_row = settings[2]
                    df = pd.read_csv(price_path, delimiter=';', encoding=encoding, skiprows=lambda x: x < start_row, nrows=end_row - start_row)
                else:
                    df = pd.read_csv(price_path, delimiter=';', encoding=encoding, skiprows=lambda x: x < start_row)

            new_labels = create_alphabet_labels(len(df.columns))
            df.columns = new_labels

            if settings[2]:
                df = df[settings[1]:settings[2]]
            else:
                df = df[settings[1]:]

            for field in fields:
                if not field[3] or not field[2]:
                    continue
                if field[-1]:
                    final_df[field[3]] = field[-1]
                    continue
                if '+' in field[2]:
                    final_df[field[3]] = df.apply(lambda row: ' '.join(row[col] for col in [i for i in field[2].split('+') if '"' not in i]), axis=1)
                    
                    for i in field[2].split('+'):
                        if '"' in i:
                            i = i.replace('"', '')
                            final_df[field[3]] = final_df[field[3]].astype(str) + " " + i
                else:
                    final_df[field[3]] = df[field[2]]
        
            if not activity:
                final_df['BUY PRICE'] = 0
                final_df['AVAILABILTY'] = 0
                
            print(price_type, DEFAULT_PRICES[0])
            if price_type == DEFAULT_PRICES[0]:
                final_df.drop("price_id", axis=1, inplace=True)
                final_df.drop("list_id", axis=1, inplace=True)
                upload_my_data(final_df)
            else:
                final_df['price_id'] = price_id 
                final_df['list_id'] = list_id
                
                final_df_list = final_df.values.tolist()
                
                new_rows = []
                
                for index, line in enumerate(final_df_list):
                    f = False
                    for indexD, lineD in enumerate(data_df_list):
                        if line[name_index+2]==lineD[name_index+2] or line[sku_index+2]==lineD[sku_index+2]:
                            data_df_list[indexD] = line
                            f = True
                            break
                    if not f:
                        new_rows.append(line)
                        
                all_new_rows+=new_rows

    data_df_list+=all_new_rows
    data_df = pd.DataFrame(data_df_list, columns=['price_id', 'list_id']+DEFAULT_COLUMNS_EN)
    
    upload_data(data_df)
    return True


if __name__ == '__main__':
    sync_prices()
            