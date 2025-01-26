import psycopg2
from psycopg2 import sql, OperationalError


# Функция, которая создает таблицы phones и clients в базе данных
def create_db(database="clients_db", user="postgres", password="password"):
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
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

# Вызов функции создания таблиц в базе данных
create_db()


# Функция, которая добавляет нового клиента в базу данных
def add_client(first_name, last_name, email, phone_number, database="clients_db", user="postgres", password="password"):
  try:
    conn = psycopg2.connect(database=database, user=user, password=password)
    with conn.cursor() as cur:

      # Добавляем нового клиента в таблицу clients
      insert_client_query = """
      INSERT INTO clients (first_name, last_name, email) 
      VALUES (%s, %s, %s)
      RETURNING client_id;
      """
      cur.execute(insert_client_query, (first_name, last_name, email))
      
      # Получаем ID нового клиента
      new_client_id = cur.fetchone()[0]
      
      # Добавляем телефон клиента в таблицу phones
      insert_phone_query = """
      INSERT INTO phones (client_id, phone_number) 
      VALUES (%s, %s);
      """
      cur.execute(insert_phone_query, (new_client_id, phone_number))
      
      # Фиксация изменений в базе данных
      conn.commit()
      
      # Проверяем информацию о новом клиенте в базе данных
      print(f"Добавлен новый клиент: ID {new_client_id}, ФИО {first_name} {last_name}, эл. почта {email}, телефон {phone_number}")

  # Обработка ошибок   
  except OperationalError as e:
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

# Вызов функции добавления нового клиента
add_client(
  "first_name", 
  "last_name", 
  "r.mail@example.com", 
  "+79167750813"
  )


# Функция, которая добавляет телефон для существующего клиента
def add_phone_number(database, user, password, email, phone_number):
  try:
    # Подключение к базе данных
    conn = psycopg2.connect(database=database, user=user, password=password)
    
    with conn.cursor() as cur:
      # Проверка существования клиента по email
      cur.execute("SELECT client_id FROM clients WHERE email = %s", (email,))
      result = cur.fetchone()
      
      if result is None:
        print(f"Клиент с электронной почтой {email} не найден.")
        return
      
      client_id = result[0]

      # Проверка существования номера телефона для данного клиента
      cur.execute("SELECT phone_id FROM phones WHERE client_id = %s AND phone_number = %s", (client_id, phone_number))
      phone_result = cur.fetchone()

      if phone_result:
        print(f"{phone_number} уже есть у клиента.")
        return
      
      # Добавляем номер телефона для существующего клиента
      cur.execute("""
      INSERT INTO phones (client_id, phone_number) VALUES (%s, %s);
      """, (client_id, phone_number))
      
      # Фиксация изменений в базе данных
      conn.commit()
      
      # Вывод информации о добавленом номере телефона
      print(f"Клиенту с ID {client_id} и эл. почтой {email} добавлен номер телефона {phone_number}")
  
  except OperationalError as e:
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

# Вызов функции добавления телефонного номера с передачей в функцию параметров для подключения базы данных
add_phone_number(
   database="clients_db", 
   user="postgres", 
   password="password", 
   email="email@example.com", 
   phone_number="+43125670307"
   )


# Функция, которая изменяет информацию о существующем клиенте
def update_client_info(database, user, password, client_email, new_first_name=None, new_last_name=None, new_email=None, new_phone_number=None):
  try:
    # Подключение к базе данных
    conn = psycopg2.connect(database=database, user=user, password=password)

    with conn.cursor() as cur:
      # Поиск клиента по email
      cur.execute("SELECT client_id FROM clients WHERE email = %s", (client_email,))
      result = cur.fetchone()

      if result is None:
        print(f"Клиент с email {client_email} не найден.")
        return

      # Извлечение client_id для дальнейших операций
      client_id = result[0]

      # Обновление информации о клиенте
      if new_first_name:
        cur.execute("UPDATE clients SET first_name = %s WHERE email = %s", (new_first_name, client_email))
      if new_last_name:
        cur.execute("UPDATE clients SET last_name = %s WHERE email = %s", (new_last_name, client_email))
      if new_email:
        cur.execute("UPDATE clients SET email = %s WHERE email = %s", (new_email, client_email))

      # Обновление или добавление номера телефона
      if new_phone_number:
        cur.execute("SELECT phone_id FROM phones WHERE client_id = %s", (client_id,))
        phone_result = cur.fetchone()
        
        if phone_result:
          cur.execute("UPDATE phones SET phone_number = %s WHERE client_id = %s", (new_phone_number, client_id))
        else:
          cur.execute("INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)", (client_id, new_phone_number))
      
      # Подтверждение изменений
      conn.commit()

      # Проверяем информацию о новом клиенте в базе данных
      print(f"Информация о клиенте с эл. почтой {client_email} обновлена: ФИО {new_first_name} {new_last_name}, эл. почта {new_email}, телефон {new_phone_number}")
      # print(f"Информация о клиенте с email {client_email} была успешно обновлена.")
  
  except OperationalError as e:
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

# Вызов функции, которая изменяет информацию о существующем клиенте
update_client_info(
  database="clients_db", 
  user="postgres", 
  password="password", 
  client_email="updated.r.mail@example.com", 
  new_first_name="Иван", 
  new_last_name="Петров", 
  new_email="r.mail@example.com", 
  new_phone_number="-56782321212"
)


