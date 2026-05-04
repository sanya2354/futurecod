import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from urllib.parse import quote

class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
        self.search_results = {}

        self.create_widgets()
        self.update_favorites_list()

    def create_widgets(self):
        # --- Поиск ---
        search_frame = ttk.LabelFrame(self.root, text="Поиск пользователя", padding=10)
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Введите имя пользователя:").grid(row=0, column=0, sticky="w")
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<Return>", lambda e: self.search_users())

        search_btn = ttk.Button(search_frame, text="Найти", command=self.search_users)
        search_btn.grid(row=0, column=2, padx=5)

        # --- Результаты ---
        results_frame = ttk.LabelFrame(self.root, text="Результаты поиска", padding=10)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_listbox = tk.Listbox(results_frame, height=8)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_listbox.yview)
        self.results_listbox.configure(yscrollcommand=scrollbar.set)
        self.results_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        add_btn = ttk.Button(self.root, text="★ Добавить в избранное", command=self.add_to_favorites)
        add_btn.pack(pady=5)

        # --- Избранное ---
        favorites_frame = ttk.LabelFrame(self.root, text="Избранное", padding=10)
        favorites_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.favorites_listbox = tk.Listbox(favorites_frame, height=6)
        fav_scrollbar = ttk.Scrollbar(favorites_frame, orient="vertical", command=self.favorites_listbox.yview)
        self.favorites_listbox.configure(yscrollcommand=fav_scrollbar.set)
        self.favorites_listbox.pack(side="left", fill="both", expand=True)
        fav_scrollbar.pack(side="right", fill="y")

        remove_btn = ttk.Button(self.root, text="Удалить из избранного", command=self.remove_from_favorites)
        remove_btn.pack(pady=5)

    def load_favorites(self):
        if os.path.exists(self.favorites_file):
            try:
                with open(self.favorites_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_favorites(self):
        with open(self.favorites_file, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, indent=4, ensure_ascii=False)

    def search_users(self):
        query = self.search_entry.get().strip()
        if not query:
            messagebox.showwarning("Предупреждение", "Поле поиска не может быть пустым!")
            return

        self.results_listbox.delete(0, tk.END)
        self.search_results.clear()

        encoded_query = quote(query)
        url = f"https://api.github.com/search/users?q={encoded_query}"
        headers = {"User-Agent": "GitHubUserFinder/1.0"}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                error_msg = f"GitHub API вернул статус {response.status_code}\n"
                try:
                    error_data = response.json()
                    error_msg += error_data.get("message", response.text[:200])
                except:
                    error_msg += response.text[:200]
                messagebox.showerror("Ошибка API", error_msg)
                return

            data = response.json()
            users = data.get("items", [])
            if not users:
                self.results_listbox.insert(tk.END, "Пользователи не найдены.")
                return

            for user in users:
                login = user["login"]
                profile_url = user["html_url"]
                self.search_results[login] = profile_url
                self.results_listbox.insert(tk.END, login)

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка соединения", f"Не удалось выполнить запрос:\n{e}")

    def add_to_favorites(self):
        selection = self.results_listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Сначала выберите пользователя из результатов поиска.")
            return

        login = self.results_listbox.get(selection[0])
        if login == "Пользователи не найдены.":
            return

        if login in self.favorites:
            messagebox.showinfo("Информация", f"Пользователь {login} уже в избранном.")
            return

        profile_url = self.search_results.get(login)
        if profile_url:
            self.favorites[login] = profile_url
            self.save_favorites()
            self.update_favorites_list()
            messagebox.showinfo("Успех", f"Пользователь {login} добавлен в избранное.")

    def remove_from_favorites(self):
        selection = self.favorites_listbox.curselection()
        if not selection:
            messagebox.showinfo("Информация", "Выберите пользователя из списка избранного.")
            return

        login = self.favorites_listbox.get(selection[0])
        if login in self.favorites:
            del self.favorites[login]
            self.save_favorites()
            self.update_favorites_list()
            messagebox.showinfo("Успех", f"Пользователь {login} удалён из избранного.")

    def update_favorites_list(self):
        self.favorites_listbox.delete(0, tk.END)
        for login in self.favorites.keys():
            self.favorites_listbox.insert(tk.END, login)

if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()