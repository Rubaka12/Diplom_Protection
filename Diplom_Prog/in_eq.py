import random
import time
from datetime import datetime
import mysql.connector
from resources.config import DB_CONFIG

def insert_random_data():
    while True:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cursor = conn.cursor()

            A1 = round(random.uniform(30, 150), 2)
            A2 = round(random.uniform(30, 150), 2)
            A3 = round(random.uniform(30, 150), 2)
            A4 = round(random.uniform(30, 150), 2)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            equipment_id = 1  # используем существующий ID

            query = """
                INSERT INTO eq_001 (equipment_id, A1, A2, A3, A4, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (equipment_id, A1, A2, A3, A4, timestamp)

            cursor.execute(query, values)
            conn.commit()
            print(f"Данные вставлены: {values}")
        except Exception as e:
            print(f"Ошибка: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

        time.sleep(10)

if __name__ == "__main__":
    insert_random_data()