import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import random
import os


def task1():
    f_path = filedialog.asksaveasfilename(
        title="Сохранить файл f",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if not f_path:
        return

    count = simpledialog.askinteger("Количество чисел", "Сколько чисел записать в файл f?",
                                    minvalue=1, maxvalue=100000)
    if not count:
        return

    min_val = simpledialog.askinteger("Минимум", "Минимальное число?")
    max_val = simpledialog.askinteger("Максимум", "Максимальное число?")
    if min_val is None or max_val is None:
        return

    numbers = [random.randint(min_val, max_val) for _ in range(count)]

    with open(f_path, "w", encoding="utf-8") as f:
        f.write(" ".join(map(str, numbers)))

    seen = set()
    unique = []
    for n in numbers:
        if n not in seen:
            unique.append(n)
            seen.add(n)

    g_path = os.path.join(os.path.dirname(f_path), "g_unique.txt")

    with open(g_path, "w", encoding="utf-8") as g:
        g.write(" ".join(map(str, unique)))

    result_box.delete(0, tk.END)
    result_box.insert(tk.END, "Задание 1 выполнено!")
    result_box.insert(tk.END, f"Файл f создан: {f_path}")
    result_box.insert(tk.END, f"Файл g (без повторов): {g_path}")
    result_box.insert(tk.END, f"Чисел в f: {len(numbers)}, уникальных: {len(unique)}")


def task2():
    f_path = filedialog.asksaveasfilename(
        title="Сохранить файл f (для задачи 2)",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if not f_path:
        return

    count = simpledialog.askinteger("Количество чисел", "Сколько чисел записать в файл f?",
                                    minvalue=1, maxvalue=100000)
    t = simpledialog.askinteger("Значение T", "Введите T (делится на T)")
    c = simpledialog.askinteger("Значение C", "Введите C (НЕ делится на C)")
    min_val = simpledialog.askinteger("Минимум", "Минимальное число?")
    max_val = simpledialog.askinteger("Максимум", "Максимальное число?")

    if None in (count, t, c, min_val, max_val):
        return

    numbers = [random.randint(min_val, max_val) for _ in range(count)]

    with open(f_path, "w", encoding="utf-8") as f:
        f.write(" ".join(map(str, numbers)))

    filtered = [n for n in numbers if (n % t == 0) and (n % c != 0)]

    g_path = os.path.join(os.path.dirname(f_path), "g_filtered.txt")

    with open(g_path, "w", encoding="utf-8") as g:
        g.write(" ".join(map(str, filtered)))

    result_box.delete(0, tk.END)
    result_box.insert(tk.END, "Задание 2 выполнено!")
    result_box.insert(tk.END, f"Файл f создан: {f_path}")
    result_box.insert(tk.END, f"Файл g (делятся на {t} и не делятся на {c}): {g_path}")
    result_box.insert(tk.END, f"Всего чисел в f: {len(numbers)}")
    result_box.insert(tk.END, f"Подошло по условию: {len(filtered)}")


root = tk.Tk()
root.title("ПР №27 – Работа с файлами (Вариант 3)")
root.geometry("750x430")

title = tk.Label(
    root,
    text=("ПР №27: Работа с чтением и записью файлов\n"
          "Задание 1: Создать файл f случайных чисел → создать файл g без повторов.\n"
          "Задание 2: Создать файл f → получить g: числа делятся на T и не делятся на C."),
    font=("Arial", 12),
    justify="left"
)
title.pack(pady=10)

btn_frame = tk.Frame(root)
btn_frame.pack(pady=5)

btn1 = tk.Button(btn_frame, text="Задание 1", font=("Arial", 12), width=20, command=task1)
btn1.grid(row=0, column=0, padx=10)

btn2 = tk.Button(btn_frame, text="Задание 2", font=("Arial", 12), width=20, command=task2)
btn2.grid(row=0, column=1, padx=10)

result_box = tk.Listbox(root, width=100, height=14, font=("Arial", 10))
result_box.pack(pady=10)

root.mainloop()
