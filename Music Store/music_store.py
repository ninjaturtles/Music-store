import mysql.connector

#Global variable
user_name = "" 

# Establish db connection
db = mysql.connector.connect(user='root', password='jk123456', 
                    host='localhost', database='notown')
cursor = db.cursor()
print("Connecting to Database...")


# stmt = "DROP TABLE IF EXISTS purchase"
# cursor.execute(stmt)
# stmt = "DROP TABLE IF EXISTS credit_cards"
# cursor.execute(stmt)
# stmt = "DROP TABLE IF EXISTS registered_customer"
# cursor.execute(stmt)

""" -----------------------------------------
create tables if DNE
------------------------------------------"""
stmt = "SHOW TABLES LIKE 'registered_customer'"
cursor.execute(stmt)
rows = cursor.fetchall()
if len(rows) == 0:      # create new table
    stmt = """CREATE TABLE registered_customer(
            user_name VARCHAR(30),
            password VARCHAR(30),
            address VARCHAR(50),
            phone_number VARCHAR(10),
            PRIMARY KEY (user_name));"""
    cursor.execute(stmt)

stmt = "SHOW TABLES LIKE 'credit_cards'"
cursor.execute(stmt)
rows = cursor.fetchall()
if len(rows) == 0:      # create new table
    stmt = """CREATE TABLE credit_cards(
            user_name VARCHAR(30),
            credit_number VARCHAR(20) NOT NULL,
            FOREIGN KEY (user_name) REFERENCES registered_customer(user_name));"""
    cursor.execute(stmt)

stmt = "SHOW TABLES LIKE 'purchase'"
cursor.execute(stmt)
rows = cursor.fetchall()
if len(rows) == 0:      # create new table
    stmt = """CREATE TABLE purchase(
            user_name VARCHAR(30),
            album_id INTEGER,
            album_name VARCHAR(30),
            price NUMERIC(5,2),
            credit_number VARCHAR(20) NOT NULL,
            FOREIGN KEY (user_name) REFERENCES registered_customer(user_name));"""
    cursor.execute(stmt)

#search by musician name, returns None if not found
def search_musician(musician_name):
    stmt = """SELECT DISTINCT A.album_id, A.album_title,A.price FROM 
            musicians As M JOIN perform As P JOIN albums As A
            ON M.sin = P.musician_id AND A.album_id = P.album_id
            WHERE name = '{}';""".format(musician_name)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return rows
    else:
        return None

# search by album title, returns None if not found
def search_album(album_title):
    stmt = """SELECT album_id, album_title, price FROM albums WHERE album_title = '{}';""".format(album_title)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return rows
    else:
        return None
    
# search by song title, returns None if not found
def search_song(song_title):
    stmt = """SELECT album_id,album_title,price FROM (songs NATURAL JOIN albums)
             WHERE song_title = '{}';""".format(song_title)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return rows
    else:
        return None

# search by producer name, returns None if not found
def search_producer(producer_name):
    stmt = """SELECT A.album_id, A.album_title, A.price
                FROM notown.musicians AS M JOIN notown.albums AS A
                ON sin = producer_id WHERE name = '{}';""".format(producer_name)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return rows
    else:
        return None

# verifies if username already exists
def user_exists(name, cc):
    stmt = """SELECT * FROM registered_customer WHERE user_name = '{}';""".format(name)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    if len(rows) > 0:
        return True
    else:
        return False

# verifies log on info, returns 1 if ok, -1 if password incorrect, 0 if username not found 
def check_log_on(uName, pw):
    stmt = """SELECT * FROM registered_customer WHERE user_name = '{}';""".format(uName)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    if len(rows) == 0:
        return 0    # username not found
    elif rows[0][1] == pw:
        return 1    # ok
    else:
        return -1   # incorrect password
    
