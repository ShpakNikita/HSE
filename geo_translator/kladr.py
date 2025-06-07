import sys
import argparse
from dadata import Dadata
import pandas as pd
import os

# Настройки API
API_KEY = 'XXXX'
SECRET_KEY = 'XXXX'
dadata = Dadata(API_KEY, SECRET_KEY)

def get_address_info(kladr_code):
    """Получение полной информации об адресе по коду КЛАДР"""
    try:
        result = dadata.find_by_id("address", kladr_code)
        if result:
            data = result[0]['data']
            return {
                'region': data.get('region_with_type', ''),
                'area': data.get('area_with_type', ''),
                'city': data.get('city_with_type', ''),
                'settlement': data.get('settlement_with_type', ''),
                'street': data.get('street_with_type', ''),
                'house': data.get('house', ''),
                'postal_code': data.get('postal_code', '')
            }
        return None
    except Exception as e:
        print(f"Ошибка при обработке КЛАДР {kladr_code}: {e}", file=sys.stderr)
        return None

def get_kladr_by_address(address):
    """Получение полной информации по адресу"""
    try:
        result = dadata.suggest("address", address)
        if result:
            data = result[0]['data']
            return {
                'kladr_id': data.get('kladr_id', ''),
                'region': data.get('region_with_type', ''),
                'area': data.get('area_with_type', ''),
                'city': data.get('city_with_type', ''),
                'settlement': data.get('settlement_with_type', ''),
                'street': data.get('street_with_type', ''),
                'house': data.get('house', ''),
                'postal_code': data.get('postal_code', '')
            }
        return None
    except Exception as e:
        print(f"Ошибка при обработке адреса '{address}': {e}", file=sys.stderr)
        return None

def process_file_input(input_filename, file_type, output_filename, mode):
    """Обработка файлового ввода с детализацией по столбцам"""
    try:
        # Определяем расширение файла
        ext = '.csv' if file_type == '1' else ('.xlsx' if file_type == '2' else None)
        if not ext:
            print("Неверный тип файла", file=sys.stderr)
            return False
        
        input_path = f"{input_filename}{ext}"
        
        # Читаем файл
        if ext == '.csv':
            df = pd.read_csv(input_path, header=None, dtype=str)
        else:
            df = pd.read_excel(input_path, header=None, dtype=str)
        
        # Обрабатываем данные
        results = []
        for _, row in df.iterrows():
            value = str(row[0]).strip() if pd.notna(row[0]) else ''
            if not value:
                continue
                
            if mode == '1':  # KLADR -> Address
                address_info = get_address_info(value)
                if address_info:
                    results.append({
                        'Исходный КЛАДР': value,
                        'Регион': address_info['region'],
                        'Район': address_info['area'],
                        'Город': address_info['city'],
                        'Населенный пункт': address_info['settlement'],
                        'Улица': address_info['street'],
                        'Дом': address_info['house'],
                        'Индекс': address_info['postal_code']
                    })
            else:  # Address -> KLADR
                kladr_info = get_kladr_by_address(value)
                if kladr_info:
                    results.append({
                        'Исходный адрес': value,
                        'КЛАДР': kladr_info['kladr_id'],
                        'Регион': kladr_info['region'],
                        'Район': kladr_info['area'],
                        'Город': kladr_info['city'],
                        'Населенный пункт': kladr_info['settlement'],
                        'Улица': kladr_info['street'],
                        'Дом': kladr_info['house'],
                        'Индекс': kladr_info['postal_code']
                    })
        
        if not results:
            print("Нет данных для сохранения", file=sys.stderr)
            return False
            
        # Сохраняем результат
        output_path = f"{output_filename}.xlsx"
        df_result = pd.DataFrame(results)
        df_result.to_excel(output_path, index=False, engine='openpyxl')
            
        print(f"Результат сохранен в {output_path}")
        return True
        
    except Exception as e:
        print(f"Ошибка обработки файла: {e}", file=sys.stderr)
        return False

def process_manual_input(values, output_filename, mode):
    """Обработка ручного ввода с детализацией по столбцам"""
    try:
        results = []
        for value in values:
            value = str(value).strip()
            if not value:
                continue
                
            if mode == '1':  # KLADR -> Address
                address_info = get_address_info(value)
                if address_info:
                    results.append({
                        'Исходный КЛАДР': value,
                        'Регион': address_info['region'],
                        'Район': address_info['area'],
                        'Город': address_info['city'],
                        'Населенный пункт': address_info['settlement'],
                        'Улица': address_info['street'],
                        'Дом': address_info['house'],
                        'Индекс': address_info['postal_code']
                    })
            else:  # Address -> KLADR
                kladr_info = get_kladr_by_address(value)
                if kladr_info:
                    results.append({
                        'Исходный адрес': value,
                        'КЛАДР': kladr_info['kladr_id'],
                        'Регион': kladr_info['region'],
                        'Район': kladr_info['area'],
                        'Город': kladr_info['city'],
                        'Населенный пункт': kladr_info['settlement'],
                        'Улица': kladr_info['street'],
                        'Дом': kladr_info['house'],
                        'Индекс': kladr_info['postal_code']
                    })
        
        if not results:
            print("Нет данных для сохранения", file=sys.stderr)
            return False
            
        # Сохраняем результат в Excel с группировкой по столбцам
        output_path = f"{output_filename}.xlsx"
        df_result = pd.DataFrame(results)
        df_result.to_excel(output_path, index=False, engine='openpyxl')
            
        print(f"Результат сохранен в {output_path}")
        return True
        
    except Exception as e:
        print(f"Ошибка обработки: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description='KLADR Address Translator')
    parser.add_argument('mode', choices=['1', '2'], help='1: KLADR->Address, 2: Address->KLADR')
    parser.add_argument('input_method', choices=['1', '2'], help='1: File input, 2: Manual input')
    parser.add_argument('output_filename', help='Output filename without extension')
    
    # Для файлового ввода
    parser.add_argument('--file_type', choices=['1', '2'], help='1: CSV, 2: Excel (required for file input)')
    parser.add_argument('--input_filename', help='Input filename without extension (required for file input)')
    
    # Для ручного ввода
    parser.add_argument('values', nargs='*', help='Values to process (for manual input)')
    
    args = parser.parse_args()
    
    if args.input_method == '1':  # Файловый ввод
        if not args.file_type or not args.input_filename:
            print("Для файлового ввода требуются --file_type и --input_filename", file=sys.stderr)
            sys.exit(1)
        success = process_file_input(
            args.input_filename,
            args.file_type,
            args.output_filename,
            args.mode
        )
    else:  # Ручной ввод
        if not args.values:
            print("Для ручного ввода требуются значения", file=sys.stderr)
            sys.exit(1)
        success = process_manual_input(
            args.values,
            args.output_filename,
            args.mode
        )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()