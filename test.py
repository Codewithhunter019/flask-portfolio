import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='muneeb0987@'  # 👈 Replace this with your actual MySQL root password
    )

    if connection.is_connected():
        print("✅ Connected to MySQL successfully!")
        cursor = connection.cursor()
        cursor.execute("SHOW DATABASES;")
        print("\n📂 Existing Databases:")
        for db in cursor.fetchall():
            print(" -", db[0])

except Error as e:
    print("❌ Error while connecting to MySQL:", e)

finally:
    if 'connection' in locals() and connection.is_connected():
        connection.close()
