import psycopg2
import json
conn = psycopg2.connect(dbname='XXX', user='XXX', 
                        password='XXX', host='XXX', port= XXX)

conn_gp = psycopg2.connect(dbname='XXX', user='XXX', 
                        password='XXX', host='XXX', port= XXX)

conn_dvh = psycopg2.connect(dbname='XXX', user='XXX', 
                        password='XXX', host='XXX', port= XXX)


def get_geo():
    arr_out = []
    cursor = conn.cursor()

    f = open('./bd_geo.txt', 'r', encoding="utf8")

    script = f.read()
    f.close()
    
    cursor.execute(script)
    out = cursor.fetchall()
    arr_out = []
    
    for i in out:
        arr_out.append(dict({'Банк-партнер':i[0], 
                        'Тип продукта':i[1], 
                        'Оффер':i[2], 
                        'Гео доступности':i[3], 
                        'Исключение гео доступности':i[4], 
                        'Гео факт':i[5], 
                        'Исключение гео факт':i[6], 
                        'Гео регистрации':i[7], 
                        'Исключение гео регистрации':i[8], 
                        'Гео работы':i[9], 
                        'Исключение гео работы':i[10]}))
    print(arr_out)
    return arr_out


def get_kvots():
    arr_out = []
    cursor = conn.cursor()

    f = open('./bd_kvots.txt', 'r', encoding="utf8")

    script = f.read()
    f.close()
    
    cursor.execute(script)
    out = cursor.fetchall()
    print(out[0])
    
    for i in out:
        arr_out.append(dict({'Банк-партнер':i[0], 
                        'Оффер':i[1], 
                        'День месяца':str(i[2]), 
                        'День недели':str(i[3]), 
                        'Час':str(i[4]), 
                        'Заявки':i[5], 
                        'Клики':i[6], 
                        'Активность квоты':i[7], 
                        'Активный оффер':i[8], 
                        'Тип продукта':i[9]}))
    print(arr_out)
    return arr_out


def get_1017():
    arr_out = []
    cursor = conn_gp.cursor()

    f = open('./bd_1017.txt', 'r', encoding="utf8")

    script = f.read()
    f.close()
    
    cursor.execute(script)
    out = cursor.fetchall()
    print(out[0])
    
    for i in out:
        arr_out.append(dict({'Банк-партнер':i[0], 
                        'Тип продукта':i[1], 
                        'Оффер':i[2], 
                        'Причина':str(i[3]), 
                        'Кол-во':i[4]}))
    print(arr_out)
    return arr_out

def get_cost():
    arr_out = []
    cursor = conn.cursor()

    f = open('./bd_cost.txt', 'r', encoding="utf8")

    script = f.read()
    f.close()
    
    cursor.execute(script)
    out = cursor.fetchall()
    print(out[0])
    
    for i in out:
        arr_out.append(dict({'Банк-партнер':i[0], 
                        'Тип продукта':i[1], 
                        'Оффер':i[2], 
                        'Активные продукты':str(i[3]), 
                        'Закрутка':i[4]}))
    print(arr_out)
    return arr_out

def get_cost_2():
    arr_out = []
    cursor = conn_dvh.cursor()

    f = open('./bd_cost_2.txt', 'r', encoding="utf8")

    script = f.read()
    f.close()
    
    cursor.execute(script)
    out = cursor.fetchall()
    print(out[0])
    
    for i in out:
        arr_out.append(dict({'Код оффер':i[0], 
                        'Код продукта':i[1], 
                        'Тип продукта':i[2], 
                        'Закрутка':i[3], 
                        'Конверсия (для депозитов)':i[4],
                        'Позиция продукта (для МФО)': i[5]}))
    print(arr_out)
    return arr_out
def get_sum():
    arr_out = []
    cursor = conn.cursor()

    f = open('./bd_sum.txt', 'r', encoding="utf8")

    script = f.read()
    f.close()
    
    cursor.execute(script)
    out = cursor.fetchall()
    print(out[0])
    
    for i in out:
        arr_out.append(dict({'Банк':i[0], 
                        'Тип продукта':i[1], 
                        'Оффер':i[2], 
                        'Продукт':i[3], 
                        'Название продукта':i[4],
                        'Сумма на продукте (макс.)': i[5],
                        'Сумма на оффере (макс.)': i[6]}))
    print(arr_out)
    return arr_out

def get_srok():
    arr_out = []
    cursor = conn.cursor()

    f = open('./bd_srok.txt', 'r', encoding="utf8")

    script = f.read()
    f.close()
    
    cursor.execute(script)
    out = cursor.fetchall()
    print(out)
    
    for i in out:
        arr_out.append(dict({'Банк':i[0], 
                        'Тип продукта':i[1], 
                        'Оффер':i[2], 
                        'Продукт':i[3], 
                        'Название продукта':i[4],
                        'Сумма на продукте (макс.)': i[5],
                        'Сумма на оффере (макс.)': i[6]}))
    print(arr_out)
    return arr_out				 		