# registers new customer, returns 1 if ok, 0 otherwise
def register(user_name, password, address, phone_num, credit):
    valid = user_exists(user_name, credit)
    if not valid:
        stmt = """INSERT INTO registered_customer (user_name, password, address, phone_number) VALUES 
        ('{}','{}','{}','{}');""".format(user_name, password, address, phone_num)
        cursor.execute(stmt)
        db.commit()
        stmt = """INSERT INTO credit_cards (user_name, credit_number) VALUES ('{}','{}');""".format(user_name,credit)
        cursor.execute(stmt)
        db.commit()
        return 1
    else:
        return 0

# adds new credit card to credit cards table
def add_new_cc(uName,card):
    stmt = """SELECT * FROM credit_cards WHERE user_name = '{}';""".format(uName)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    for row in rows:
        if row[1] == card:
            return 0    #already exists
        else:
            stmt = """INSERT INTO credit_cards (user_name, credit_number) VALUES ('{}','{}');""".format(uName, card)
            cursor.execute(stmt)
            db.commit()
            return 1        #new credit added
        
# inserts content of shopping basket into purchase table
def checkout(user_name,basket,credit):
    for item in basket:
        stmt = """INSERT INTO purchase (user_name,album_id,album_name,price,credit_number) VALUES 
        ('{}','{}','{}','{}','{}');""".format(user_name, item[0], item[1], item[2],credit)
        cursor.execute(stmt)
        db.commit()
    return

# displays retrieved albums
def display_album(rows):
    print()
    i = 1
    print("{:<3s}{:^15s} {:>10s}".format("#","Album Name","Price($)"))
    print("-------------------------------")
    for row in rows:
        print("{:<3d}{:^15s}{:>10,.2f}".format(i,row[1],float(row[2])))
        i+=1
    print()

# displays costumer's credit cards
def display_credit_cards(rows):
    i = 1
    print("{:<3s}{:<16s}".format("#","Credit Card"))
    print("-------------------------------")
    for _ in rows:
        print("{:<3d}{:<16s}".format(i,rows[i-1][0]))
        i+=1
    print()

# displays costumer's credit cards
def display_purchases(rows):
    i = 1
    print("{:<3s}{:^15s}{:>12s}{:^20s}".format("#","Album Name","Price($)","Credit Card"))
    print("-------------------------------------------------")
    for _ in rows:
        print("{:<3d}{:^15s}{:>10,.2f}{:>20s}".format(i,rows[i-1][0],rows[i-1][1],rows[i-1][2]))
        i+=1
    print()
    
# get costumer's credit card from credit cards table
def get_credit_cards(user_name):
    stmt = """SELECT credit_number FROM credit_cards WHERE user_name = '{}';""".format(user_name)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    return rows

# get costumer's credit card from credit cards table
def get_purcahse_history(user_name):
    stmt = """SELECT album_name, price, credit_number FROM notown.purchase 
            WHERE user_name = '{}';""".format(user_name)
    cursor.execute(stmt)
    rows = cursor.fetchall()
    return rows

# retrieve all records in a table  
def retrieve_all(table_name):
        stmt = "SELECT * from {}".format(table_name)
        cursor.execute(stmt)
        rows = cursor.fetchall()
        rows.sort()
        return rows
    

# print retrieved data
def print_table(rows):
    if len(rows) == 0:
        print("Table is Empty!")
    else:
        for row in rows:
            print(row)
            
"""-------------------------
 testing
-------------------------- """
def add_cus():
    file = open("cus.txt","r")
    line = file.readline().strip()
    while line != "":
        temp = line.split(",")
        register(temp[0],temp[1],temp[2],temp[3],temp[4])
        line = file.readline().strip()
    file.close()

