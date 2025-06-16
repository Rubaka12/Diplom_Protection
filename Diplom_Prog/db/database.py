import mysql.connector
from resources.config import DB_CONFIG
from datetime import datetime

def get_equipment_info_by_table(table_name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # !!! ВСТАВКА ИМЕНИ ТАБЛИЦЫ В СТРОКУ ЗАПРОСА !!!
    query_id = f"""
        SELECT equipment_id 
        FROM {table_name}
        WHERE id = 1 
    """
    cursor.execute(query_id)
    result_id = cursor.fetchone()

    if not result_id:
        cursor.close()
        conn.close()
        return None

    query = """
        SELECT id, name, location 
        FROM medical_equipment 
        WHERE id = %s
    """
    cursor.execute(query, (result_id[0],))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result:
        return {
            "id": result[0],
            "name": result[1],
            "location": result[2]
        }
    else:
        return None

# для стартовой страницы и её разновидностей, позволяет получить кол-во необходимых мини-окон
def get_machine_tables():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall() if row[0].startswith('eq_')]
    conn.close()
    return tables

def get_title_graph(table):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute(f"SELECT equipment_id FROM {table} LIMIT 1")
    equipment_id_result = cursor.fetchone()
    if equipment_id_result:
        equipment_id = equipment_id_result[0]  # Извлекаем первое значение из кортежа
    else:
        # Обработка случая, когда нет данных
        equipment_id = None
        return "Неизвестно"

    cursor.execute(f"SELECT Name, UM FROM standards WHERE Id_eq = {equipment_id}")
    Names_p = cursor.fetchall()
    Names = []
    Names_2 = []
    for i in Names_p:
        Fname = ": ".join(i)
        Names.append(Fname)
        Names_2.append(i[0])

    cursor.execute(f"SELECT Name, Min, Max FROM standards WHERE Id_eq = {equipment_id}")
    Names_p3 = cursor.fetchall()
    Names_3 = {name.strip(): (min_val, max_val) for name, min_val, max_val in Names_p3}
    #print("Names", Names) #выводим в подпись мини-окна
    #print("Names_2", Names_2) #используем для поиска эталонов
    #print("Names_3", Names_3) #используем для создания словаря

    cursor.execute(f"SELECT Name, UM, Min, Max FROM standards WHERE Id_eq = {equipment_id}")
    Names_p4 = cursor.fetchall()
    Names_4 = []

    print("Names_p4", Names_p4[0])
    for i in Names_p4:
        #print("i", i)
        new_data = i[:2] + (str(i[2]), str(i[3]))
        #print(new_data)
        Fname = "; ".join(new_data)
        Names_4.append(Fname)

    return Names, Names_2, Names_3, Names_4

