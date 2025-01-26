# Функция для создания таблиц в базе данных

import psycopg2
from psycopg2 import sql, OperationalError

def create_db(database="clients_db", user="postgres", password="1Qazse432"):
  try:
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn.cursor() as cur:

      # Удаление таблиц phones и clients, если они существуют
      cur.execute("DROP TABLE IF EXISTS phones;")
      cur.execute("DROP TABLE IF EXISTS clients;")
      
      # Создание таблицы clients
      cur.execute("""
      CREATE TABLE IF NOT EXISTS clients (
        client_id SERIAL PRIMARY KEY,
        first_name VARCHAR(40) NOT NULL,
        last_name VARCHAR(40) NOT NULL,
        email VARCHAR(40) NOT NULL UNIQUE
      );""")
      
      # Создание таблицы phones
      cur.execute("""
      CREATE TABLE IF NOT EXISTS phones (
        phone_id SERIAL PRIMARY KEY,
        client_id INTEGER REFERENCES clients(client_id),
        phone_number VARCHAR(12)
      );""")
      
      # Фиксация изменений в базе данных
      conn.commit()

  # Обработка ошибок  
  except OperationalError as e:
    print(f"OperationalError: {e}")
  except Exception as e:
    print(f"An error occurred: {e}")
  finally:
    if conn:
      conn.close()

# Вызов функции создания таблиц в базе данных
create_db()