
"""
Script Manager — tkinter (OOП)
- Treeview с колонками: Название | Язык | Режим
- Фильтрация по столбцам и сортировка по клику на заголовок
- Модальный диалог добавления скрипта (с параметрами)
- Запуск скрипта: режим script (CLI args) или function (вызывает main в модуле через подпроцесс)
- Окно запуска содержит "консоль" с выводом процесса в реальном времени
"""

from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import os
import sys
import json
import threading
import uuid
import shlex

DB_FILE = "scripts.json"


# ----------------------------
# Утилиты
# ----------------------------
def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except Exception:
                return []
    return []


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ----------------------------
# Менеджер скриптов (логика)
# ----------------------------
class ScriptManager:
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file
        self.scripts = load_json(self.db_file)

    def save(self):
        save_json(self.db_file, self.scripts)

    def add_script(self, script_data):
        # script_data должен содержать: name, description, path, language, mode, params (list)
        # гарантируем уникальный id
        if "id" not in script_data:
            script_data["id"] = str(uuid.uuid4())
        self.scripts.append(script_data)
        self.save()

    def update_script(self, script_id, new_data):
        for i, s in enumerate(self.scripts):
            if s.get("id") == script_id:
                new_data["id"] = script_id
                self.scripts[i] = new_data
                self.save()
                return True
        return False

    def remove_script(self, script_id):
        self.scripts = [s for s in self.scripts if s.get("id") != script_id]
        self.save()

    def search(self, query="", search_name=True, search_desc=False, search_code=False):
        q = (query or "").lower().strip()
        if not q:
            return list(self.scripts)
        results = []
        for s in self.scripts:
            found = False
            if search_name and q in s.get("name", "").lower():
                found = True
            if search_desc and q in s.get("description", "").lower():
                found = True
            if search_code:
                try:
                    with open(s.get("path", ""), "r", encoding="utf-8") as f:
                        if q in f.read().lower():
                            found = True
                except Exception:
                    pass
            if found:
                results.append(s)
        return results


