from test3 import get_data, conn, cursor
from jira import JIRA
import webbrowser
import logging
import time
import sys
import json
import os
import concurrent.futures


# Configuring logging
logging.basicConfig(
    filename='jira_update.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def html_to_jira_markup(html):
    """
    Converts HTML to Jira Markup.
    """
    # Removing the extra characters {}
    html = html.replace("{", "").replace("}", "")

    # Replace HTML tags with Jira Markup
    html = html.replace("<b>", "*").replace("</b>", "*") 
    html = html.replace("<u>", "_").replace("</u>", "_")  
    html = html.replace("<br>", "\n") 
    html = html.replace("<i>", "_").replace("</i>", "_")  

    return html

def extract_issue_key(issue_url):
    """
    Extracts the task key from the Jira link.
    """
    return issue_url.split("/")[-1]

def process_offers(offers, cursor):
    """Batch processing of offers"""
    try:
        with open('./script2.txt', 'r', encoding="utf8") as f:
            script_template = f.read()
        
        script = script_template.split('where doc.code in ()')[0] + \
                'where doc.code in (' + offers + ')' + \
                script_template.split('where doc.code in ()')[1]
        
        cursor.execute(script)
        records = cursor.fetchall()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(process_record, records))
        
        return ''.join(results)
        
    except Exception as e:
        logging.error(f"Ошибка при выполнении SQL-запроса: {e}")
        return ""

def process_record(self, record):
    out = ''
    for i in record:
        if isinstance(i, str):
            if 'Настройки от' in i:
                out += i
            else:
                out += i + '~~~'
        else:
            for f in i:
                out += str(f) + '~~~'
    return out

def update_jira_issue(issue_key, description):
    JIRA_SERVER = "XXX"
    JIRA_LOGIN = "XXX"
    JIRA_PASSWORD = "XXX"

    try:
        jira = JIRA(
            server=JIRA_SERVER,
            basic_auth=(JIRA_LOGIN, JIRA_PASSWORD))
        logging.info("Успешное подключение к Jira.")
    except Exception as e:
        logging.error(f"Ошибка подключения к Jira: {e}")
        return False

    try:
        issue = jira.issue(issue_key)
        logging.info(f"Задача {issue_key} успешно получена.")
    except Exception as e:
        logging.error(f"Ошибка при получении задачи {issue_key}: {e}")
        return False

    try:
        issue.update(description=description)
        logging.info(f"Описание задачи {issue_key} обновлено.")
        return True
    except Exception as e:
        logging.error(f"Ошибка при обновлении задачи {issue_key}: {e}")
        return False

def process_batch_mode(input_file):
    """
    Processes tasks in batch mode (from a JSON file)
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
            
        if not tasks:
            logging.error("Файл с задачами пуст")
            return False
            
        success_count = 0
        for task in tasks:
            if len(task) < 2:
                continue
                
            issue_url = task[0]
            offers = task[1]
            
            if not issue_url or not offers:
                continue
                
            issue_key = extract_issue_key(issue_url)
            logging.info(f"Обработка задачи {issue_key} с офферами: {offers}")
            
            description = process_offers(offers, cursor)
            if not description:
                logging.error(f"Не удалось получить данные для задачи {issue_key}")
                continue
                
            if update_jira_issue(issue_key, description):
                success_count += 1
                webbrowser.open(issue_url)
            else:
                logging.error(f"Ошибка при обновлении задачи {issue_key}")
                
        logging.info(f"Успешно обработано {success_count} из {len(tasks)} задач")
        return success_count > 0
        
    except Exception as e:
        logging.error(f"Ошибка при пакетной обработке: {e}")
        return False

def interactive_mode():
    tasks = []  

    while True:
        # Entering a link to a task
        issue_url = input("Введите ссылку на задачу в Jira (например, xxxx ").strip()
        if not issue_url:
            break
            
        issue_key = extract_issue_key(issue_url)
        print(f"Ключ задачи: {issue_key}")
        logging.info(f"Добавлена задача: {issue_key}")

        # Entering offer numbers
        offers = input('Введите номера офферов через запятую: ')
        offers = offers.replace(" ", "").strip() 
        if not offers:
            print("Офферы не введены, пропускаем задачу")
            continue
            
        logging.info(f"Введены офферы: {offers}")

        tasks.append((issue_key, offers, issue_url))
        logging.info(f"Задача {issue_key} добавлена в список.")

        add_more = input("Добавить ещё одну задачу? (y/n): ").strip().lower()
        if add_more != 'y':
            break

    success_count = 0
    for issue_key, offers, issue_url in tasks:
        logging.info(f"Обновление задачи {issue_key}...")
        description = process_offers(offers, cursor)
        
        if update_jira_issue(issue_key, description):
            success_count += 1
            print(f"Задача {issue_key} успешно обновлена.")
            webbrowser.open(issue_url)
        else:
            print(f"Ошибка при обновлении задачи {issue_key}. Проверьте логи.")
            
    print(f"\nИтог: успешно обновлено {success_count} из {len(tasks)} задач")

def main():
    if len(sys.argv) > 1:
        # JSON file processing mode
        input_file = sys.argv[1]
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            success_count = 0
            total = len(data)
            
            for pair_name, pair_data in data.items():
                issue_url = pair_data["link"]
                offers = pair_data["offer"]
                
                if not issue_url or not offers:
                    continue
                    
                issue_key = extract_issue_key(issue_url)
                logging.info(f"Обработка задачи {issue_key} с офферами: {offers}")
                
                description = process_offers(offers, cursor)
                if not description:
                    logging.error(f"Не удалось получить данные для задачи {issue_key}")
                    continue
                    
                if update_jira_issue(issue_key, description):
                    success_count += 1
                    webbrowser.open(issue_url)
                else:
                    logging.error(f"Ошибка при обновлении задачи {issue_key}")
            
            logging.info(f"Успешно обработано {success_count} из {total} задач")
            return success_count > 0
            
        except Exception as e:
            logging.error(f"Ошибка при обработке JSON файла: {e}")
            return False
    else:
        interactive_mode()

if __name__ == "__main__":
    main()