"""-------------------------
 main
-------------------------- """
def main():
    #log on/register loop
    done = False
    while not done:
        choice = input("""[1] Log on
[2] Register
[Any key] Quit
==> """)
        if choice == "1":       #Log on
            while not done:
                uName = input("User name: ")
                pw = input("Password: ")
                check_log = check_log_on(uName, pw)
                if check_log == 1:
                    print("Log on successful!")
                    print()
                    user_name = uName
                    done = True
                else:
                    print("Invalid User Name or password. Check and try again")
                    print()
            
        elif choice == "2":     #register new customer 
            while not done:
                uName = input("User name: ")
                pw = input("Password: ")
                address = input("Address: ")
                phone = input("Phone Number: ")
                credit_num = input("Credit Card #: ")
                complete = register(uName,pw,address,phone,credit_num)
                if complete == 1:
                    print("Registered!")
                    print()
                    user_name = uName
                    done = True
                elif complete == 0:
                    print("Invalid User Name or Credit Card #. Try Again")
                    print()
        else:
            print("Database connection closed.")
            print("Program Terminated!")
            cursor.close()
            db.close()
            return  #terminate program
    
    #search loop    
    print("Search for albums by: ")
    print()
    basket = []     # initialize empty shopping basket
    total = 0       # initialize gross total
    while True:
        choice = input("""[1] Search by Musician
[2] Search by Album Title
[3] Search by Producer Name
[4] Search by Song Name
[5] Checkout
[6] Add another Credit Card
[7] Purchase History
[Any key] Log-out
==> """)  
        if choice == '1':   # Search by Musician
            name = input("Musician name: ")
            rows = search_musician(name)
            if rows is not None:
                display_album(rows)
                num = int(input("Which item# would you like to buy?: "))
                total = total + float(rows[num-1][2])
                basket.append(rows[num-1])
                print("Item added to basket. Total price: ${}".format(total))
                print()
            else:
                print("No results!")
                
        elif choice == '2':     #Search by Album Title
            name = input("Album Title: ")
            rows = search_album(name)
            if rows is not None:
                display_album(rows)
                num = int(input("Which item# would you like to buy? (#): "))
                total = total + float(rows[num-1][2])
                basket.append(rows[num-1])
                print("Item added to basket. Total price: ${}".format(total))
                print()
            else:
                print("No results")     
            
        elif choice == '3':     #Search by Producer Name
            name = input("Producer name: ")
            rows = search_producer(name)
            if rows is not None:
                display_album(rows)
                num = int(input("Which item# would you like to buy? (#): "))
                total = total + float(rows[num-1][2])
                basket.append(rows[num-1])
                print("Item added to basket. Total price: ${}".format(total))
                print()
            else:
                print("No results")

        elif choice == '4':     #Search by Song Name
            name = input("Song name: ")
            rows = search_song(name)
            if rows is not None:
                display_album(rows)
                num = int(input("Which album would you like to buy? (#): "))
                total = total + float(rows[num-1][2])
                basket.append(rows[num-1])
                print("Item added to basket. Total price: ${}".format(total))
                print()
            else:
                print("No results")
            
        elif choice == '5':     # Checkout
            if len(basket)>0:
                rows = get_credit_cards(user_name)
                display_credit_cards(rows)
                num = int(input("Which card would you like to use? (#): "))
                checkout(user_name,basket,rows[num-1][0])
                print("Checkout complete. Thank you for shopping!")
                print()
            else:
                print("Nothing in shopping baskets!")
        
        elif choice == '6':     #Add another Credit Card
                new_cc = int(input("Enter new credit card #: "))
                num = add_new_cc(user_name,str(new_cc))
                if num == 1:
                    print("New credit card added")
                    print()
                else:
                    print("Credit Card already exits")
                    print()
                    
        elif choice == '7':     #View Customer's Purchase History
            rows = get_purcahse_history(user_name)
            display_purchases(rows)
            
        else:           # terminate and exit
            print("Logged out. Thank you for shopping!")
            print("Database connection closed.")
            print("Program Terminated")
            cursor.close()
            db.close()
            break


main()
# rows = retrieve_all('registered_customer')
# print_table(rows)
# rows = retrieve_all('credit_cards')
# print_table(rows)
# rows = retrieve_all('purchase')
# print_table(rows)
#add_cus()