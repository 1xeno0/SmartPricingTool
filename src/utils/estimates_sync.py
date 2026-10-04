import sqlite3
import pandas as pd

from config import *
from src.database.database import *


# Sync prices Function
def sync_prices():
    conn = connect_db()
    cur = conn.cursor()
    
    prices = pd.DataFrame(fetch_prices(), columns=['id', 'price_name', 'price_path', 'price_type', 'activity'])
    connections = pd.DataFrame(fetch_connections(), columns=['id', 'product_id', 'connected_product_id'])
    estimates = fetch_estimates()
    
    my_data = pd.DataFrame(get_all_my_data(), columns=['id']+DEFAULT_COLUMNS_EN)
    data = pd.DataFrame(get_all_data(), columns=['id', 'price_id', 'list_id']+DEFAULT_COLUMNS_EN)
    
    cur.execute("DELETE FROM compared_products")
    conn.commit()
    
    all_connected_products = connections['product_id'].unique().tolist()
    
    for product_id in all_connected_products:
        all_connected_ids = connections.loc[connections['product_id'] == product_id]
        
        all_supplier_prices = []
        all_competitor_prices = []
        
        print(all_connected_ids['connected_product_id'])
        for connected_product_id in all_connected_ids['connected_product_id']:
            product = data[data['id'] == connected_product_id].values[0]
            price = prices[prices['id'] == product[1]].values[0]
            
            if not price[-1] or not product[5]:
                continue
            
            print(product, price)
            if price[3]=="Конкурент":
                all_competitor_prices.append(float(product[5]))
            else:
                all_supplier_prices.append(float(product[5]))
        
        if all_supplier_prices:    
            min_supplier_price = sorted(all_supplier_prices)[0]
            
            for estimate in estimates:
                if estimate[1] and min_supplier_price<estimate[1]:
                    continue
                if estimate[2] and min_supplier_price>estimate[2]:
                    continue
                
                if not all_competitor_prices:
                    minimal_price = min_supplier_price*(1+(estimate[4]/100))
                    final_price = minimal_price
                    result = '-'
                    continue
                
                minimal_price = min_supplier_price*(1+(estimate[3]/100))
                sorted_comptetitor_prices = sorted(all_competitor_prices)[::-1]
                print(sorted_comptetitor_prices)
                
                for min_competitor_price in sorted_comptetitor_prices:
                    if min_supplier_price <= min_competitor_price:
                        final_price = min_competitor_price
                        result = '='
                    elif min_supplier_price >= min_competitor_price:
                        final_price = minimal_price
                        result = '<'
                    
                # Insert or update final price in a new or existing table for final prices
                # Assuming you have a table called final_prices to store these results
                cur.execute('INSERT INTO compared_products (product_id, final_price, minimal_price, result) VALUES (?, ?, ?, ?)', (product_id, round(final_price, 2), round(minimal_price, 2), result))
                
                conn.commit()
                
                break
        # Close the connection
    conn.close()


# Run the sync process
if __name__ == '__main__':
    sync_prices()

