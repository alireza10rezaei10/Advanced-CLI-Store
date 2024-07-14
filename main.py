from database import Database

DATE_NOW = "2020-02-07"
DEFAULT_CREDITS = 1500

class Session:
    def __init__(self) -> None:
        self.user = None
session = Session()

database = Database()

# helper functions ------------------------------
def authenicate(username, password, is_admin=False):
    user = database.get_user(username)
    if user:
        if user.password == password:
            if (user.access and is_admin) or (not user.access and not is_admin):   
                return user
    return None

def is_product_id_exists(product_id):    
    return database.get_product(product_id)
    
def add_product(id, name, price, stock):
    return database.add_product(id, name, price, stock)

def change_stock(product_id, new_stock):
    product = database.get_product(product_id)
    database.update_product(product_id, product.price, new_stock)
    return True

def change_price(product_id, new_price):
    product = database.get_product(product_id)
    database.update_product(product_id, new_price, product.stock)
    return True

def is_password_strong(password):
    if len(password)<8:
        return (False, "short password...")
    return True

def change_password(username, new_password):
    database.change_password(username, new_password)
    return True

def is_username_available(username):
    return not database.get_user(username)

def signup_user(username, password):
    return database.add_user(username, password, DEFAULT_CREDITS)

def products_list():
    return database.get_all_products()

def is_product_in_stock(product_id):
    return database.get_product(product_id)

def discount_code_status(code):
    code =  database.get_discount_code(code)
    if code:
        if code.used or code.is_expired():
            print("not a valid code.")
            return 0
        else:
            return code.discount_percentage

    print("not a valid code.")
    return 0

def new_order(product_id, ordered_count, total_price, username, date):
    database.add_order(product_id, total_price, date, username)
    
    product = database.get_product(product_id)
    database.update_product(product_id, product.price, product.stock-ordered_count)
    return True


# pages ----------------------
def start():
    print("in each step you can enter 'back' command to back to the previous page.")    
    command = input("are you an admin or a customer? [1 for admin 2 for customer]\n")

    if command == "1":
        login_page(is_admin=True)
    elif command == "2":
        customer_first_page()
    else:
        print("wrong command please just enter 1 or 2...")
        start()

def login_page(is_admin):
    command = input("username: ")
    if command == "back":
        start()
        return None
    username = command
    
    command = input("password: ")
    if command == "back":
        start()
        return None
    password = command

    user = authenicate(username, password, is_admin)
    if user:
        print("you logged in successfully.")
        session.user = user
        if is_admin:
            admin_menu_page()
        else:
            customer_menu_page()
    else:
        print("wrong username or password... try again")
        login_page(is_admin)
        return None

def signup_page():
    command = input("username: ")
    if command == "back":
        start()
        return None
    username = command

    if is_username_available(username):
        while True:
            command = input("password: ")
            if command == "back":
                start()
                return None
            password = command
            
            if is_password_strong(password):
                status = signup_user(username, password)
                if status == True:
                    print("done successfully.")
                    customer_first_page()
                else:
                    print("an error occured... please try again.")
                    signup_page()
                return None
            else:
                print("password is weak... it has to contain 8 charactor and...")    
    
    else:
        print("username is not available... try again.")
        signup_page()
        return None

def admin_menu_page():
    command = input("1: add product \n2: change stock \n3: change price \n4: change password \n")
    if command == "back":
        login_page(is_admin=True)
        return None

    if command == "1":
        add_product_page()
    elif command == "2":
        change_stock_page()
    elif command == "3":
        change_price_page()
    elif command == "4":
        change_password_page(is_admin=True)
    else:
        print("wrong command... try again.")
        admin_menu_page()

def add_product_page():
    command = input("enter the product id: ")
    if command == "back":
        admin_menu_page()
        return None
    product_id = command

    if not is_product_id_exists(product_id):
        command = input("product name: ")
        if command == "back":
            admin_menu_page()
            return None
        name = command

        command = input("product price: ")
        if command == "back":
            admin_menu_page()
            return None
        price = command

        command = input("product stock: ")
        if command == "back":
            admin_menu_page()
            return None
        stock = command

        status = add_product(product_id, name, price, stock)
        if status == True:
            print("product added successfully.")
            print("add new product or 'back' to back to the admin dashboard.")
            add_product_page()
            return None
        else:
            print("an error occurred... please try again.")
            add_product_page()
            return None

    else:
        print("we have this product already... please try again.")
        add_product_page()

