import tkinter as tk
import duckdb
import sqlparse
from tkinter import Frame
from tkinter import messagebox
from tkinter import ttk
from tkinter import Text

class DataBaseGUI:
    view_open = False
    guest_window = master_window = None
    user_entry = pw_entry = None
    user_info_frame = None
    invalid_login = None
    root = conn = None

    def __init__guest__database__(self):
        try:
            self.conn = duckdb.connect('DatingDB.db', read_only=True)
        except duckdb.Error as error:
            print(error)
            exit()

    def __init__master__database__(self):
        try:
            self.conn = duckdb.connect('DatingDB.db', read_only=False)
        except duckdb.Error as error:
            print(error)
            exit()

    def check_master_login(self, user, pw):
        return user == 'master' and pw == '12345678'

    def try_login(self):
        user, pw = self.user_entry.get(), self.pw_entry.get()
        if self.invalid_login is not None:
            self.invalid_login.destroy()
        if self.check_master_login(user, pw):
            self.master_view()
        else:
            self.invalid_login = tk.Label(self.user_info_frame, text = 'Invalid Login', font = ('Arial 8'), fg = '#fc2d2d')
            self.invalid_login.grid(row = 5, column = 10)

    def __init__(self):
        window = tk.Tk()
        window.title("DatingDB Login")

        frame = tk.Frame(window)
        frame.pack(padx = 20, pady = 20)

        self.user_info_frame = tk.LabelFrame(frame)
        self.user_info_frame.grid(row = 50, column = 50)

        user_label = tk.Label(self.user_info_frame, text = 'Admin Login')
        user_label.grid(row = 0, column = 10)

        self.user_entry = tk.Entry(self.user_info_frame, width = 15)
        self.pw_entry = tk.Entry(self.user_info_frame, width = 15)
        self.user_entry.grid(row = 1, column = 10)
        self.pw_entry.grid(row = 2, column = 10)

        guest_login = tk.Button(self.user_info_frame, text = 'Guest', font = ('Arial 8'), command=self.guest_view)
        guest_login.grid(row = 5, column = 9)

        master_login = tk.Button(self.user_info_frame, text = 'Login', font = ('Arial 8'), command=self.try_login)
        master_login.grid(row = 5, column = 11)

        window.mainloop()
    
    def set_view_off(self):
        self.root.destroy()
        self.view_open = False
        self.conn.close()
    
    def master_view(self):
        if self.view_open:
            return
        self.view_open = True
        self.__init__master__database__()
        
        self.root = tk.Tk()
        self.root.configure(background='#c0d4ff')
        self.root.title('Dating Database (MASTER)')
        self.init_database_components()

    def guest_view(self):
        if self.view_open:
            return
        self.view_open = True
        self.__init__guest__database__()

        self.root = tk.Tk()
        self.root.configure(background='#c0d4ff')
        self.root.title('Dating Database (READ ONLY)')
        self.init_database_components()

    def init_database_components(self):
        border_color = tk.Frame(self.root, background='light blue')
        self.label = tk.Label(border_color, text="Dating Database", bg='#d4faff', fg='#000000')
        self.label.pack(padx=1, pady=1)
        border_color.pack(padx=10, pady=10)

        entry_query = tk.Label(self.root, text="Enter Query:", height=1, width=63, bg='#c0d4ff', fg='#000000', anchor='w')
        entry_query.pack()

        self.textbox = tk.Text(self.root, height=5, font=('Arial', 12), fg='#000000', insertbackground='#000000')
        self.textbox.configure(bg='white')
        self.textbox.pack(padx=80, pady=5)

        self.button = tk.Button(self.root, borderwidth=1, text="Query", font=('Arial', 12), fg='black', command=self.display_query)
        self.button.pack(pady=10)

        self.root.protocol('WM_DELETE_WINDOW', self.set_view_off)
        self.root.mainloop()

    def is_read_only_query(self, sql_query: str) -> bool:
        # Assumes a single query is defined in sql_query
        query_type = sqlparse.parse(sql_query)[0].get_type().lower()
        return query_type == 'select' or query_type == 'unknown'

    def display_query(self):
        sql_query = self.textbox.get('1.0', tk.END)
        try:
            query_results = self.conn.execute(sql_query).fetchall()
            if not self.is_read_only_query(sql_query):
                messagebox.showinfo(title='Query Results', message='Query Success!')
                return

            field_names = [item[0] for item in self.conn.description]
            query_window = tk.Tk()
            query_window.configure(background='#ffffff')

            style = ttk.Style(query_window)
            style.theme_use('clam')
            style.configure("Treeview", borderwidth=0, bg="#9be8e5", fg="#000000")

            query_frame = Frame(query_window, bg='#ffffff')
            query_frame.pack()

            tree_view = ttk.Treeview(query_frame, columns=[i for i in range(1, len(field_names) + 1)], 
                                        show="headings")
            tree_view.pack()

            for idx in range(len(field_names)):
                tree_view.heading(idx + 1, text=field_names[idx])

            for elem in query_results:
                tree_view.insert('', 'end', values=elem)
            query_window.title("Query Results")
            query_window.mainloop()
        except:
            messagebox.showinfo(title='Query Results', message='Query Failed!')

DataBaseGUI()