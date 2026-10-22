from database import get_db_connection


try:
    connection = get_db_connection()

    if connection.is_connected():
        print("MySQL connection successful!")

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE();")

        database_name = cursor.fetchone()

        print("Connected database:", database_name[0])

        cursor.close()
        connection.close()

except Exception as error:
    print("MySQL connection failed!")
    print("Error:", error) 