import tkinter as tk
from tkinter import ttk, messagebox


def parse_matrix(text: str) -> list[list[int]]:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    if not lines:
        return []

    matrix = []
    n_cols = None
    for i, line in enumerate(lines, start=1):
        parts = line.replace(",", " ").split()
        if not parts:
            raise ValueError(f"Пустая строка #{i}")
        try:
            row = [int(p) for p in parts]
        except ValueError:
            raise ValueError(f"Строка #{i}: используйте целые числа")
        if n_cols is None:
            n_cols = len(row)
        elif len(row) != n_cols:
            raise ValueError(f"Строка #{i}: число столбцов {len(row)} не равно {n_cols}")
        matrix.append(row)
    return matrix


def col_maxima(matrix: list[list[int]]) -> list[int]:
    if not matrix:
        return []
    n_rows, n_cols = len(matrix), len(matrix[0])
    maxima = []
    for c in range(n_cols):
        m = matrix[0][c]
        for r in range(1, n_rows):
            if matrix[r][c] > m:
                m = matrix[r][c]
        maxima.append(m)
    return maxima


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Задание 13: Макс. по столбцам → минимальный из них")
        self.geometry("780x420")
        self.minsize(720, 380)

        root = ttk.Frame(self, padding=14)
        root.pack(fill="both", expand=True)


        ttk.Label(root, text="Матрица (по строке на строку, числа через пробел/запятую):").grid(row=1, column=0, sticky="w")
        self.txt_in = tk.Text(root, height=10, width=60, wrap="none")
        self.txt_in.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=(0, 8), pady=(4, 6))

        example = (
            "1  7  -3  4\n"
            "2  5   0  9\n"
            "8  1  12  3\n"
            "6  4   2  5"
        )
        self.txt_in.insert("1.0", example)

        btns = ttk.Frame(root)
        btns.grid(row=3, column=0, columnspan=2, sticky="w", pady=(2, 6))
        ttk.Button(btns, text="Вычислить", command=self.on_compute).pack(side="left")
        ttk.Button(btns, text="Очистить", command=self.on_clear).pack(side="left", padx=(8, 0))
        ttk.Button(btns, text="Выход", command=self.destroy).pack(side="left", padx=(8, 0))

        ttk.Label(root, text="Результат:").grid(row=1, column=2, sticky="w")
        self.txt_out = tk.Text(root, height=10, width=38, wrap="word", state="disabled")
        self.txt_out.grid(row=2, column=2, sticky="nsew", pady=(4, 6))

        self.status = ttk.Label(root, text="Подсказка: все строки должны иметь одинаковое число столбцов.", foreground="#666")
        self.status.grid(row=4, column=0, columnspan=3, sticky="w")

        root.columnconfigure(0, weight=3)
        root.columnconfigure(1, weight=0)
        root.columnconfigure(2, weight=2)
        root.rowconfigure(2, weight=1)

        self.bind("<Control-Return>", lambda e: self.on_compute())
        self.bind("<F5>", lambda e: self.on_compute())

        try:
            self.tk.call("tk", "scaling", 1.2)
        except Exception:
            pass

    def on_compute(self):
        text = self.txt_in.get("1.0", "end")
        try:
            matrix = parse_matrix(text)
            if not matrix:
                self._set_out("Матрица пуста.")
                return
            maxima = col_maxima(matrix)
            min_of_max = min(maxima) if maxima else None

            lines = [
                "Введённая матрица:",
                *["  " + " ".join(f"{x:>5}" for x in row) for row in matrix],
                "",
                f"Максимумы по столбцам: {maxima}",
                f"Минимальный из максимумов: {min_of_max}",
            ]
            self._set_out("\n".join(lines))
            self.status.configure(text=f"Размер матрицы: {len(matrix)}×{len(matrix[0])}. Всё хорошо ✅")
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e))
            self.status.configure(text="Ошибка: проверьте формат данных.")

    def on_clear(self):
        self.txt_in.delete("1.0", "end")
        self._set_out("")
        self.status.configure(text="")

    def _set_out(self, s: str):
        self.txt_out.configure(state="normal")
        self.txt_out.delete("1.0", "end")
        self.txt_out.insert("1.0", s)
        self.txt_out.configure(state="disabled")


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