# позволяет получить последние данные для заполениня графиков в мини-окнах
def get_latest_data(table, Name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    #print("")
    #print("table", table)
    cursor.execute(f"SELECT equipment_id FROM {table} LIMIT 1")
    equipment_id_result = cursor.fetchone()
    if equipment_id_result:
        equipment_id = equipment_id_result[0]  # Извлекаем первое значение из кортежа
    else:
        # Обработка случая, когда нет данных
        equipment_id = None
        return "Неизвестно"

    # cursor.execute(f"SELECT Name FROM standards WHERE Id_eq = {equipment_id}")
    # Names_p = cursor.fetchall()
    # NamesList = [row[0] for row in Names_p]
    # Names = ", ".join(f"`{name}`" for name in NamesList)
    #
    # print("Names", Names)
    # print("table", table)

    query = f"SELECT {Name} FROM {table} ORDER BY Timestamp DESC LIMIT 6"
    #query = "SELECT A1, А2, А3, A4 FROM eq_001 ORDER BY Timestamp DESC LIMIT 6"
    #print("query", query)
    cursor.execute(query)

    values = [row[0] for row in cursor.fetchall()]
    #print("values", values)
    conn.close()
    return values[::-1]  # от старого к новому

# производим поиск имени оборудования
def get_equipment_name(table_name):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    try:
        # Получаем equipment_id из таблицы данных
        cursor.execute(f"SELECT equipment_id FROM {table_name} LIMIT 1")
        equipment_id = cursor.fetchone()
        if not equipment_id:
            return "Неизвестно", "Неизвестно"

        # Используем полученный id для запроса имени оборудования и местоположения
        cursor.execute("SELECT Name, Location FROM medical_equipment WHERE id = %s", (equipment_id[0],))
        result = cursor.fetchone()
        if result:
            #print(result[0], result[1])
            return result[0], result[1]
        else:
            return "Неизвестно", "Неизвестно"
    finally:
        cursor.close()
        conn.close()

#фнкция по добавлению данных и эталонов в БД
def register_equipment(name, model, location, parameters):
    conn = mysql.connector.connect(**DB_CONFIG)

    cursor = conn.cursor()
    try:
            # 0. Проверка на уже существующее имя
            check_name_sql = "SELECT COUNT(*) FROM medical_equipment WHERE Name = %s"
            cursor.execute(check_name_sql, (name,))
            if cursor.fetchone()[0] > 0:
                raise ValueError(f"Оборудование с именем '{name}' уже существует.")
            print("0 этап завершён")

            # 1. Вставка в medical_equipment
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            insert_equipment_sql = """
                INSERT INTO medical_equipment (Name, Model, Location, Date_connected)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_equipment_sql, (name, model, location, now))
            equipment_id = cursor.lastrowid
            print("1 этап завершён")

            # 2. Определение номера новой таблицы
            cursor.execute("SHOW TABLES LIKE 'eq_%'")
            existing = cursor.fetchall()
            table_number = len(existing) + 1
            new_table_name = f"eq_{table_number:03d}"
            print("2 этап завершён")

            # 3. Создание новой таблицы с показателями
            print("parameters", parameters)
            indicators = [row[0] for row in parameters]
            columns_def = ", ".join([f"`{ind}` FLOAT NULL" for ind in indicators])
            print("indicators", indicators)
            create_table_sql = f"""
                CREATE TABLE `{new_table_name}` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    equipment_id INT,
                    {columns_def},
                    timestamp DATETIME NULL,
                    FOREIGN KEY (equipment_id) REFERENCES medical_equipment(Id)
                )
            """
            cursor.execute(create_table_sql)
            # Создаём список значений: первый элемент — equipment_id, остальные — None
            insert_values = [equipment_id] + [None] * (len(indicators))

            # Вставляем "equipment_id" как первый столбец
            indicators.insert(0, "equipment_id")

            # Формируем плейсхолдеры для SQL (%s, %s, %s, ...)
            placeholders_ind = ", ".join(["%s"] * len(indicators))

            # Формируем SQL-запрос
            insert_null_table = f"""
                INSERT INTO `{new_table_name}`
                ({", ".join(indicators)}) 
                VALUES 
                ({placeholders_ind})
            """

            # Отладочная печать
            print("new_table_name:", new_table_name)
            print("indicators:", indicators)
            print("insert_values:", insert_values)
            print("placeholders_ind:", placeholders_ind)
            print("insert_null_table:", insert_null_table)

            # Выполняем запрос
            cursor.execute(insert_null_table, insert_values)
            print("3 этап завершён")

            # 4. Создание и вставка в таблицу standards
            # Проверка существующих столбцов


            #-------------------------------------------------------------
            #новая функция
            for row in parameters:
                value_set = [row[0], row[1], float(row[2]), float(row[3]), row[4]]
                dynamic_values = []
                placeholders = ()
                insert_values = ()
                for value in value_set:
                    dynamic_values.append(value)
                    insert_values = [equipment_id] + dynamic_values
                    print("insert_values", insert_values)
                    print("len(insert_values)", len(insert_values))
                    placeholders = ", ".join(["%s"] * len(insert_values))
                    print("placeholders", placeholders)
                insert_standards_sql = f"""
                                            INSERT INTO standards (`Id_eq`, `Name`, `UM`, `Min`, `Max`, `Group`)
                                            VALUES ({placeholders})
                                        """
                cursor.execute(insert_standards_sql, insert_values)
            print("4 этап завершён")
            conn.commit()
    finally:
        cursor.close()
        conn.close()

#----------------------------------------------------------------------------------------------------------------------

def fetch_groups(equipment_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM standards WHERE id_eq = %s", (equipment_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if not row:
        return {}, []

    group_columns = [col for col in row if col.endswith('_Group') and row[col] not in (None, 0)]
    param_to_group = {}
    unique_groups = set()

    for col in group_columns:
        param = col[:-6]  # Remove '_Group' suffix
        group = row[col]
        param_to_group.setdefault(group, []).append(param)
        unique_groups.add(group)

    return param_to_group, list(unique_groups)


def param_descr(equipment_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = "SELECT * FROM standards WHERE id_eq = %s"
    cursor.execute(query, (equipment_id,))
    row = cursor.fetchone()
    columns = [desc[0] for desc in cursor.description]
    conn.close()

    descriptions = {}  # Словарь для описаний параметров

    if row:
        standards_dict = dict(zip(columns, row))
        for col in columns:
            if col.endswith('_UM') and standards_dict[col]:
                key = col[:-3]  # удаляем "_UM"
                values = []

                # Получаем связанные значения
                unit = standards_dict.get(f"{key}_UM")
                min_val = standards_dict.get(f"{key}_Min")
                max_val = standards_dict.get(f"{key}_Max")
                group = standards_dict.get(f"{key}_Group")

                # Формируем список непустых значений
                if unit: values.append(str(unit))
                if min_val not in (None, 0): values.append(str(min_val))
                if max_val not in (None, 0): values.append(str(max_val))
                if group: values.append(str(group))

                if values:
                    # Формируем строку описания
                    descriptions[key] = f"{key}: {', '.join(values)}"

    return descriptions

#-------------------------------------------------------------------------------------------------------
#регистрация пользователя
def insert_user(fio, location, post, login, password):
    conn = mysql.connector.connect(**DB_CONFIG)
    """
    Вставляет нового пользователя в таблицу users.
    Пока без шифрования пароля — для теста.

    Args:
        conn: объект соединения MySQL (mysql.connector.connect)
        fio: строка — ФИО
        location: строка — место работы
        post: строка — должность
        login: строка — логин
        password: строка — пароль (в дальнейшем нужно хешировать!)
    """
    try:
        cursor = conn.cursor()

        # SQL запрос с параметрами (защищён от SQL-инъекций)
        query = """
            INSERT INTO Engineers (Name, Post, Location,  Login, Password)
            VALUES (%s, %s, %s, %s, %s)
        """

        # Выполнение запроса
        cursor.execute(query, (fio, location, post, login, password))
        conn.commit()  # Подтверждаем изменения

        print("Пользователь успешно добавлен.")
    except mysql.connector.Error as err:
        print(f"Ошибка при добавлении пользователя: {err}")
        conn.rollback()  # Откат изменений при ошибке
    finally:
        cursor.close()
        conn.close()

def anomalis_count(table_name, equipment_id):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    names = get_title_graph(table_name)[1]
    # A1, A2, A3
    row_all = {}
    stand_all = {}
    print("names", names)
    print("table_name", table_name)
    for i in names:
        print("i", i)
        query = f"SELECT {i} FROM {table_name} WHERE equipment_id = {equipment_id}"
        print("query", query)
        cursor.execute(query)
        row = cursor.fetchall()
        print("row", row)
        row_all[i] = row  # сохраняем список значений по имени параметра
        #вторая часть
        # SELECT `Min`, `Max` FROM `standards` WHERE `Id_eq`= 1 AND `Name`="A1"
        query2 = "SELECT Min, Max FROM standards WHERE Id_eq = %s AND Name = %s"
        cursor.execute(query2, (equipment_id, i))
        print("query2", query2)
        stand = cursor.fetchall()
        stand_all[i] = stand

    #print("stand_all", stand_all)
    #print("row_all", row_all)
    #print("")

#находим аномалии
    anomalies = {}
    anom_text = {}
    for key, values in row_all.items():
        if key in stand_all:
            print("stand_all", stand_all[key][0])
            print("key", key)
            min_val = stand_all[key][0][0]
            max_val = stand_all[key][0][1]
            print("min_val", min_val)
            print("max_val", max_val)
            # Проверяем каждое значение из values
            for v in values:
                # Предположим, что v — кортеж из одной ячейки (row from fetchall), достанем из него значение
                val = v[0] if isinstance(v, (list, tuple)) else v
                if val < min_val:
                    if key not in anomalies:
                        anomalies[key] = []
                    anomalies[key].append(val)
                    if key not in anom_text:
                        anom_text[key] = []
                    text = "значение ниже нормы"
                    anom_text[key].append(text)
                elif val > max_val:
                    if key not in anomalies:
                        anomalies[key] = []
                    anomalies[key].append(val)
                    if key not in anom_text:
                        anom_text[key] = []
                    text = "значение выше нормы"
                    anom_text[key].append(text)
                    #print("anomalies", anomalies)

    #print("anomalies", anomalies)
    #print("anom_text", anom_text)

    print(" ")
    id_anom = {}
    for i in names:
        par = anomalies
        print("par", par)
        id_a = []
        for x in par[i]:
            print("X", x)
            query3 = f"SELECT id, timestamp FROM {table_name} WHERE {i} = {x}"
            cursor.execute(query3)
            print("query3", query3)
            records = cursor.fetchall()
            print("records", records)
            for record in records:
                record_id = record[0]
                timestamp_str = record[1].strftime("%Y-%m-%d %H:%M:%S")
                id_a.append((record_id, timestamp_str))
        id_anom[i] = id_a

    print("id_anom", id_anom)
    # INSERT INTO `anomalies`
    # (`equipment_id`, `metric_id`, `Name`, `Anomalies_telemetr`, `timestamp`)
    # VALUES
    # ('[value-2]','[value-3]','[value-4]','[value-5]','[value-6]')
    for d in names:
        Name = d
        print("\n")
        print("id_anom[Name]", id_anom[Name])
        i = 0
        for g in id_anom[Name]:
            equipment_id2 = equipment_id
            metric_id = str(g[0])
            print("i", len(anomalies[Name]))
            Anomalies_telemetr = anomalies[Name][i]
            print("Anomalies_telemetr", Anomalies_telemetr)
            text = anom_text[Name][i]
            print("text", text)
            #print("g", g)
            timestamp = g[1]
            i += 1
            query4 = f"INSERT INTO " \
             f"anomalies (equipment_id, metric_id, Name, Anomalies_telemetr, text, timestamp) " \
             f"VALUES ({equipment_id2}, {metric_id}, '{Name}', '{Anomalies_telemetr}','{text}', '{timestamp}')"
            #print("query4", query4)
            print("DF:YSQ VJVTYN query4", query4)
            cursor.execute(query4)
            conn.commit()
    cursor.close()
    conn.close

def chat_err(equipment_id):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Предположим, что у тебя есть таблица `equipment_errors` со следующими полями:
        # id, equipment_id, parameter, status, date, user
        query = """
            SELECT Name, Text, Anomalies_telemetr,  timestamp	
            FROM anomalies
            WHERE equipment_id = %s
        """
        cursor.execute(query, (equipment_id,))
        results = cursor.fetchall()

        return results  # [(A1, 'превышено', 150, '2025-06-01'), ...]

    except mysql.connector.Error as e:
        print("Ошибка при загрузке сообщений из БД:", e)
        return []
    finally:
        cursor.close()
        conn.close()