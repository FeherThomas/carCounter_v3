import mysql.connector
from mysql.connector import Error as mysqlError


def create_table():
    connection = get_connection()

    mysql_create_table_carcounter = """CREATE TABLE CarCounter (
                                CounterId int NOT NULL AUTO_INCREMENT,
                                Day DateTime NOT NULL,
                                Direction Varchar(20),
                                PRIMARY KEY (CounterId))"""

    cursor = connection.cursor()
    try:
        result = cursor.execute(mysql_create_table_carcounter)
        print(result)
    except mysqlError as mse:
        print("Error while insert into database:", mse)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Mysql connection is closed")


def insert_into_db(direction):
    connection = get_connection()

    mysql_insert_into_carcounter = "INSERT INTO CarCounter (Day, Direction) VALUES(now(), '" + direction + "')"
    # mysql_insert_into_carcounter = "INSERT INTO CarCounter (Day, Direction) VALUES(now(), 'left')"

    cursor = connection.cursor()
    try:
        result = cursor.execute(mysql_insert_into_carcounter)
        print(result)

        connection.commit()
    except mysqlError as mse:
        print("Error during insert into database", mse)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Mysql connection is closed")


def drop_table():
    connection = get_connection()

    mysql_drop_table = """DROP TABLE CarCounter"""

    cursor = connection.cursor()
    try:
        result = cursor.execute(mysql_drop_table)
        print(result)
    except mysqlError as mse:
        print("Error while dropping table CarCounter", mse)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySql connection is closed")


def get_connection():
    try:
        connection = mysql.connector.connect(host='localhost',
                                             database='carcounterDB',
                                             user='car_counter',
                                             password='StrongPassword')

        if connection.is_connected():
            db_info = connection.get_server_info()
            print("Connected to MySql Server version ", db_info)
            cursor = connection.cursor()
            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You are connected to database: ", record)
            return connection

    except mysqlError as mse:
        print("Error while connecting to MySql:", mse)
    # finally:
    #    if connection.is_connected():
    #        cursor.close()
    #        connection.close()
    #        print("Mysql connection is closed")


def get_current_vehicle_count():
    connection = get_connection()

    mysql_drop_table = "SELECT MAX(CounterId) FROM CarCounter cc"

    cursor = connection.cursor()
    try:
        cursor.execute(mysql_drop_table)

        result = cursor.fetchone()[0]
        if result is None:
            return 0

        return result

    except mysqlError as mse:
        print("Error while dropping table CarCounter", mse)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySql connection is closed")


def update_car_direction(car):
    connection = get_connection()

    mysql_drop_table = "UPDATE CarCounter SET Direction = '" + car.direction + \
                       "' WHERE CounterId = " + str(car.carId)

    cursor = connection.cursor()
    try:
        cursor.execute(mysql_drop_table)
        connection.commit()

        print("Updated direction of car: ", car.carId)
    except mysqlError as mse:
        print("Error while dropping table CarCounter", mse)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySql connection is closed")
