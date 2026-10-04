import sqlite3
from config import * 


def connect_db():
    """Create a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_PATH)
    return conn

def setup_database():
    """Create the database tables if they do not exist."""
    conn = connect_db()
    cur = conn.cursor()
    new_line = '\n'
    cur.execute('PRAGMA encoding="UTF-8";')
    conn.commit()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY,
            price_name TEXT,
            price_path TEXT,
            price_type TEXT,
            activity BOOLEAN
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS lists (
            id INTEGER PRIMARY KEY,
            price_id INTEGER,
            list_name TEXT,
            FOREIGN KEY (price_id) REFERENCES prices(id)
        )
    ''')
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY,
            price_id INTEGER,
            list_id INTEGER,
            {f',{new_line}'.join([column + " TEXT" for column in DEFAULT_COLUMNS_EN])},
            FOREIGN KEY (price_id) REFERENCES prices(id),
            FOREIGN KEY (list_id) REFERENCES lists(id)
        )
    ''')
    cur.execute(f'''
        CREATE TABLE IF NOT EXISTS my_data (
            id INTEGER PRIMARY KEY,
            {f',{new_line}'.join([column + " TEXT" for column in DEFAULT_COLUMNS_EN])}
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS fields (
            id INTEGER PRIMARY KEY,
            list_id INTEGER,
            file_field TEXT,
            final_column TEXT,
            additional_data TEXT,
            FOREIGN KEY (list_id) REFERENCES lists(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            list_id INTEGER,
            start_row INTEGER,
            end_row INTEGER,
            price_currency TEXT,
            rrc_currency TEXT,
            main_column TEXT,
            brand_name TEXT,
            price_id,
            FOREIGN KEY (list_id) REFERENCES lists(id)
            FOREIGN KEY (price_id) REFERENCES prices(id)
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS currency_rates (
            id INTEGER PRIMARY KEY,
            date TEXT,
            usd REAL,
            eur REAL,
            rub REAL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS currency_rates_settings (
            id INTEGER PRIMARY KEY,
            usd REAL,
            eur REAL,
            rub REAL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS connections (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            connected_product_id INTEGER,
            FOREIGN KEY (product_id) REFERENCES my_data(id),
            FOREIGN KEY (connected_product_id) REFERENCES data(id)
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS estimates (
            id INTEGER PRIMARY KEY,
            min_price REAL,
            max_price REAL,
            min_percentage REAL,
            no_competitor_percentage REAL
        );
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS compared_products (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            final_price REAL,
            minimal_price REAL, 
            result TEXT,
            FOREIGN KEY (product_id) REFERENCES my_data(id)
        );
    ''')
    
    # Парсеры
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scrapers (
            id INTEGER PRIMARY KEY,
            name TEXT,
            directory TEXT,
            activity BOOLEAN
        )
    ''')
    
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scraper_links (
            id INTEGER PRIMARY KEY,
            links TEXT,
            scraper_id INTEGER,
            FOREIGN KEY (scraper_id) REFERENCES scrapers(id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS scraper_settings (
            id INTEGER PRIMARY KEY,
            field TEXT,
            left_bound TEXT,
            right_bound TEXT,
            only_numbers BOOLEAN,
            default_value TEXT,
            links TEXT,
            scraper_id INTEGER,
            FOREIGN KEY (scraper_id) REFERENCES scrapers(id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            activity BOOLEAN,
            name TEXT,
            type Text, 
            last_time_run TEXT, 
            status TEXT
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ftp_settings (
            id INTEGER PRIMARY KEY,
            run_type TEXT,
            run_time TEXT,
            protocol TEXT,
            server_ip TEXT,
            login TEXT,
            password TEXT,
            port TEXT,
            operation TEXT,
            file_path TEXT,
            folder_path_server TEXT,
            task_id INTEGER,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    ''')
    
    # Экспорт
    cur.execute('''
        CREATE TABLE IF NOT EXISTS exports (
            id INTEGER PRIMARY KEY,
            name TEXT,
            fields TEXT,
            filters TEXT
        )
    ''')
    
    cur.execute('INSERT INTO currency_rates_settings (usd, eur, rub) VALUES (0, 0, 0)')
        
    conn.commit()
    conn.close()
    
def update_task_activity(id, value):
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET activity=? WHERE id=?", (value, id))
    conn.commit()
    conn.close()
    
def fetch_tasks():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks')
    data = cur.fetchall()
    conn.close()
    return data

def delete_task(id):
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id=?", (id, ))
    cur.execute('UPDATE tasks SET id = id - 1 WHERE id > ?', (id,))
    conn.commit()
    conn.close()

def add_task(task_type, name):
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (type, name, activity) VALUES (?, ?, 1)", (task_type, name))
    conn.commit()
    conn.close()

def update_task(id, task_type, name):
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("UPDATE tasks SET type=?, name=? WHERE id=?", (task_type, name, id))
    conn.commit()
    conn.close()

def get_scraper_links(scraper_id):
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM scraper_links WHERE scraper_id=?', (scraper_id, ))
    data = cur.fetchone()
    conn.close()
    return data

def update_scraper_links(scraper_id, links):
    """Update an scraper price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE scraper_links SET links=? WHERE scraper_id=?', (links, scraper_id))
    conn.commit()
    conn.close()
    
