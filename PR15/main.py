import tkinter as tk
from tkinter import messagebox

def process():
    fio = entry.get().strip()
    if not fio:
        messagebox.showwarning("Ошибка", "Введите ФИО!")
        return

    length = len(fio)

    count_a = fio.lower().count('а')

    parts = fio.split()
    if len(parts) >= 1:
        surname = parts[0]
        reversed_surname = surname[::-1]
    else:
        reversed_surname = "Фамилия не указана"

    result = (
        f"Длина строки: {length}\n"
        f"Количество букв 'а': {count_a}\n"
        f"Фамилия в обратном порядке: {reversed_surname}"
    )
    messagebox.showinfo("Результат", result)


root = tk.Tk()
root.title("Анализ ФИО")
root.geometry("400x200")

label = tk.Label(root, text="Введите Фамилию, Имя, Отчество:")
label.pack(pady=10)

entry = tk.Entry(root, width=40)
entry.pack(pady=5)

button = tk.Button(root, text="Обработать", command=process)
button.pack(pady=10)

root.mainloop()
