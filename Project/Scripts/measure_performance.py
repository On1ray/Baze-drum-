import subprocess
import time
import sys
import os

QUERY_PY = os.path.join(os.path.dirname(__file__), 'query.py')
QUERIES_DIR = r'E:\Рабочий\Учеба\БД\DB\DB\sql\queries'
QUERY_FILES = [
    '04_sales_stock_forecast.sql',
    '05_manager_monthly_rating.sql'
]

def measure_query(query_path, repeat=3):
    """Выполняет query.py для данного SQL-файла repeat раз и возвращает среднее время."""
    times = []
    for i in range(repeat):
        start = time.perf_counter()
        result = subprocess.run(
            [sys.executable, QUERY_PY, query_path],
            capture_output=True, text=True
        )
        end = time.perf_counter()
        elapsed = end - start
        times.append(elapsed)
        if i == 0:
            print(f"--- Первые строки вывода {os.path.basename(query_path)} ---")
            print('\n'.join(result.stdout.splitlines()[:10]))
            if result.stderr:
                print("Ошибки:", result.stderr[:200])
    avg_time = sum(times) / len(times)
    return avg_time, times

def main():
    print("=" * 60)
    print("ИЗМЕРЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ ЗАПРОСОВ")
    print("=" * 60)
    results = {}
    for qfile in QUERY_FILES:
        full_path = os.path.join(QUERIES_DIR, qfile)
        if not os.path.exists(full_path):
            print(f"Файл не найден: {full_path}")
            continue
        print(f"\nВыполняется {qfile}...")
        avg, all_times = measure_query(full_path, repeat=3)
        results[qfile] = {'avg': avg, 'times': all_times}
        print(f"Среднее время: {avg:.4f} сек (замеры: {', '.join(f'{t:.4f}' for t in all_times)})")
    
    print("\n" + "=" * 60)
    print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ (БЕЗ ИНДЕКСОВ)")
    for qfile, data in results.items():
        print(f"{qfile}: {data['avg']:.4f} сек")
    print("=" * 60)

if __name__ == '__main__':
    main()