def add_scraper_links(scraper_id, links):
    """Add a new scraper to the database."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO scraper_links (links, scraper_id) VALUES (?, ?)", (links, scraper_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении парсера: {e}")
    finally:
        conn.close()
    
def fetch_compared_products():
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM compared_products')
    data = cur.fetchall()
    conn.close()
    return data

def fetch_connections():
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM connections')
    data = cur.fetchall()
    conn.close()
    return data

# Парсеры
def add_scraper(name, directory, activity=True):
    """Add a new scraper to the database."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO scrapers (name, directory, activity) VALUES (?, ?, ?)", (name, directory, activity))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении парсера: {e}")
    finally:
        conn.close()
        
    add_scraper_links(len(fetch_scrapers()), "")

def update_scraper(id, name, directory):
    """Update an scraper price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE scrapers SET name=?, directory=? WHERE id=?', (name, directory, id))
    conn.commit()
    conn.close()


def fetch_scrapers():
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM scrapers')
    scrapers = cur.fetchall()
    conn.close()
    return scrapers

def get_scraper(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scrapers WHERE id=?", (id, ))
    price = cur.fetchall()[0]
    conn.close()
    
    return price

def delete_scraper(id):
    """Update an scraper price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM scrapers WHERE id=?', (id, ))
    cur.execute('UPDATE scrapers SET id = id - 1 WHERE id > ?', (id,))
    cur.execute('DELETE FROM scraper_settings WHERE scraper_id=?', (id, ))
    cur.execute('DELETE FROM scraper_links WHERE scraper_id=?', (id, ))
    conn.commit()
    conn.close()
    
def update_scraper_activity(id, activity):
    """Update an scraper price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE scrapers SET activity=? WHERE id=?', (activity, id))
    conn.commit()
    conn.close()
    
def add_scraper_settings(scraper_id, field, left_bound, right_bound, only_numbers, default_value, links):
    """Add a new scraper to the database."""
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO scraper_settings (field, left_bound, right_bound, only_numbers, default_value, links, scraper_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (field, left_bound, right_bound, only_numbers, default_value, links, scraper_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при добавлении парсера: {e}")
    finally:
        conn.close()
        
def get_original_scraper_settings_id(id, scraper_id):
    print(id, scraper_id)
    fields = fetch_scraper_settings(scraper_id)
    #print(lists, list_id, price_id)
    id = fields[id-1][0]
    
    return id
        
def update_scraper_settings_column(id, scraper_id, column_name, value):
    id = get_original_scraper_settings_id(id, scraper_id)
    """Update an scraper price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE scraper_settings SET {column_name}=? WHERE id=?', (value, id))
    conn.commit()
    conn.close()
    
def update_scraper_settings_links(id, links, scraper_id):
    id = get_original_scraper_settings_id(id, scraper_id)
    """Update an scraper price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE scraper_settings SET links=? WHERE id=?', (links, id))
    conn.commit()
    conn.close()

def fetch_scraper_settings(scraper_id):
    """Fetch all scrapers from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM scraper_settings WHERE scraper_id=?', (scraper_id, ))
    scraper_settings = cur.fetchall()
    conn.close()
    return scraper_settings