# Функция, которая удаляет все телефоны существующего клиента
def delete_all_phone_numbers(database, user, password, email):
  try:
    # Подключение к базе данных
    conn = psycopg2.connect(database=database, user=user, password=password)
    
    with conn.cursor() as cur:
      # Проверка существования клиента по email
      cur.execute("SELECT client_id FROM clients WHERE email = %s", (email,))
      result = cur.fetchone()
      
      if result is None:
        print(f"Клиент с электронной почтой {email} не найден.")
        return
      
      client_id = result[0]

      # Удаление всех номеров телефона у существующего клиента
      cur.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))

      # Фиксация изменений в базе данных
      conn.commit()
      
      # Вывод информации об удалении всех номеров телефона
      print(f"Все номера телефонов были удалены у клиента с ID {client_id} и эл. почтой {email}")
  
  except OperationalError as e:
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

Вызов функции удаления всех телефонов у клиента с параметрами для подключения к базе данных
delete_all_phone_numbers(
    database="clients_db", 
    user="postgres", 
    password="password", 
    email="stiv.kvant@example.com"
    )


# Функция, которая удаляет определенный телефон существующего клиента
def delete_phone_number(database, user, password, email, phone_number):
  try:
    # Подключение к базе данных
    conn = psycopg2.connect(database=database, user=user, password=password)
    
    with conn.cursor() as cur:
      # Проверка существования клиента по email
      cur.execute("SELECT client_id FROM clients WHERE email = %s", (email,))
      result = cur.fetchone()
      
      if result is None:
        print(f"Клиент с электронной почтой {email} не найден.")
        return
      
      client_id = result[0]

      # Проверка существования номера телефона для данного клиента
      cur.execute("SELECT phone_id FROM phones WHERE client_id = %s AND phone_number = %s", (client_id, phone_number))
      phone_result = cur.fetchone()

      if phone_result is None:
        print(f"Номер {phone_number} не найден у клиента.")
        return
      
      # Удаление определенного номера телефона у существующего клиента
      cur.execute("DELETE FROM phones WHERE client_id = %s AND phone_number = %s", (client_id, phone_number))
      
      # Фиксация изменений в базе данных
      conn.commit()
      
      # Вывод информации об удалении номера телефона
      print(f"Номер телефона {phone_number} был удалён у клиента с ID {client_id} и эл. почтой {email}")
  
  except OperationalError as e:
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

# Вызов функции удаления определеного телефонного номера с передачей в функцию параметров для подключения базы данных
delete_phone_number(
    database="clients_db", 
    user="postgres", 
    password="password", 
    email="email@example.com", 
    phone_number="+43125670307"
    )


# Функция, которая удаляет всю информацию о клиенте
def delete_client_info(database, user, password, email):
  try:
    # Подключение к базе данных
    conn = psycopg2.connect(database=database, user=user, password=password)
    
    with conn.cursor() as cur:
      # Проверка существования клиента по email
      cur.execute("SELECT client_id FROM clients WHERE email = %s", (email,))
      result = cur.fetchone()
      
      if result is None:
        print(f"Клиент с {email} не найден.")
        return
      
      client_id = result[0]

      # Удаление всех номеров телефона, связанных с клиентом
      cur.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))

      # Удаление информации о клиенте из таблицы clients
      cur.execute("DELETE FROM clients WHERE client_id = %s", (client_id,))

      # Фиксация изменений в базе данных
      conn.commit()
      
      # Вывод информации об удалении клиента
      print(f"Вся информация о клиенте с ID {client_id} и эл. почтой {email} была удалена.")
  
  except OperationalError as e:
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

# Вызов функции для удаления всей информации о клиенте
delete_client_info(
    database="clients_db", 
    user="postgres", 
    password="password", 
    email="mail@example.com"
    )


# Функция, которая ищет информацию о клиенте по его данным: имени, фамилии, email или телефону.
def find_client_info(database, user, password, first_name=None, last_name=None, email=None, phone_number=None):
  try:
    # Подключение к базе данных
    conn = psycopg2.connect(database=database, user=user, password=password)

    with conn.cursor() as cur:

      # Создание SQL-запроса и списка параметров для фильтрации
      query = "SELECT c.client_id, c.first_name, c.last_name, c.email, p.phone_number FROM clients c LEFT JOIN phones p ON c.client_id = p.client_id WHERE "
      conditions = []
      params = []

      if first_name:
        conditions.append("c.first_name = %s")
        params.append(first_name)
      if last_name:
        conditions.append("c.last_name = %s")
        params.append(last_name)
      if email:
        conditions.append("c.email = %s")
        params.append(email)
      if phone_number:
        conditions.append("p.phone_number = %s")
        params.append(phone_number)

      # Если нет условий поиска, возврат с сообщением
      if not conditions:
        print("Пожалуйста, укажите хотя бы одно условие поиска.")
        return

      # Объединение условий в запрос
      query += " AND ".join(conditions)

      # Выполнение SQL-запроса
      cur.execute(query, tuple(params))
      results = cur.fetchall()

      if not results:
        print("Клиент с указанными данными не найден.")
      else:
        for result in results:
          client_id, first_name, last_name, email, phone_number = result
          print(f"ID клиента: {client_id}")
          print(f"Имя: {first_name}")
          print(f"Фамилия: {last_name}")
          print(f"Email: {email}")
          print(f"Телефон: {phone_number if phone_number else 'не указан'}")
          print("="*40)

  except OperationalError as e:
    print(f"Операционная ошибка: {e}")
  except Exception as e:
    print(f"Произошла ошибка: {e}")
  finally:
    if conn:
      conn.close()

# Пример вызова функции
find_client_info(
  database="clients_db",
  user="postgres",
  password="password",
  first_name="Steven",
  last_name="Quantum",
  email="updated.stiv.kvant@example.com",
  phone_number="+1234567890"
)