# ----------------------------
# Диалог добавления/редактирования скрипта
# ----------------------------
class AddScriptDialog(tk.Toplevel):
    def __init__(self, parent, manager: ScriptManager, refresh_callback, edit_script=None):
        """
        edit_script: если задан, то это dict с данными для редактирования (включая id)
        """
        super().__init__(parent)
        self.parent = parent
        self.manager = manager
        self.refresh_callback = refresh_callback
        self.edit_script = edit_script

        self.title("Добавить скрипт" if edit_script is None else "Редактировать скрипт")
        self.geometry("560x560")
        self.transient(parent)     # привязать к родителю
        # self.grab_set()            # модальное поведение
        # self.focus_force()
        self.focus()

        # поля
        self.name_var = tk.StringVar()
        self.path_var = tk.StringVar()
        self.language_var = tk.StringVar(value="python")
        self.mode_var = tk.StringVar(value="script")
        self.params = []  # список словарей {"name":..., "type":...}

        # если редактирование — заполняем
        if self.edit_script:
            self.name_var.set(self.edit_script.get("name", ""))
            self.path_var.set(self.edit_script.get("path", ""))
            self.language_var.set(self.edit_script.get("language", "python"))
            self.mode_var.set(self.edit_script.get("mode", "script"))
            self.params = list(self.edit_script.get("params", []))

        self._build_widgets()

    def _build_widgets(self):
        pad = {"padx": 6, "pady": 4}
        frm = ttk.Frame(self)
        frm.pack(fill=tk.BOTH, expand=True)

        # Название
        ttk.Label(frm, text="Название:").grid(row=0, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.name_var).grid(row=0, column=1, sticky="ew", columnspan=3, **pad)

        # Описание
        ttk.Label(frm, text="Описание:").grid(row=1, column=0, sticky="nw", **pad)
        self.desc_text = tk.Text(frm, height=4, wrap="word")
        self.desc_text.grid(row=1, column=1, columnspan=3, sticky="ew", **pad)
        if self.edit_script:
            self.desc_text.insert("1.0", self.edit_script.get("description", ""))

        # Файл
        ttk.Label(frm, text="Файл:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Entry(frm, textvariable=self.path_var).grid(row=2, column=1, sticky="ew", **pad)
        ttk.Button(frm, text="Выбрать", command=self._choose_file).grid(row=2, column=2, **pad)
        ttk.Button(frm, text="Создать новый", command=self._create_file).grid(row=2, column=3, **pad)

        # Язык и режим
        ttk.Label(frm, text="Язык:").grid(row=3, column=0, sticky="w", **pad)
        ttk.OptionMenu(frm, self.language_var, self.language_var.get(), "python", "bash", "powershell").grid(row=3, column=1, sticky="w", **pad)

        ttk.Label(frm, text="Режим:").grid(row=3, column=2, sticky="w", **pad)
        ttk.OptionMenu(frm, self.mode_var, self.mode_var.get(), "script", "function").grid(row=3, column=3, sticky="w", **pad)

        # Параметры (Listbox + кнопки)
        ttk.Label(frm, text="Параметры:").grid(row=4, column=0, sticky="nw", **pad)
        self.params_box = tk.Listbox(frm, height=8)
        self.params_box.grid(row=4, column=1, columnspan=3, sticky="nsew", **pad)

        # заполнить существующие параметры (если есть)
        for p in self.params:
            self.params_box.insert(tk.END, f"{p.get('name')} ({p.get('type')})")

        pbtn_frm = ttk.Frame(frm)
        pbtn_frm.grid(row=5, column=1, columnspan=3, sticky="w", **pad)
        ttk.Button(pbtn_frm, text="Добавить параметр", command=self._param_add).pack(side=tk.LEFT, padx=4)
        ttk.Button(pbtn_frm, text="Редактировать", command=self._param_edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(pbtn_frm, text="Удалить", command=self._param_delete).pack(side=tk.LEFT, padx=4)

        # spacer
        frm.rowconfigure(4, weight=1)
        frm.columnconfigure(1, weight=1)

        # Кнопки сохранить/отмена
        btn_frm = ttk.Frame(self)
        btn_frm.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(btn_frm, text="Сохранить", command=self._save).pack(side=tk.RIGHT, padx=6)
        ttk.Button(btn_frm, text="Отмена", command=self._close).pack(side=tk.RIGHT)

    def _choose_file(self):
        # Открываем системный диалог; после закрытия поднимаем наше окно поверх
        filepath = filedialog.askopenfilename(filetypes=[("Python files", "*.py"), ("All files", "*.*")])
        if filepath:
            self.path_var.set(filepath)
        # Важно: вернуть фокус на диалог, чтобы главное окно не "перекрывало"
        # try:
        #     self.lift()
        #     self.focus_force()
        #     self.grab_set()
        # except Exception:
        #     pass

    def _create_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".py", filetypes=[("Python files", "*.py")])
        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# Новый скрипт\n")
            self.path_var.set(filepath)
        # try:
        #     self.lift()
        #     self.focus_force()
        #     self.grab_set()
        # except Exception:
        #     pass

    def _param_add(self):
        ParamDialog(self, on_save=self._param_add_save)

    def _param_add_save(self, param):
        # param = {"name":..., "type":...}
        self.params.append(param)
        self.params_box.insert(tk.END, f"{param['name']} ({param['type']})")

    def _param_edit(self):
        sel = self.params_box.curselection()
        if not sel:
            return
        idx = sel[0]
        param = self.params[idx]
        ParamDialog(self, edit=param, on_save=lambda p: self._param_edit_save(idx, p))

    def _param_edit_save(self, idx, new_param):
        self.params[idx] = new_param
        self.params_box.delete(idx)
        self.params_box.insert(idx, f"{new_param['name']} ({new_param['type']})")

    def _param_delete(self):
        sel = self.params_box.curselection()
        if not sel:
            return
        idx = sel[0]
        self.params_box.delete(idx)
        self.params.pop(idx)

    def _save(self):
        name = self.name_var.get().strip()
        path = self.path_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        language = self.language_var.get()
        mode = self.mode_var.get()
        params = self.params

        if not name:
            messagebox.showerror("Ошибка", "Укажите название скрипта")
            return
        if not path:
            messagebox.showerror("Ошибка", "Укажите файл скрипта")
            return
        # Если редактирование — обновляем, иначе добавляем
        data = {
            "name": name,
            "description": description,
            "path": path,
            "language": language,
            "mode": mode,
            "params": params
        }
        if self.edit_script:
            self.manager.update_script(self.edit_script.get("id"), data)
        else:
            self.manager.add_script(data)
        self.refresh_callback()
        self._close()

    def _close(self):
        # try:
        #     self.grab_release()
        # except Exception:
        #     pass
        self.destroy()


# ----------------------------
# Диалог управления параметром (добавление/редактирование)
# ----------------------------
class ParamDialog(tk.Toplevel):
    def __init__(self, parent, on_save=None, edit=None):
        super().__init__(parent)
        self.parent = parent
        self.on_save = on_save
        self.edit = edit
        self.title("Параметр")
        self.geometry("340x180")
        self.transient(parent)
        # self.grab_set()
        # self.focus_force()
        self.focus()

        self.name_var = tk.StringVar(value=edit.get("name") if edit else "")
        self.type_var = tk.StringVar(value=edit.get("type") if edit else "строка")

        ttk.Label(self, text="Имя параметра:").pack(anchor="w", padx=6, pady=4)
        ttk.Entry(self, textvariable=self.name_var).pack(fill=tk.X, padx=6)

        ttk.Label(self, text="Тип:").pack(anchor="w", padx=6, pady=4)
        ttk.OptionMenu(self, self.type_var, self.type_var.get(), "строка", "число", "список строк", "список чисел", "файловый путь", "путь до директории").pack(fill=tk.X, padx=6)

        btn_frm = ttk.Frame(self)
        btn_frm.pack(fill=tk.X, pady=8, padx=6)
        ttk.Button(btn_frm, text="Сохранить", command=self._save).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_frm, text="Отмена", command=self._cancel).pack(side=tk.RIGHT)

    def _save(self):
        name = self.name_var.get().strip()
        ptype = self.type_var.get()
        if not name:
            messagebox.showerror("Ошибка", "Имя параметра не может быть пустым")
            return
        param = {"name": name, "type": ptype}
        if self.on_save:
            self.on_save(param)
        # try:
        #     self.grab_release()
        # except Exception:
        #     pass
        self.destroy()

    def _cancel(self):
        # try:
        #     self.grab_release()
        # except Exception:
        #     pass
        self.destroy()