def change_stock_page():
    command = input("enter the product id: ")
    if command == "back":
        admin_menu_page()
        return None
    product_id = int(command)

    if is_product_id_exists(product_id):
        command = input("new stock: ")
        if command == "back":
            admin_menu_page()
            return None
        new_stock = int(command)

        status = change_stock(product_id, new_stock)
        if status == True:
            print("done successfully.")
            print("change another product stock or 'back' to back to the admin dashboard.")
            change_stock_page()
        else:
            print("an error occured... please try again.")
            change_stock_page()

    else:
        print("wrong product id... please try again.")
        change_stock_page()

def change_price_page():
    command = input("enter the product id: ")
    if command == "back":
        admin_menu_page()
        return None
    product_id = command

    if is_product_id_exists(product_id):
        command = input("new price: ")
        if command == "back":
            admin_menu_page()
            return None
        new_price = int(command)

        status = change_price(product_id, new_price)
        if status == True:
            print("done successfully.")
            print("change another product price or 'back' to back to the admin dashboard.")
            change_price_page()
        else:
            print("an error occured... please try again.")
            change_price_page()

    else:
        print("wrong product id... please try again.")
        change_price_page()

def change_password_page(is_admin):
    command = input("enter new password: ")    
    if command == "back":
        if is_admin:
            admin_menu_page()
        else:
            customer_menu_page()
        return None
    new_password = command

    if is_password_strong(new_password):
        status = change_password(session.user.username, new_password)
        if status == True:
            print("done successfully.")
            if is_admin:
                admin_menu_page()
            else:
                customer_menu_page()
                return None
        else:
            print("an error occured... please try again.")
            change_password_page(is_admin)

    else:
        print("password is weak... it has to contain 8 charactor and...")
        change_password_page(is_admin)

def customer_first_page():
    command = input("1: login \n2: signup \n")
    if command == "back":
        start()
        return None

    if command == "1":
        login_page(is_admin=False)
    elif command == "2":
        signup_page()
    else:
        print("wrong command... try again.")
        customer_first_page()    

def customer_menu_page():
    print(f"you have {database.get_user(session.user.username).credits} credits left.")

    command = input("1: new order \n2: history of orders \n3: change password \n")
    if command == "back":
        login_page(is_admin=False)
        return None

    if command == "1":
        new_order_page()
    elif command == "2":
        history_of_orders_page()
    elif command == "3":
        change_password_page(is_admin=False)
    else:
        print("wrong command... try again.")
        admin_menu_page()

def new_order_page():
    print("all products id: ")
    for product in products_list():
        print(f"product id: {product.id} | price : {product.price} | stock: {product.stock}")

    command = input("product id: ")
    if command == "back":
        customer_menu_page()
        return None
    product_id = command

    if is_product_id_exists(product_id):
        while True:
            product = is_product_in_stock(product_id)
            if product.stock > 0:
                command = input("count: ")
                if command == "back":
                    customer_menu_page()
                    return None
                ordered_count = int(command)
                if ordered_count <= product.stock:
                    command = input("do you have discount code? [y or n]\n")
                    discount = 0
                    if command == "back":
                        customer_menu_page()
                        return None
                    if command == "y":
                        command = input("discount code: ")
                        if command == "back":
                            customer_menu_page()
                            return None
                        discount = discount_code_status(command)
                    total_price = product.price*ordered_count*(100-discount)/100
                    print(f"total cost is: {total_price}")
                    command = input("do you want to pay with your credits? [y or n]\n")
                    if command == "back":
                        customer_menu_page()
                        return None    
                    if command == "y":
                        status = new_order(product_id, ordered_count, total_price, session.user.username, DATE_NOW)
                        if status == True:
                            print("your order registered successfully.")
                            print("do you have new order?")
                            new_order_page()
                            return None
                        else:
                            print("some thing went wrong... order didn't register.")
                    else:
                        new_order_page()
                        return None

                else:
                    print("there are limited counts of this product...")
                    print(f"you can choose up to {product.stock} instances of this product.")
            else:
                print("sorry all instances of this product are sold out... please choose another one.")
                new_order_page()
                return None

    else:
        print("wrong product id... try again.")
        new_order_page()

def history_of_orders_page():
    for order in database.get_history_of_orders(session.user.username):
        print(f"product: {order.product.id}")
        print(f"total price: {order.total_price}")
        print(f"date: {order.date}")
        print("-----------")
    if not database.get_history_of_orders(session.user.username):
        print("there were no orders...")
    customer_menu_page()


start()