import sqlite3 as sql

# Database and Table Initialization
def create_tables():
    tables = {
        "Users": '''
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''',
        "Purchases": '''
            CREATE TABLE IF NOT EXISTS Purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                total_amount FLOAT NOT NULL,
                paid_amount FLOAT NOT NULL,
                balance FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES Users (id)
            )
        ''',
        "PurchaseDetails": '''
            CREATE TABLE IF NOT EXISTS PurchaseDetails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                sub_total REAL NOT NULL,
                FOREIGN KEY (purchase_id) REFERENCES Purchases (id),
                FOREIGN KEY (product_id) REFERENCES Products (id)
            )
        ''',
        "Denominations": '''
            CREATE TABLE IF NOT EXISTS Denominations (
                value INTEGER PRIMARY KEY,
                count INTEGER NOT NULL
            )
        ''',
        "Products": '''
            CREATE TABLE IF NOT EXISTS Products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                available_stocks INTEGER NOT NULL,
                price_per_unit REAL NOT NULL,
                tax_percentage REAL NOT NULL
            )
        '''
    }

    # Establish connection to the SQLite database
    try:
        conn = sql.connect("test.db")
        print("Database connected successfully.")
        cursor = conn.cursor()

        # Create tables
        for table_name, create_statement in tables.items():
            try:
                cursor.execute(create_statement)
                print(f"{table_name} table created successfully.")
            except sql.Error as e:
                print(f"Exception occurred while creating {table_name} table: {e}")

        print("All tables processed successfully.")
    except sql.Error as e:
        print(f"Database connection error: {e}")
    finally:
        conn.commit()
        conn.close()
        print("Database connection closed.")

if __name__ == "__main__":
    create_tables()
