#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Справочник меломана — консольное приложение на Python.
Обязательный функционал:
  - добавление записи (задачи/элемента)
  - вывод на экран
  - удаление из списка

Дополнительные возможности:
  - редактирование записи
  - поиск/фильтрация/сортировка
  - оценка и рекомендации "Что послушать?"
  - статистика по жанрам и годам
  - автосохранение/загрузка (JSON), импорт/экспорт CSV
  - валидация полей и красивое табличное отображение
"""
from __future__ import annotations

import csv
import json
import os
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import List, Dict, Optional

DATA_FILE = "melomaniac_data.json"

# --------------------------- Модель ---------------------------

@dataclass
class MusicEntry:
    id: int
    artist: str
    album: str
    genre: str
    year: int
    rating: Optional[int] = None  # 1..10
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict) -> "MusicEntry":
        return MusicEntry(
            id=int(d["id"]),
            artist=str(d["artist"]),
            album=str(d["album"]),
            genre=str(d["genre"]),
            year=int(d["year"]),
            rating=None if d.get("rating") in (None, "", "None") else int(d["rating"]),
            notes=str(d.get("notes", "")),
            created_at=str(d.get("created_at", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
        )


# --------------------------- Хранилище ---------------------------

class MusicDirectory:
    def __init__(self, path: str = DATA_FILE):
        self.path = path
        self.entries: List[MusicEntry] = []
        self._next_id = 1
        self.load()

    # --- CRUD ---
    def add_entry(self, artist: str, album: str, genre: str, year: int, rating: Optional[int] = None, notes: str = "") -> MusicEntry:
        self._validate(artist, album, genre, year, rating)
        entry = MusicEntry(id=self._next_id, artist=artist.strip(), album=album.strip(), genre=genre.strip(), year=int(year), rating=rating, notes=notes.strip())
        self.entries.append(entry)
        self._next_id += 1
        self.save()
        return entry

    def list_entries(self, sort_by: str = "id", reverse: bool = False, filter_by: Optional[Dict] = None) -> List[MusicEntry]:
        data = self.entries[:]
        if filter_by:
            def pred(e: MusicEntry) -> bool:
                ok = True
                for k, v in filter_by.items():
                    if v is None or v == "":
                        continue
                    attr = getattr(e, k, None)
                    if attr is None:
                        ok = False
                        break
                    if isinstance(attr, str):
                        ok = ok and v.lower() in attr.lower()
                    else:
                        ok = ok and str(v).lower() in str(attr).lower()
                return ok
            data = [e for e in data if pred(e)]
        if sort_by not in MusicEntry.__dataclass_fields__:
            sort_by = "id"
        data.sort(key=lambda x: getattr(x, sort_by), reverse=reverse)
        return data

    def delete_entry(self, entry_id: int) -> bool:
        for i, e in enumerate(self.entries):
            if e.id == entry_id:
                del self.entries[i]
                self.save()
                return True
        return False

    def edit_entry(self, entry_id: int, **updates) -> bool:
        e = self.get(entry_id)
        if not e:
            return False
        # Prepare new values for validation
        artist = updates.get("artist", e.artist)
        album = updates.get("album", e.album)
        genre = updates.get("genre", e.genre)
        year = int(updates.get("year", e.year))
        rating = updates.get("rating", e.rating)
        notes = updates.get("notes", e.notes)
        self._validate(artist, album, genre, year, rating)
        e.artist, e.album, e.genre, e.year, e.rating, e.notes = artist.strip(), album.strip(), genre.strip(), year, rating, notes.strip()
        self.save()
        return True

    def get(self, entry_id: int) -> Optional[MusicEntry]:
        return next((e for e in self.entries if e.id == entry_id), None)

    # --- Persistence ---
    def load(self) -> None:
        if not os.path.exists(self.path):
            self.entries = []
            self._next_id = 1
            return
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.entries = [MusicEntry.from_dict(d) for d in raw.get("entries", [])]
            if self.entries:
                self._next_id = max(e.id for e in self.entries) + 1
            else:
                self._next_id = 1
        except Exception as ex:
            print(f"Не удалось загрузить данные: {ex}")
            self.entries = []
            self._next_id = 1

    def save(self) -> None:
        payload = {"entries": [e.to_dict() for e in self.entries]}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    # --- CSV ---
    def export_csv(self, csv_path: str) -> None:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["id", "artist", "album", "genre", "year", "rating", "notes", "created_at"])
            for e in self.entries:
                writer.writerow([e.id, e.artist, e.album, e.genre, e.year, e.rating if e.rating is not None else "", e.notes, e.created_at])

    def import_csv(self, csv_path: str) -> int:
        if not os.path.exists(csv_path):
            raise FileNotFoundError("CSV файл не найден")
        added = 0
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                try:
                    self.add_entry(
                        artist=row.get("artist", ""),
                        album=row.get("album", ""),
                        genre=row.get("genre", ""),
                        year=int(row.get("year", 0)),
                        rating=int(row["rating"]) if row.get("rating") not in (None, "", "None") else None,
                        notes=row.get("notes", ""),
                    )
                    added += 1
                except Exception as ex:
                    print(f"Строка пропущена ({ex}): {row}")
        return added

    # --- Доп. возможности ---
    def recommend(self) -> Optional[MusicEntry]:
        """Простая рекомендация: лучшая оценка, затем самый свежий."""
        if not self.entries:
            return None
        return sorted(self.entries, key=lambda e: (-(e.rating or 0), -e.year, e.artist.lower()))[0]

    def stats_by_genre(self) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for e in self.entries:
            result[e.genre] = result.get(e.genre, 0) + 1
        return dict(sorted(result.items(), key=lambda kv: (-kv[1], kv[0].lower())))

    # --- Валидация ---
    @staticmethod
    def _validate(artist: str, album: str, genre: str, year: int, rating: Optional[int]) -> None:
        year = int(year)
        if not artist.strip():
            raise ValueError("Поле 'Исполнитель' обязательно")
        if not album.strip():
            raise ValueError("Поле 'Альбом' обязательно")
        if not genre.strip():
            raise ValueError("Поле 'Жанр' обязательно")
        if year < 1900 or year > datetime.now().year + 1:
            raise ValueError("Год должен быть в разумных пределах (>=1900 и не в далеком будущем)")
        if rating is not None:
            rating = int(rating)
            if not 1 <= rating <= 10:
                raise ValueError("Оценка должна быть от 1 до 10")

# --------------------------- Представление (CLI) ---------------------------

def print_table(entries: List[MusicEntry]) -> None:
    if not entries:
        print("Записей нет.")
        return
    cols = ["ID", "Исполнитель", "Альбом", "Жанр", "Год", "Оценка", "Заметки"]
    rows = []
    for e in entries:
        rows.append([e.id, e.artist, e.album, e.genre, e.year, e.rating if e.rating is not None else "-", (e.notes or "-")])
    widths = [len(c) for c in cols]
    for r in rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(str(cell)))
    # header
    line = " | ".join(str(c).ljust(widths[i]) for i, c in enumerate(cols))
    sep = "-+-".join("-" * widths[i] for i in range(len(cols)))
    print(line)
    print(sep)
    # body
    for r in rows:
        print(" | ".join(str(cell).ljust(widths[i]) for i, cell in enumerate(r)))

def prompt_int(msg: str, allow_empty: bool = False) -> Optional[int]:
    while True:
        s = input(msg).strip()
        if allow_empty and s == "":
            return None
        try:
            return int(s)
        except ValueError:
            print("Введите целое число.")

def menu():
    directory = MusicDirectory()

    actions = {
        "1": ("Добавить запись", action_add),
        "2": ("Показать записи", action_list),
        "3": ("Удалить запись", action_delete),
        "4": ("Редактировать запись", action_edit),
        "5": ("Поиск/фильтр", action_search),
        "6": ("Сортировка", action_sort),
        "7": ("Экспорт CSV", action_export),
        "8": ("Импорт CSV", action_import),
        "9": ("Рекомендация: что послушать?", action_recommend),
        "10": ("Статистика по жанрам", action_stats),
        "0": ("Выход", None),
    }

    while True:
        print("\n=== Справочник меломана ===")
        for k, (title, _) in actions.items():
            print(f"{k}. {title}")
        choice = input("Выберите действие: ").strip()
        if choice == "0":
            print("До встречи!")
            break
        action = actions.get(choice)
        if action is None:
            print("Неизвестный пункт меню.")
            continue
        try:
            action[1](directory)
        except Exception as ex:
            print(f"Ошибка: {ex}")

# --------------------------- Действия ---------------------------

def action_add(directory: MusicDirectory):
    print("Добавление записи:")
    artist = input("Исполнитель*: ").strip()
    album = input("Альбом*: ").strip()
    genre = input("Жанр*: ").strip()
    year = prompt_int("Год (например, 2007)*: ")
    rating = prompt_int("Оценка (1..10, можно пропустить): ", allow_empty=True)
    notes = input("Заметки (необязательно): ").strip()
    entry = directory.add_entry(artist, album, genre, year, rating, notes)
    print(f"Добавлено: ID={entry.id} — {entry.artist} — {entry.album}")

def action_list(directory: MusicDirectory):
    print("Список записей:")
    entries = directory.list_entries()
    print_table(entries)

def action_delete(directory: MusicDirectory):
    print("Удаление записи:")
    entry_id = prompt_int("Введите ID для удаления: ")
    if directory.delete_entry(entry_id):
        print("Удалено.")
    else:
        print("Запись не найдена.")

def action_edit(directory: MusicDirectory):
    print("Редактирование записи:")
    entry_id = prompt_int("ID записи: ")
    e = directory.get(entry_id)
    if not e:
        print("Запись не найдена.")
        return
    print("Оставьте поле пустым, если не хотите менять значение.")
    artist = input(f"Исполнитель [{e.artist}]: ").strip() or e.artist
    album = input(f"Альбом [{e.album}]: ").strip() or e.album
    genre = input(f"Жанр [{e.genre}]: ").strip() or e.genre
    year_in = input(f"Год [{e.year}]: ").strip()
    year = e.year if year_in == "" else int(year_in)
    rating_in = input(f"Оценка (1..10 или пусто) [{e.rating if e.rating is not None else ''}]: ").strip()
    rating = e.rating if rating_in == "" else (int(rating_in) if rating_in.lower() != "none" else None)
    notes = input(f"Заметки [{e.notes}]: ").strip() or e.notes
    if directory.edit_entry(entry_id, artist=artist, album=album, genre=genre, year=year, rating=rating, notes=notes):
        print("Обновлено.")
    else:
        print("Не удалось обновить запись.")

def action_search(directory: MusicDirectory):
    print("Поиск/фильтр (подстроки, нечувствительно к регистру). Пустое поле — пропустить:")
    artist = input("Исполнитель: ").strip()
    album = input("Альбом: ").strip()
    genre = input("Жанр: ").strip()
    year = input("Год: ").strip()
    rating = input("Оценка: ").strip()
    filt = {}
    if artist: filt["artist"] = artist
    if album: filt["album"] = album
    if genre: filt["genre"] = genre
    if year: filt["year"] = year
    if rating: filt["rating"] = rating
    entries = directory.list_entries(filter_by=filt)
    print_table(entries)

def action_sort(directory: MusicDirectory):
    print("Сортировка по полю (id, artist, album, genre, year, rating):")
    key = input("Поле (по умолчанию id): ").strip() or "id"
    reverse = input("Обратный порядок? (y/N): ").strip().lower() == "y"
    entries = directory.list_entries(sort_by=key, reverse=reverse)
    print_table(entries)

def action_export(directory: MusicDirectory):
    path = input("Файл CSV (по умолчанию export.csv): ").strip() or "export.csv"
    directory.export_csv(path)
    print(f"Экспортировано в {path}")

def action_import(directory: MusicDirectory):
    path = input("Импортировать из CSV (например, export.csv): ").strip()
    try:
        n = directory.import_csv(path)
        print(f"Импорт завершён, добавлено записей: {n}")
    except Exception as ex:
        print(f"Ошибка импорта: {ex}")

def action_recommend(directory: MusicDirectory):
    rec = directory.recommend()
    if not rec:
        print("Пока нечего рекомендовать — добавьте записи.")
        return
    print("Советуем послушать:")
    print_table([rec])

def action_stats(directory: MusicDirectory):
    stats = directory.stats_by_genre()
    if not stats:
        print("Статистика пуста.")
        return
    print("Статистика по жанрам:")
    width_key = max(10, max(len(k) for k in stats.keys()))
    width_val = max(5, max(len(str(v)) for v in stats.values()))
    print(f"{'Жанр'.ljust(width_key)} | {'Кол-во'.rjust(width_val)}")
    print(f"{'-'*width_key}-+-{'-'*width_val}")
    for k, v in stats.items():
        print(f"{k.ljust(width_key)} | {str(v).rjust(width_val)}")

# --------------------------- Точка входа ---------------------------

def main():
    if len(sys.argv) > 1 and sys.argv[1] in {"-h", "--help"}:
        print("Запустите программу без аргументов и следуйте меню.")
        return
    menu()

if __name__ == "__main__":
    main()