# ----------------------------
# Диалог запуска: ввод параметров + встроенная консоль (stdout/stderr)
# ----------------------------
class RunDialog(tk.Toplevel):
    def __init__(self, parent, script):
        super().__init__(parent)
        self.parent = parent
        self.script = script
        self.title(f"Запуск: {script.get('name')}")
        self.geometry("800x500")
        self.transient(parent)
        # self.grab_set()
        # self.focus_force()
        self.focus()

        self.entries = {}  # name -> (widget, type)
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": 6, "pady": 4}
        top_fr = ttk.Frame(self)
        top_fr.pack(fill=tk.X, padx=6, pady=6)

        # Создаем поля для параметров
        params = self.script.get("params", [])
        for i, p in enumerate(params):
            ttk.Label(top_fr, text=f"{p['name']} ({p['type']}):").grid(row=i, column=0, sticky="w", **pad)
            ent = ttk.Entry(top_fr)
            ent.grid(row=i, column=1, sticky="ew", **pad)
            top_fr.columnconfigure(1, weight=1)
            # для файловых путей добавим кнопку выбора
            if p["type"] == "файловый путь":
                def _choose(e=ent):
                    fp = filedialog.askopenfilename()
                    if fp:
                        e.delete(0, tk.END)
                        e.insert(0, fp)
                        # try:
                        #     self.lift()
                        #     self.focus_force()
                        #     self.grab_set()
                        # except Exception:
                        #     pass
                ttk.Button(top_fr, text="...", width=3, command=_choose).grid(row=i, column=2, **pad)
            elif p["type"] == "путь до директории":
                def _choose(e=ent):
                    fp = filedialog.askdirectory()
                    if fp:
                        e.delete(0, tk.END)
                        e.insert(0, fp)
                        # try:
                        #     self.lift()
                        #     self.focus_force()
                        #     self.grab_set()
                        # except Exception:
                        #     pass
                ttk.Button(top_fr, text="...", width=3, command=_choose).grid(row=i, column=2, **pad)
            self.entries[p["name"]] = (ent, p["type"])

        # Кнопки
        btn_fr = ttk.Frame(self)
        btn_fr.pack(fill=tk.X, padx=6, pady=4)
        ttk.Button(btn_fr, text="Запустить", command=self._on_run).pack(side=tk.RIGHT, padx=4)
        ttk.Button(btn_fr, text="Закрыть", command=self._on_close).pack(side=tk.RIGHT)

        # Консоль (Text)
        lbl = ttk.Label(self, text="Консоль (stdout/stderr):")
        lbl.pack(anchor="w", padx=6)
        self.console = tk.Text(self, height=18, wrap="none", state="disabled")
        self.console.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        # добавим вертикальный скроллбар
        sb = ttk.Scrollbar(self, orient="vertical", command=self.console.yview)
        self.console.configure(yscrollcommand=sb.set)
        sb.place(in_=self.console, relx=1.0, rely=0, relheight=1.0, anchor="ne")

    def _append_console(self, text):
        self.console.configure(state="normal")
        self.console.insert(tk.END, text)
        self.console.see(tk.END)
        self.console.configure(state="disabled")

    def _on_run(self):
        # собираем аргументы в зависимости от типа и режима
        args_raw = {}
        for name, (widget, ptype) in self.entries.items():
            v = widget.get().strip()
            args_raw[name] = (v, ptype)

        # преобразуем в аргументы для script (cli) или для function (будем передавать JSON)
        mode = self.script.get("mode", "script")
        language = self.script.get("language", "python")
        path = self.script.get("path")

        # Формируем команду
        if mode == "script":
            # пример: python path/to/test.py --param1 value1 --list paramA,paramB
            cmd = []
            if language == "python":
                cmd.append(sys.executable)
                cmd.append(path)
            elif language == "bash":
                cmd.append("bash")
                cmd.append(path)
            elif language == "powershell":
                cmd = ["powershell", "-File", path]
            else:
                messagebox.showerror("Ошибка", f"Неизвестный язык: {language}")
                return

            # добавляем параметры как --name value
            for name, (val, ptype) in args_raw.items():
                if val == "":
                    continue
                cli_name = f"--{name}"
                if ptype == "число":
                    try:
                        _ = float(val)  # проверка
                        cmd.append(cli_name)
                        cmd.append(str(val))
                    except Exception:
                        messagebox.showerror("Ошибка", f"Параметр {name} должен быть числом")
                        return
                elif ptype == "список чисел":
                    parts = [p.strip() for p in val.split(",") if p.strip() != ""]
                    try:
                        parts = [str(float(p)) for p in parts]
                    except Exception:
                        messagebox.showerror("Ошибка", f"Параметр {name} должен быть списком чисел через запятую")
                        return
                    cmd.append(cli_name)
                    # передадим как запятую-список
                    cmd.append(",".join(parts))
                elif ptype == "список строк":
                    parts = [p.strip() for p in val.split(",") if p.strip() != ""]
                    cmd.append(cli_name)
                    cmd.append(",".join(parts))
                else:  # строка, путь до директории или файловый путь
                    cmd.append(cli_name)
                    cmd.append(val)
            # Запускаем подпроцесс и ведём вывод
            self._run_subprocess(cmd)

        elif mode == "function":
            # Будем запустить подпроцесс python, который импортирует модуль и вызовет main(args...)
            # Для передачи аргументов используем JSON, чтобы корректно пробросить списки/числа/строки.
            import json as _json
            parsed_args = []
            for name, (val, ptype) in args_raw.items():
                if ptype == "число":
                    if val == "":
                        parsed_args.append(None)
                    else:
                        try:
                            if "." in val:
                                parsed_args.append(float(val))
                            else:
                                parsed_args.append(int(val))
                        except Exception:
                            messagebox.showerror("Ошибка", f"Параметр {name} должен быть числом")
                            return
                elif ptype == "список чисел":
                    if val == "":
                        parsed_args.append([])
                    else:
                        parts = [p.strip() for p in val.split(",") if p.strip() != ""]
                        try:
                            nums = [float(p) if "." in p else int(p) for p in parts]
                        except Exception:
                            messagebox.showerror("Ошибка", f"{name}: список чисел должен быть через запятую")
                            return
                        parsed_args.append(nums)
                elif ptype == "список строк":
                    if val == "":
                        parsed_args.append([])
                    else:
                        parsed_args.append([p.strip() for p in val.split(",") if p.strip() != ""])
                else:
                    parsed_args.append(val)

            # Упакуем parsed_args в JSON и передадим как единый аргумент
            json_args = json.dumps(parsed_args, ensure_ascii=False)
            # Команда будет: python -c "import importlib.util,sys,json; ... " "<json_args>"
            # Соберём команду аккуратно
            if language != "python":
                messagebox.showerror("Ошибка", "Режим function поддерживается только для python-скриптов")
                return

            # конструируем однострочник python, который импортирует модуль по пути и вызовет main(*args)
            # использование repr(json_args) чтобы корректно передать через argv
            wrapper_code = (
                "import importlib.util,sys,json\n"
                "args_json=sys.argv[1]\n"
                "args=json.loads(args_json)\n"
                "spec=importlib.util.spec_from_file_location('user_module', r'''%s''')\n"
                "m=importlib.util.module_from_spec(spec)\n"
                "spec.loader.exec_module(m)\n"
                "if hasattr(m,'main'):\n"
                "    try:\n"
                "        res=m.main(*args)\n"
                "        if res is not None:\n"
                "            print(res)\n"
                "    except Exception as e:\n"
                "        import traceback\n"
                "        traceback.print_exc()\n"
                "else:\n"
                "    print('Module has no main(*args)')\n"
            ) % path

            cmd = [sys.executable, "-c", wrapper_code, json_args]
            self._run_subprocess(cmd)

        else:
            messagebox.showerror("Ошибка", f"Неизвестный режим: {mode}")

    def _run_subprocess(self, cmd):
        # Запускаем процесс и читаем stdout/stderr в поток
        self._append_console(f"Запускаю: {' '.join(shlex.quote(c) for c in cmd)}\n\n")
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        except Exception as e:
            messagebox.showerror("Ошибка запуска", str(e))
            return

        def reader_thread():
            try:
                for line in proc.stdout:
                    self._append_console(line)
            except Exception as e:
                self._append_console(f"\n[Ошибка чтения вывода процесса: {e}]\n")
            finally:
                proc.wait()
                self._append_console(f"\n[Процесс завершился с кодом {proc.returncode}]\n")

        t = threading.Thread(target=reader_thread, daemon=True)
        t.start()

    def _on_close(self):
        # try:
        #     self.grab_release()
        # except Exception:
        #     pass
        self.destroy()