def get_scraper_settings(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM scraper_settings WHERE id=?", (id, ))
    price = cur.fetchall()[0]
    conn.close()
    
    return price

def delete_scraper_settings(id, scraper_id):
    id = get_original_scraper_settings_id(id, scraper_id)
    """Update an scraper price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM scraper_settings WHERE id=?', (id, ))
    cur.execute('UPDATE scraper_settings SET id = id - 1 WHERE id > ?', (id,))
    conn.commit()
    conn.close()

def fetch_compared_products():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM compared_products')
    data = cur.fetchall()
    conn.close()
    
    return data

def add_compared_products(product_id, result):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO compared_products (product_id, result) VALUES (?, ?)', (product_id, result))
    conn.commit()
    conn.close()

def update_compared_products(id, product_id, result):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE compared_products SET product_id=?, result=? WHERE id=?', (product_id, result, id))
    conn.commit()
    conn.close()

def delete_compared_products(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM compared_products WHERE id=?', (id, ))
    cur.execute('UPDATE compared_products SET id = id - 1 WHERE id > ?', (id,))
    conn.commit()
    conn.close()

def fetch_estimates():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM estimates')
    data = cur.fetchall()
    conn.close()
    
    return data

def add_estimates(min_price, max_price, min_percentage, no_competitor_percentage):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO estimates (min_price, max_price, min_percentage, no_competitor_percentage) VALUES (?, ?, ?, ?)', (min_price, max_price, min_percentage, no_competitor_percentage))
    conn.commit()
    conn.close()

def update_estimates(id, column_name, value):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE estimates SET {column_name}=? WHERE id=?', (value, id))
    conn.commit()
    conn.close()

def delete_estimates(id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'DELETE FROM estimates WHERE id=?', (id, ))
    cur.execute('UPDATE estimates SET id = id - 1 WHERE id > ?', (id,))
    conn.commit()
    conn.close()

def add_connection_db(product_id, connected_product_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO connections (product_id, connected_product_id) VALUES (?, ?)', (product_id, connected_product_id))
    conn.commit()
    conn.close()

def delete_connection_db(product_id, connected_product_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM connections WHERE product_id=? AND connected_product_id=?', (product_id, connected_product_id))
    conn.commit()
    conn.close()

def get_connections(product_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT connected_product_id FROM connections WHERE product_id=?', (product_id, ))
    data = cur.fetchall()
    conn.close()
    
    return data

def update_connection_db(product_id, connected_product_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE connections SET product_id=? WHERE connected_product_id=?', (product_id, connected_product_id))
    conn.commit()
    conn.close()

def get_all_connections():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT connected_product_id FROM connections')
    data = cur.fetchall()
    conn.close()
    
    return data

def get_full_connections():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT product_id FROM connections')
    data = cur.fetchall()
    conn.close()
    
    return data

def get_currency_settings():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'SELECT * FROM  currency_rates_settings WHERE id=1')
    data = cur.fetchone()
    conn.close()
    
    return data
    
def update_currency_settings(usd, eur, rub):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE currency_rates_settings SET usd=?, eur=?, rub=? WHERE id=1', (usd, eur, rub))
    conn.commit()
    conn.close()
    
def add_currencies(usd, eur, rub, date):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO currency_rates (date, usd, eur, rub) VALUES (?, ?, ?, ?)', (date, usd, eur, rub))
    conn.commit()
    conn.close()
    
def update_currencies(usd, eur, rub, date):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE currency_rates SET usd=?, eur=?, rub=? WHERE date=?', (usd, eur, rub, date))
    conn.commit()
    conn.close()
    
def get_currencies(date):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM currency_rates WHERE date=?', (date, ))
    currencies = cur.fetchone()
    conn.close()
    
    return currencies

# Прайсы
def update_price_activity(price_id, activity=False):
    """Add a new price to the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE prices SET activity=? WHERE id=?', (activity, price_id))
    conn.commit()
    conn.close()
    
def add_price(price_name, price_path, price_type):
    """Add a new price to the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO prices (price_name, price_path, price_type, activity) VALUES (?, ?, ?, False)', (price_name, price_path, price_type))
    conn.commit()
    conn.close()

def fetch_prices():
    """Fetch all prices from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM prices')
    prices = cur.fetchall()
    conn.close()
    return prices

def update_price(id, price_name, price_path, price_type):
    """Update an existing price in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE prices SET price_name=?, price_path=?, price_type=? WHERE id=?', (price_name, price_path, price_type, id))
    conn.commit()
    conn.close()

def delete_price(id):
    """Delete a price from the database."""
    conn = connect_db()
    cur = conn.cursor()
    try:
        # Delete the row with the specified primary key
        cur.execute('DELETE FROM prices WHERE id=?', (id,))
        
        # Update the primary key values for all rows following the deleted row
        cur.execute('UPDATE prices SET id = id - 1 WHERE id > ?', (id,))
        conn.commit()
            
        cur.execute('DELETE FROM fields WHERE price_id=?', (id, ))
        cur.execute('DELETE FROM lists WHERE price_id=?', (id, ))
        cur.execute('DELETE FROM settings WHERE price_id=?', (id, ))
        
        # Commit the changes
        conn.commit()
    except Exception as e:
        # Rollback the transaction if an error occurs
        conn.rollback()
        print("Error:", e)
    finally:
        # Close the connection
        conn.close()
        
# Листы прайсов
def get_original_list_id(list_id, price_id):
    lists = fetch_lists(price_id)
    #print(lists, list_id, price_id)
    list_id = lists[list_id-1][0]
    
    return list_id
        
def get_original_field_id(field_id, list_id, price_id):
    fields = fetch_fields(list_id, price_id)
    
    field_id = fields[field_id-1][0]
    
    return field_id

def fetch_lists(price_id):
    """Fetch all lists associated with a given price."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM lists WHERE price_id=?', (price_id,))
    lists = cur.fetchall()
    conn.close()
    return lists

def add_list(list_name, price_id):
    """Add a new list to a price."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO lists (list_name, price_id) VALUES (?, ?)', (list_name, price_id))
    conn.commit()
    cur.execute(f"SELECT COUNT(*) FROM lists")
    count = cur.fetchone()[0]  # Fetch the result of the query
    cur.execute('INSERT INTO settings (list_id, start_row, end_row, rrc_currency, price_currency, main_column, brand_name, price_id) VALUES (?, 0, Null, "BYN", "BYN", "None", Null, ?)', (count, price_id))
    conn.commit()
    conn.close()

def update_list(id, list_name, price_id):
    """Update an existing list."""
    id = get_original_list_id(id, price_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE lists SET list_name=? WHERE id=?', (list_name, id))
    conn.commit()
    conn.close()

def delete_list(id, price_id):
    """Delete a list from the database."""
    list_id = id
    id = get_original_list_id(id, price_id)
    conn = connect_db()
    cur = conn.cursor()
    try:
        # Delete the row with the specified primary key
        cur.execute('DELETE FROM lists WHERE id=?', (id,))
            
        cur.execute('DELETE FROM fields WHERE list_id=?', (list_id, ))
        
        cur.execute('DELETE FROM settings WHERE list_id=?', (list_id, ))
        
        # Commit the changes
        conn.commit()
    except Exception as e:
        # Rollback the transaction if an error occurs
        conn.rollback()
        print("Error:", e)
    finally:
        # Close the connection
        conn.close()


def fetch_fields(list_id, price_id):
    """Fetch all fields associated with a given list."""
    list_id = get_original_list_id(list_id, price_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM fields WHERE list_id=?', (list_id,))
    fields = cur.fetchall()
    conn.close()
    return fields

# Свойства листов парайсов
def add_field(list_id, file_field, final_column, additional_data, price_id):
    list_id = get_original_list_id(list_id, price_id)
    print(list_id, file_field, final_column, price_id)
    """Add a new field to a list."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO fields (list_id, file_field, final_column, additional_data) VALUES (?, ?, ?, ?)', (list_id, file_field, final_column, additional_data))
    conn.commit()
    conn.close()

def update_field(id, value, column_name, list_id, price_id):
    id = get_original_field_id(id, list_id, price_id)
    """Update an existing field."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE fields SET {column_name}=? WHERE id=?', (value, id))
    conn.commit()
    conn.close()

def delete_field(id, list_id, price_id):
    id = get_original_field_id(id, list_id, price_id)
    """Delete a field from the database."""
    conn = connect_db()
    cur = conn.cursor()
    try:
        # Delete the row with the specified primary key
        cur.execute('DELETE FROM fields WHERE id=?', (id,))
        
        # Update the primary key values for all rows following the deleted row
        cur.execute('UPDATE fields SET id = id - 1 WHERE id > ?', (id,))
        
        # Commit the changes
        conn.commit()
    except Exception as e:
        # Rollback the transaction if an error occurs
        conn.rollback()
        print("Error:", e)
    finally:
        # Close the connection
        conn.close()

def get_price(price_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM prices WHERE id=?", (price_id, ))
    price = cur.fetchall()[0]
    conn.close()
    
    return price

def get_list(list_id, price_id):
    list_id = get_original_list_id(list_id, price_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM lists WHERE id=?", (list_id, ))
    list = cur.fetchall()[0]
    conn.close()
    
    return list

def get_field(field_id, list_id, price_id):
    field_id = get_original_field_id(field_id, list_id, price_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM fields WHERE id=?", (field_id, ))
    field = cur.fetchall()[0]
    conn.close()
    
    return field

def update_settings(value, column_name, list_id, price_id):
    print('se')
    list_id = get_original_list_id(list_id, price_id)
    print(list_id, value, column_name)
    """Update an existing settings."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(f'UPDATE settings SET {column_name}=? WHERE list_id=?', (value, list_id))
    conn.commit()
    conn.close()

def get_settings(list_id, price_id):
    list_id = get_original_list_id(list_id, price_id)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM settings WHERE list_id=?", (list_id, ))
    settings = cur.fetchall()
    settings = [i if i!=None else '' for i in settings[0]]
    conn.close()
    
    return settings

def select_data(prompt):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(prompt)
    data = cur.fetchall()
    conn.close()
    
    return data

def upload_data(df):
    conn = connect_db()
    df['id'] = range(1, len(df) + 1)
    cols = list(df.columns)
    cols.insert(0, cols.pop(cols.index('id')))
    df = df[cols]
    df.to_sql('data', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

def upload_my_data(df):
    conn = connect_db()
    df['id'] = range(1, len(df) + 1)
    cols = list(df.columns)
    cols.insert(0, cols.pop(cols.index('id')))
    df = df[cols]
    df.to_sql('my_data', conn, if_exists='replace', index=False)
    conn.commit()
    conn.close()

def get_all_my_data():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM my_data")
    data = cur.fetchall()
    conn.close()
    
    return data

def get_all_data():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM data")
    data = cur.fetchall()
    conn.close()
    
    return data
    
def set_currency():
    pass
    
def get_currency():
    pass


# Экспорт
def add_export(name, fields, filters):
    """Add a new export setting to the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('INSERT INTO exports (name, fields, filters) VALUES (?, ?, ?)',
                (name, fields, filters))
    conn.commit()
    conn.close()

def update_export(export_id, name, fields, filters):
    """Update an existing export setting in the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE exports SET name = ?, fields = ?, filters = ? WHERE id = ?',
                (name, fields, filters, export_id))
    conn.commit()
    conn.close()

def delete_export(export_id):
    """Delete an export setting from the database."""
    print(f"Trying to delete export with ID: {export_id}")
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('DELETE FROM exports WHERE id = ?', (export_id,))
    conn.commit()
    conn.close()

def fetch_exports():
    """Fetch all export settings from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, name, fields, filters FROM exports')
    results = cur.fetchall()
    conn.close()
    return results

def fetch_export_by_id(export_id):
    """Fetch a single export setting by its ID from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('SELECT id, name, fields, filters FROM exports WHERE id = ?', (export_id,))
    result = cur.fetchone()
    conn.close()
    return result if result else None

def update_export_name(export_id, new_name):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('UPDATE exports SET name = ? WHERE id = ?', (new_name, export_id))
    conn.commit()
    conn.close()

def fetch_column_names_from_my_data():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(my_data)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    conn.close()
    return column_names
       
setup_database()