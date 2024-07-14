import sqlite3 as db
DATE_NOW = "2020-02-07"

class User:
    def __init__(self, username, password, access) -> None:
        self.username = username
        self.password = password
        self.access = access

class Admin(User):
    def __init__(self, username, password, access=True) -> None:
        User.__init__(self, username, password, access)

class Customer(User):
    def __init__(self, credits, username, password, access=False) -> None:
        User.__init__(self, username, password, access)
        self.credits = credits
        self.history = []

class Product:
    def __init__(self, id, name, price, stock) -> None:
        self.id = id
        self.name = name
        self.price = price
        self.stock = stock

class Order:
    def __init__(self, product, total_price, date) -> None:
        self.product = product
        self.total_price = total_price
        self.date = date

class DiscountCode:
    def __init__(self, code, expiry_date, discount_percentage, used) -> None:
        self.code = code
        self.expiry_date = expiry_date
        self.discount_percentage = discount_percentage
        self.used = used

    def is_expired(self):
        if self.expiry_date < DATE_NOW:
            return True
        return False
    

def initiate_tables(cursor):
        cursor.execute(''' CREATE TABLE users
            (username            TEXT  PRIMARY KEY NOT NULL,
            password        TEXT NOT NULL,
            access BOOLEAN NOT NULL);
            ''')

        cursor.execute(''' CREATE TABLE extrainfos
            (credits        INT    NOT NULL,
            username,
            FOREIGN KEY (username) REFERENCES users(username));
            ''')
        
        cursor.execute(''' CREATE TABLE products
            (id INT PRIMARY KEY     NOT NULL,
            name        TEXT    NOT NULL,
            price            INT    UNIQUE NOT NULL,
            stock       INT NOT NULL);
            ''')

        cursor.execute(''' CREATE TABLE discountcodes
            (code TEXT  UNIQUE NOT NULL,
            expiry_date  TEXT    NOT NULL,
            discount_percentage     INT   NOT NULL,
            used  BOOLEAN  DEFAULT 1
            );
            ''')

        cursor.execute(''' CREATE TABLE salehistory
            (
            product_id,
            total_price REAL NOT NULL,
            date        TEXT    NOT NULL,
            username,
            FOREIGN KEY (username) REFERENCES users(username));
            ''')

        print("all tables created successfully.")

class Database:
    def __init__(self, db_path="starstore.db") -> None:
        self.db_path = db_path
        try:
            self.connection = db.connect(self.db_path)
            self.cursor = self.connection.cursor()
        except db.Error as error:
            print('An error occurred: ', error)        

    def add_product(self, id, name, price, stock):
        sql = "INSERT INTO products (id, name, price, stock) VALUES (?, ?, ?, ?)"
        params = (id, name, price, stock)
        self.cursor.execute(sql, params)
        self.connection.commit()
        return True

    def add_user(self, username, password,  credits=0, is_admin=False):
        sql = "INSERT INTO users (username, password, access) VALUES (?, ?, ?)"
        params = (username, password, is_admin)
        self.cursor.execute(sql, params)
        self.connection.commit()

        if not is_admin:
            sql = "INSERT INTO extrainfos (credits, username) VALUES (?, ?)"
            params = (credits, username)
            self.cursor.execute(sql, params)
            self.connection.commit()
        return True

    def update_product(self, id, price, stock):
        update_statement = 'UPDATE products SET price=?, stock=? WHERE id=?'
        self.cursor.execute(update_statement, (price, stock, id))
        self.connection.commit()

    def change_password(self, username, new_password):
        update_statement = 'UPDATE users SET password=? WHERE username=?'
        self.cursor.execute(update_statement, (new_password, username))
        self.connection.commit()

    def get_user(self, username):
        self.cursor.execute('SELECT * FROM users WHERE "username" = ?', (username, ))
        user = self.cursor.fetchone()
        if user:
            if user[2] == 1:
                return Admin(user[0], user[1])
            
            self.cursor.execute('SELECT * FROM extrainfos WHERE "username" = ?', (username, ))
            credits = self.cursor.fetchone()[0]
            customer = Customer(credits, user[0], user[1])

            return customer 

        return None
    
    def get_history_of_orders(self, username):
        self.cursor.execute('SELECT * FROM salehistory WHERE "username" = ?', (username, ))
        history = self.cursor.fetchall()
        result = []
        for order in history:
            result.append(
                Order(self.get_product(order[0]), order[1], order[2])
            )
        return result

    def get_product(self, id):
        self.cursor.execute('SELECT * FROM products WHERE "id" = ?', (id, ))
        product = self.cursor.fetchone()
        
        if product:
            return Product(product[0], product[1], product[2], product[3])
        return None
    
    def get_all_products(self):
        self.cursor.execute('SELECT * FROM products')
        products = self.cursor.fetchall()
        
        all_products = []
        for p in products:
            all_products.append(
                Product(p[0], p[1], p[2], p[3])
            )

        return all_products

    def get_discount_code(self, code):
        self.cursor.execute('SELECT * FROM discountcodes WHERE "code" = ?', (code, ))
        code = self.cursor.fetchone()
        if code:
            return DiscountCode(code[0], code[1], code[2], code[3])
        else:
            return None

    def add_order(self, product_id, total_price, date, username):
        sql = "INSERT INTO salehistory (product_id, total_price, date, username) VALUES (?, ?, ?, ?)"
        params = (product_id, total_price, date, username)
        self.cursor.execute(sql, params)
        self.connection.commit()

        update_statement = 'UPDATE extrainfos SET credits=? WHERE username=?'
        old_credits = self.get_user(username).credits
        self.cursor.execute(update_statement, (old_credits - total_price, username))
        self.connection.commit()

        return True
        
    def add_descount_code(self, code, expiry_date, discount_percentage, used):
        sql = "INSERT INTO discountcodes (code, expiry_date, discount_percentage, used) VALUES (?, ?, ?, ?)"
        params = (code, expiry_date, discount_percentage, used)
        self.cursor.execute(sql, params)
        self.connection.commit()
        return True


##just first time run this to initiate tables
# import json

# database = Database()
# initiate_tables(database.cursor)
# import json
# with open('discount_codes.json') as file:
#     file_contents = file.read()
#     parsed_json = json.loads(file_contents)
#     for code in parsed_json:
#         try:
#             database.add_descount_code(code, parsed_json[code]["expiry_date"], parsed_json[code]["discount_percentage"], used=False)
#         except Exception as e:
#             print(e)