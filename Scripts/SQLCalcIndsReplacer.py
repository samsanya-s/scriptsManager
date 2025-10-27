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
    refs = re.findall(r"i(\d+)", expr)

    new_expr = expr
    for r in refs:
        sub_expr, base_codes = expand_formula(r, visited, base_codes)
        new_expr = new_expr.replace(f"i{r}", f"({sub_expr})")

    return new_expr, base_codes


# --- парсер аргументов json_build_array ---
def split_sql_args(arg_str: str):
    args = []
    current = []
    depth = 0
    quote = None
    escape = False

    for ch in arg_str:
        if escape:
            current.append(ch)
            escape = False
            continue

        if ch == '\\':
            escape = True
            current.append(ch)
            continue

        if quote:
            current.append(ch)
            if ch == quote:
                quote = None
            continue

        if ch in ('"', "'"):
            quote = ch
            current.append(ch)
            continue

        if ch == '(':
            depth += 1
            current.append(ch)
            continue

        if ch == ')':
            depth -= 1
            current.append(ch)
            continue

        if ch == ',' and depth == 0 and not quote:
            arg = ''.join(current).strip()
            if arg:
                args.append(arg)
            current = []
            continue

        current.append(ch)

    if current:
        args.append(''.join(current).strip())

    return args


def extract_json_build_array_args(sql_text: str):
    results = []
    i = 0
    while True:
        match = re.search(r'json_build_array\s*\(', sql_text[i:], re.IGNORECASE)
        if not match:
            break
        start = i + match.end()
        depth = 1
        j = start
        while j < len(sql_text) and depth > 0:
            if sql_text[j] == '(':
                depth += 1
            elif sql_text[j] == ')':
                depth -= 1
            j += 1
        inner = sql_text[start:j-1]
        i = j
        args = split_sql_args(inner)
        if len(args) > 2:
            results.append(args[2:])  # берём аргументы начиная с третьего
        else:
            results.append([])
    return results


def extract_other_codes_from_sql(sql_text):
    return re.findall(r"AS\s+ind([0-9]+)", sql_text)


def generate_sql_block(codeOM, codeInd, periodStart, periodEnd):
    return f"monitoring.indicator_value_on_period_for_object({codeOM}, {codeInd}, {periodStart}, {periodEnd}),"


# --- обновление SQL ---
def update_sql_with_new_codes(sql_text, all_base_codes):
    # Все вызовы json_build_array
    array_args = extract_json_build_array_args(sql_text)

    # Соберём все коды из них (третий аргумент — это код индикатора)
    existing_codes = []
    for args in array_args:
        if len(args) >= 2:
            existing_codes.append(args[1].strip("'\""))

    missing_codes = [c for c in all_base_codes if c not in existing_codes]

    used_codes = extract_other_codes_from_sql(sql_text)

    # Заменяем json_build_array(...) AS indXXXX на развёрнутые блоки
    def replacer_json(match):
        code = match.group(1)
        ans = []
        for base_code in all_base_codes:
            if base_code not in used_codes:
                # возьмём последние 3 аргумента (om, start, end)
                args = array_args[0]
                if len(args) >= 3:
                    codeOM, periodStart, periodEnd = args[0], args[1], args[2]
                    ans.append(generate_sql_block(codeOM, base_code, periodStart, periodEnd))
                    used_codes.append(base_code)
        return "\n".join(ans)

    sql_text = re.sub(
        r"json_build_array\s*\([^)]*'get-indicator-value'[^)]*'([0-9]+)'[^)]*\)\s+AS\s+ind[0-9]+,",
        replacer_json,
        sql_text,
        flags=re.IGNORECASE
    )

    SQL_QUERIES.append(sql_text)
    print(f"[OK] Заменены JSON функции на блоки. Добавлены новые блоки для кодов: {missing_codes}")


# --- основной процесс ---
def main(inds_file, sql_file_input, sql_file_output):
    tree = ET.parse(inds_file)
    root = tree.getroot()

    for ind in root.findall(".//Indicator"):
        code = ind.get("code")
        type_ = ind.get("type")
        calc = ind.find("IndicatorCalculationParameter")
        expr = calc.get("expressionSource") if calc is not None else None
        INDICATORS[code] = {"type": type_, "expr": expr}

    with open(sql_file_input, encoding="utf-8") as f:
        sql_text = f.read()

    for query in sql_text.split('--NEXT_QUERY'):
        # Находим все json_build_array вызовы
        json_args = extract_json_build_array_args(query)
        initial_codes = []
        for args in json_args:
            if len(args) >= 2:
                code = re.sub(r"['\"]", "", args[1])
                initial_codes.append(code)

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
