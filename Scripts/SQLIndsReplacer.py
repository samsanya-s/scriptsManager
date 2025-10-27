import re
from datetime import datetime
import sys

# шаблон для indicator_value_on_year
year_pattern = re.compile(
    r"monitoring\.indicator_value_on_year\s*\(\s*[^,]+,\s*[^,]+,\s*([^,]+),\s*([^)]+)\)",
    re.IGNORECASE
)

# шаблон для indicator_value_on_period
period_pattern = re.compile(
    r"monitoring\.indicator_value_on_period\s*\(\s*[^,]+,\s*[^,]+,\s*([^,]+),\s*'([^']+)',\s*'([^']+)'\s*\)",
    re.IGNORECASE
)

TEMPLATE = """(
    SELECT CASE
        WHEN MAX(mi.type) = 1
        THEN COALESCE(SUM(mm.value), 0)
        ELSE COALESCE((array_agg(mm.value ORDER BY mm.measure_date DESC))[1], 0)
    END
    FROM monitoring.measure mm
    JOIN monitoring.indicator AS mi ON mi.id = mm.indicator_id        
    WHERE mm.monitoring_object_id = mo.id
      AND mi.code = '{code}'
      AND (
        (mi.type = 1 and EXTRACT(YEAR FROM mm.measure_date) = {year})
        OR
        (mi.type = 2 and EXTRACT(YEAR FROM mm.measure_date) <= {year})
      )
)"""

def replace_year(match):
    code = match.group(1).strip().strip("'\"")   # 3-й аргумент
    year = match.group(2).strip()               # 4-й аргумент
    return TEMPLATE.format(code=code, year=year)

def replace_period(match):
    code = match.group(1).strip().strip("'\"")  # 3-й аргумент
    date_start = match.group(2).strip()
    # достаем год из даты
    year = datetime.strptime(date_start, "%Y-%m-%d").year
    return TEMPLATE.format(code=code, year=year)

def transform_sql(sql: str) -> str:
    sql = year_pattern.sub(replace_year, sql)
    sql = period_pattern.sub(replace_period, sql)
    return sql

def main(input_file: str, output_file: str):
    with open(input_file, "r", encoding="utf-8") as f:
        sql_text = f.read()

    transformed = transform_sql(sql_text)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(transformed)

    print(f"Обработка завершена. Результат сохранён в {output_file}")

# if __name__ == "__main__":
#     if len(sys.argv) < 3:
#         print("Использование: python script.py input.sql output.sql")
#     else:
#         main(sys.argv.input, sys.argv.output)
