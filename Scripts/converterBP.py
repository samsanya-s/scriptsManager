import re
import json
import os

REPLACEMENTS_FILE = r"C:\Users\a.medvedev\Documents\projects\managerScripts\scriptsManager\Scripts\replacements.json"
input_file = r"C:\Users\a.medvedev\Documents\code\Добавить данные по Допланированию для Цифрового паспорта региона.bpmn"
output_file = r"C:\Users\a.medvedev\Documents\code\Добавить данные по Допланированию для Цифрового паспорта региона3.bpmn"


def load_replacements():
    if os.path.exists(REPLACEMENTS_FILE):
        with open(REPLACEMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_replacements(replacements):
    with open(REPLACEMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(replacements, f, ensure_ascii=False, indent=4)


def replace_blocks(text, replacements):
    # Находим все {{...}}
    blocks = re.findall(r"(\{\{.*?\}\})", text)

    for block in blocks:
        replaced = False

        # Проверяем все правила из JSON
        for pattern, repl in replacements.items():
            if re.search(pattern, block):
                text = re.sub(pattern, repl, text)
                replaced = True
                break

        # Если замены нет — спросим у пользователя
        if not replaced:
            print(f"Неизвестный блок: {block}")
            # new_repl = input("Введите замену (можно использовать группы вида \\1, \\2): ")
            # pattern = input("Введите regex-шаблон для этого блока (Enter для точного совпадения): ")
            # if not pattern.strip():
            #     pattern = re.escape(block)  # если regex не указан — точное совпадение
            # replacements[pattern] = new_repl
            # text = re.sub(pattern, new_repl, text)
            # save_replacements(replacements)

    return text, replacements


def main(input_file, output_file):
    # Загружаем заменители
    replacements = load_replacements()

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Производим замену
    new_text, replacements = replace_blocks(text, replacements)

    # Сохраняем результат
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(new_text)

    # Обновляем JSON


    print("Готово! Результат сохранён в", output_file)


if __name__ == "__main__":
    main(None, None)
