import xml.etree.ElementTree as ET
import re

INDICATORS = {}
SQL_QUERIES = []

# --- рекурсивная функция раскрытия формул ---
def expand_formula(code, visited=None, base_codes=None):
    if visited is None:
        visited = set()
    if base_codes is None:
        base_codes = set()

    if code in visited:
        return "i" + code, base_codes  # защита от циклов
    visited.add(code)

    ind = INDICATORS.get(code)
    if not ind:
        return "i" + code, base_codes

    if ind["type"] != "CALCULATED" or not ind["expr"]:
        base_codes.add(code)
        return "i" + code, base_codes

    expr = ind["expr"]
    # находим все коды вида iXX
    refs = re.findall(r"i(\d+)", expr)

    new_expr = expr
    for r in refs:
        sub_expr, base_codes = expand_formula(r, visited, base_codes)
        new_expr = new_expr.replace(f"i{r}", f"({sub_expr})")

    return new_expr, base_codes


def extract_codes_from_sql(sql_text):
    pattern = re.compile(r"JSON_BUILD_ARRAY\([^)]*'get-indicator-value'[^)]*'([0-9]+)'[^)]*\)")
    
    codes = pattern.findall(sql_text)
    return codes

def extract_other_codes_from_sql(sql_text):
    pattern = re.compile(r"AS\s+ind([0-9]+)")
    codes_used = pattern.findall(sql_text)
    return codes_used


def generate_sql_block(code):
    return f"""
    (
    SELECT CASE
    WHEN MAX(mi.type) = 1 THEN COALESCE(SUM(mm.value), 0)
    ELSE COALESCE(
    (ARRAY_AGG(mm.value ORDER BY mm.measure_date DESC))[1],
    0
    )
    END
    FROM monitoring.measure mm
    JOIN monitoring.indicator AS mi ON mi.id = mm.indicator_id
    WHERE mm.monitoring_object_id = mo.id
    AND mi.code = '{code}'
    AND (
    (mi.type = 1 AND EXTRACT(YEAR FROM mm.measure_date) = 2025)
    OR (mi.type = 2 AND EXTRACT(YEAR FROM mm.measure_date) <= 2025)
    )
    ) AS ind{code},
"""


# --- функция обновления SQL файлом ---
def update_sql_with_new_codes(sql_text, new_codes):
    # уже существующие коды в SQL
    existing_codes = extract_codes_from_sql(sql_text)

    missing_codes = [c for c in new_codes if c not in existing_codes]

    # раскрываем формулы для всех исходных кодов
    replacement_map = {}
    base_refs_map = {}
    for code in existing_codes:
        formula, base_codes = expand_formula(code)
        replacement_map[code] = formula
        base_refs_map[code] = base_codes
    used_codes = extract_other_codes_from_sql(sql_text)

    # заменяем JSON_BUILD_ARRAY на блоки
    def replacer_json(match):
        code = match.group(1)
        ans = []
        for base_code in base_refs_map[code]:
            if base_code not in used_codes:
                ans.append(generate_sql_block(base_code))
                used_codes.append(base_code)
        # for a in ans:
        #     print(a)
        return "\n".join(ans)

    sql_text = re.sub(r"JSON_BUILD_ARRAY\([^)]*'get-indicator-value'[^)]*'([0-9]+)'[^)]*\)\s+AS ind([0-9]+),", replacer_json, sql_text)

    for code, formula in replacement_map.items():
        if not formula:
            continue
        # заменяем iXXXXX на indXXXXX
        # print(formula)
        sql_formula = re.sub(r"i(\d+)", r"ind\1", formula)

        # делаем регексп для гибкого поиска
        pattern = re.compile(rf"ind{code}\s+AS\s+ind{code}", re.IGNORECASE)

        replacement = f"{sql_formula} AS ind{code}"

        # проверим, было ли совпадение
        if not pattern.search(sql_text):
            print(f"[WARN] Не найдено место для замены ind{code} AS ind{code}")
        else:
            sql_text = pattern.sub(replacement, sql_text)
            print(f"[OK] Заменено: ind{code} AS ind{code} -> {replacement}")



    SQL_QUERIES.append(sql_text)
    print(f". Заменены JSON функции на блоки. Обновлены агрегаты для кодов: {list(base_refs_map.keys())}.\n Добавлены новые блоки: {missing_codes}")


def main(inds_file, sql_file_input, sql_file_output):
    # --- загрузка XML ---
    tree = ET.parse(inds_file)
    root = tree.getroot()

    # --- словарь код -> данные индикатора ---
    for ind in root.findall(".//Indicator"):
        code = ind.get("code")
        type_ = ind.get("type")
        calc = ind.find("IndicatorCalculationParameter")
        expr = calc.get("expressionSource") if calc is not None else None
        INDICATORS[code] = {
            "type": type_,
            "expr": expr
        }

    # --- основной код ---
    with open(sql_file_input, encoding="utf-8") as f:
        sql_text = f.read()
    for query in sql_text.split('--NEXT_QUERY'):
        initial_codes = extract_codes_from_sql(query)
        # print(initial_codes)

        final_formulas = {}
        all_base_codes = set()

        for code in initial_codes:
            formula, base_codes = expand_formula(code)
            final_formulas[code] = formula
            all_base_codes.update(base_codes)

        print("Развёрнутые формулы:")
        for k, v in final_formulas.items():
            print(f"{k}: {v}")

        print("\nБазовые индикаторы:")
        print(sorted(all_base_codes))

        update_sql_with_new_codes(query, all_base_codes)
    with open(sql_file_output, "w", encoding="utf-8") as f:
        f.write("--NEXT_QUERY".join(SQL_QUERIES))
    # print([el for el in initial_codes if el in base_codes])