# ----------------------------
# Основное приложение
# ----------------------------
class ScriptApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Script Manager")
        self.root.geometry("1100x700")

        self.manager = ScriptManager()

        # переменные поиска
        self.search_var = tk.StringVar()
        self.chk_name_var = tk.BooleanVar(value=True)
        self.chk_desc_var = tk.BooleanVar(value=False)
        self.chk_code_var = tk.BooleanVar(value=False)

        # фильтры по колонкам
        self.filter_name = tk.StringVar()
        self.filter_lang = tk.StringVar()
        self.filter_mode = tk.StringVar()

        # порядок сортировки: column -> (asc True/False)
        self.sort_state = {"column": None, "asc": True}

        self._build_ui()
        self.refresh_list()

    def _build_ui(self):
        # grid layout — верх поиск (60%), низ таблица/preview (40%)
        self.root.rowconfigure(0, weight=3)  # поиск area (включает фильтры)
        self.root.rowconfigure(1, weight=5)  # таблица + preview
        self.root.rowconfigure(2, weight=0)  # кнопки
        self.root.columnconfigure(0, weight=1)

        # --- Поиск и чекбоксы ---
        search_frame = ttk.Frame(self.root)
        search_frame.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Поиск:").grid(row=0, column=0, sticky="w")
        ttk.Entry(search_frame, textvariable=self.search_var).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(search_frame, text="Поиск", command=self.refresh_list).grid(row=0, column=2, padx=4)

        ttk.Checkbutton(search_frame, text="Название", variable=self.chk_name_var).grid(row=1, column=0, sticky="w", pady=4)
        ttk.Checkbutton(search_frame, text="Описание", variable=self.chk_desc_var).grid(row=1, column=1, sticky="w", pady=4)
        ttk.Checkbutton(search_frame, text="Код", variable=self.chk_code_var).grid(row=1, column=2, sticky="w", pady=4)

        # фильтры по столбцам (Name, Lang, Mode)
        filt_fr = ttk.Frame(search_frame)
        filt_fr.grid(row=2, column=0, columnspan=3, sticky="ew", pady=6)
        filt_fr.columnconfigure(1, weight=1)
        ttk.Label(filt_fr, text="Фильтр по названию:").grid(row=0, column=0, sticky="w")
        ttk.Entry(filt_fr, textvariable=self.filter_name).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Label(filt_fr, text="Язык:").grid(row=0, column=2, sticky="w", padx=(8,0))
        ttk.Entry(filt_fr, textvariable=self.filter_lang, width=12).grid(row=0, column=3, sticky="w")
        ttk.Label(filt_fr, text="Режим:").grid(row=0, column=4, sticky="w", padx=(8,0))
        ttk.Entry(filt_fr, textvariable=self.filter_mode, width=12).grid(row=0, column=5, sticky="w", padx=(0,8))
        ttk.Button(filt_fr, text="Применить фильтры", command=self.refresh_list).grid(row=0, column=6, padx=4)

        # --- Таблица (Treeview) ---
        table_fr = ttk.Frame(self.root)
        table_fr.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0,6))
        table_fr.rowconfigure(1, weight=1)
        table_fr.columnconfigure(0, weight=1)

        columns = ("name", "lang", "mode")
        self.tree = ttk.Treeview(table_fr, columns=columns, show="headings", selectmode="browse")
        self.tree.grid(row=1, column=0, sticky="nsew")

        # Заголовки
        self.tree.heading("name", text="Название", command=lambda: self._sort_by("name"))
        self.tree.heading("lang", text="Язык", command=lambda: self._sort_by("lang"))
        self.tree.heading("mode", text="Режим", command=lambda: self._sort_by("mode"))

        # Колонки
        self.tree.column("name", width=420, anchor="w")
        self.tree.column("lang", width=120, anchor="center")
        self.tree.column("mode", width=120, anchor="center")

        # scrollbar
        vsb = ttk.Scrollbar(table_fr, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=1, column=1, sticky="ns")

        # двоичный клик — редактирование
        self.tree.bind("<Double-1>", self._on_tree_double_click)
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Описание + предпросмотр
        bottom_fr = ttk.Frame(table_fr)
        bottom_fr.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(8,0))
        bottom_fr.columnconfigure(0, weight=1)
        ttk.Label(bottom_fr, text="Описание:").grid(row=0, column=0, sticky="w")
        self.desc_var = tk.StringVar()
        ttk.Label(bottom_fr, textvariable=self.desc_var, wraplength=1000, justify="left").grid(row=1, column=0, sticky="w", pady=(2,8))

        ttk.Label(bottom_fr, text="Предпросмотр кода:").grid(row=2, column=0, sticky="w")
        self.preview = tk.Text(bottom_fr, height=14, wrap="none")
        self.preview.grid(row=3, column=0, sticky="nsew", pady=(2,2))
        bottom_fr.rowconfigure(3, weight=1)

        vsb2 = ttk.Scrollbar(bottom_fr, orient="vertical", command=self.preview.yview)
        self.preview.configure(yscrollcommand=vsb2.set)
        vsb2.grid(row=3, column=1, sticky="ns")

        # --- Кнопки управления ---
        btn_fr = ttk.Frame(self.root)
        btn_fr.grid(row=2, column=0, sticky="ew", padx=6, pady=6)
        ttk.Button(btn_fr, text="Добавить", command=self._open_add).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_fr, text="Редактировать", command=self._open_edit).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_fr, text="Удалить", command=self._delete_selected).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_fr, text="Открыть в редакторе", command=self._open_editor).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_fr, text="Запустить", command=self._open_run).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_fr, text="Обновить", command=self.refresh_list).pack(side=tk.RIGHT, padx=4)

    def refresh_list(self):
        # очистка
        for row in self.tree.get_children():
            self.tree.delete(row)

        # поиск
        q = self.search_var.get().strip()
        scripts = self.manager.search(q, search_name=self.chk_name_var.get(),
                                      search_desc=self.chk_desc_var.get(),
                                      search_code=self.chk_code_var.get())

        # фильтрация по колонкам (если заданы)
        fname = self.filter_name.get().strip().lower()
        flang = self.filter_lang.get().strip().lower()
        fmode = self.filter_mode.get().strip().lower()

        filtered = []
        for s in scripts:
            if fname and fname not in s.get("name", "").lower():
                continue
            if flang and flang not in s.get("language", "").lower():
                continue
            if fmode and fmode not in s.get("mode", "").lower():
                continue
            filtered.append(s)

        # сортировка
        col = self.sort_state["column"]
        asc = self.sort_state["asc"]
        if col:
            filtered.sort(key=lambda x: (x.get(col) or "").lower(), reverse=not asc)

        # вставляем
        for s in filtered:
            iid = s.get("id") or s.get("name")
            # values порядок соответствует columns ("name","lang","mode")
            self.tree.insert("", tk.END, iid=iid, values=(s.get("name"), s.get("language", "python"), s.get("mode", "script")))

        # очищаем preview/desc
        self.desc_var.set("")
        self.preview.delete("1.0", tk.END)

    def _sort_by(self, column):
        if self.sort_state["column"] == column:
            self.sort_state["asc"] = not self.sort_state["asc"]
        else:
            self.sort_state["column"] = column
            self.sort_state["asc"] = True
        self.refresh_list()

    def _get_selected_script(self):
        sel = self.tree.selection()
        if not sel:
            return None
        iid = sel[0]
        for s in self.manager.scripts:
            if s.get("id") == iid or s.get("name") == iid:
                return s
        return None

    def _on_tree_select(self, event):
        s = self._get_selected_script()
        if not s:
            return
        self.desc_var.set(s.get("description", ""))
        # preview
        self.preview.delete("1.0", tk.END)
        try:
            with open(s.get("path", ""), "r", encoding="utf-8") as f:
                self.preview.insert("1.0", f.read())
        except Exception as e:
            self.preview.insert("1.0", f"[Ошибка чтения файла: {e}]")

    def _on_tree_double_click(self, event):
        # откроем редактирование
        self._open_edit()

    def _open_add(self):
        AddScriptDialog(self.root, self.manager, self.refresh_list)

    def _open_edit(self):
        s = self._get_selected_script()
        if not s:
            messagebox.showinfo("Редактировать", "Выберите скрипт для редактирования")
            return
        AddScriptDialog(self.root, self.manager, self.refresh_list, edit_script=s)

    def _delete_selected(self):
        s = self._get_selected_script()
        if not s:
            messagebox.showinfo("Удалить", "Выберите скрипт для удаления")
            return
        if not messagebox.askyesno("Подтвердите", f"Удалить скрипт '{s.get('name')}'?"):
            return
        self.manager.remove_script(s.get("id"))
        self.refresh_list()

    def _open_editor(self):
        s = self._get_selected_script()
        if not s:
            messagebox.showinfo("Открыть", "Выберите скрипт")
            return
        path = s.get("path")
        try:
            if sys.platform.startswith("win"):
                current_dir = Path(__file__).resolve().parent
                os.startfile(current_dir / path)
            elif sys.platform == "darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{e}")

    def _open_run(self):
        s = self._get_selected_script()
        if not s:
            messagebox.showinfo("Запуск", "Выберите скрипт")
            return
        RunDialog(self.root, s)


# ----------------------------
# Запуск приложения
# ----------------------------
def main():
    root = tk.Tk()
    app = ScriptApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
