import logging
import psycopg2

conn = psycopg2.connect(
    dbname='XXX', 
    user='XXX', 
    password='XXX', 
    host='XXX', 
    port=XXX
)
cursor = conn.cursor()

def get_data(offers, cursor):
    """
    Gets data from the database on offers.
    """
    try:
        with open('./script2.txt', 'r', encoding="utf8") as f:
            script = f.read()

        # Modifying the SQL query
        script = script.split('where doc.code in ()')[0] + 'where doc.code in (' + offers + ')' + script.split('where doc.code in ()')[1]

        # Executing the request
        cursor.execute(script)
        records = cursor.fetchall()

        # Forming the result
        out = ''
        for row in records:
            for i in row:
                if 'Настройки от' in i:
                    out += i
                else:
                    try:
                        out += i + '~~~'
                    except Exception:
                        for f in i:
                            out += f + '~~~'
        return out

    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        return ""