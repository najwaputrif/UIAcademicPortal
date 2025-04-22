import tkinter as tk
from tkinter import ttk
import sqlite3
import pandas as pd

def create_db_and_tables():
    conn = sqlite3.connect('C:/Users/najwa/Downloads/Database_data/Database UI.db')
    cursor = conn.cursor()
    
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS Rumpun (
                         ID_Rumpun TEXT PRIMARY KEY NOT NULL, 
                         Nama_Rumpun TEXT);
    CREATE TABLE IF NOT EXISTS ProgramStudi (
                         ID_Prodi TEXT PRIMARY KEY NOT NULL, 
                         Nam_Prodi TEXT, 
                         Akreditasi TEXT, 
                         Daya_Tampung INTEGER, 
                         ID_Fakultas TEXT, 
                         ID_Program TEXT,
                         FOREIGN KEY (ID_Fakultas) REFERENCES Fakultas(ID_Fakultas),
                         FOREIGN KEY (ID_Program) REFERENCES Program(ID_Program));
    CREATE TABLE IF NOT EXISTS BiayaPendidikan (
                         ID_Biaya TEXT PRIMARY KEY NOT NULL, 
                         Golongan TEXT, 
                         Harga TEXT,
                         ID_Rumpun,
                         FOREIGN KEY (ID_Rumpun) REFERENCES Rumpun(ID_Rumpun));
    CREATE TABLE IF NOT EXISTS ProspekKerja (
                         ID_Prospek TEXT PRIMARY KEY NOT NULL, 
                         Nama_Prospek TEXT, 
                         Gaji_per_bulan TEXT,
                         ID_Prodi,
                         FOREIGN KEY (ID_Prodi) REFERENCES ProgramStudi(ID_Prodi));
    CREATE TABLE IF NOT EXISTS ProgramPendidikan (
                         ID_Program TEXT PRIMARY KEY NOT NULL, 
                         Jenjang TEXT);
    CREATE TABLE IF NOT EXISTS Fakultas (
                         ID_Fakultas TEXT PRIMARY KEY NOT NULL, 
                         Nama_Fakultas TEXT, 
                         Biaya_Golongan_Terendah TEXT, 
                         Biaya_Golongan_Tertinggi TEXT,
                         ID_Rumpun,
                         FOREIGN KEY (ID_Rumpun) REFERENCES Rumpun(ID_Rumpun));
    ''')
    
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect('C:/Users/najwa/Downloads/Database_data/Database UI.db')

    df_fakultas = pd.read_csv('C:/Users/najwa/Downloads/Database_data/Fakultas.csv', encoding='utf-8')
    df_fakultas.to_sql('Fakultas', conn, if_exists='replace', index=False)

    df_program_studi = pd.read_csv('C:/Users/najwa/Downloads/Database_data/Program Studi.csv', encoding='utf-8')
    df_program_studi.to_sql('ProgramStudi', conn, if_exists='replace', index=False)
    
    df_biaya_pendidikan = pd.read_csv('C:/Users/najwa/Downloads/Database_data/Biaya Pendidikan.csv', encoding='utf-8')
    df_biaya_pendidikan.to_sql('BiayaPendidikan', conn, if_exists='replace', index=False)
    
    df_rumpun = pd.read_csv('C:/Users/najwa/Downloads/Database_data/Rumpun.csv', encoding='utf-8')
    df_rumpun.to_sql('Rumpun', conn, if_exists='replace', index=False)

    df_prospek_kerja = pd.read_csv('C:/Users/najwa/Downloads/Database_data/Prospek Kerja.csv', encoding='utf-8')
    df_prospek_kerja.to_sql('ProspekKerja', conn, if_exists='replace', index=False)
    
    df_program_pendidikan = pd.read_csv('C:/Users/najwa/Downloads/Database_data/Program Pendidikan.csv', encoding='utf-8')
    df_program_pendidikan.to_sql('ProgramPendidikan', conn, if_exists='replace', index=False)

    conn.commit()
    conn.close()

def query_program_pendidikan(jenjang):
    conn = sqlite3.connect('C:/Users/najwa/Downloads/Database_data/Database UI.db')
    cursor = conn.cursor()
    query = """
    SELECT r.Nama_Rumpun, f.Nama_Fakultas, f.Biaya_Golongan_Terendah, f.Biaya_Golongan_Tertinggi
    FROM ProgramPendidikan pp
    JOIN ProgramStudi ps ON ps.ID_Program = pp.ID_Program
    JOIN Fakultas f ON ps.ID_Fakultas = f.ID_Fakultas
    JOIN Rumpun r ON f.ID_Rumpun = r.ID_Rumpun
    WHERE pp.Jenjang = ?
    """
    cursor.execute(query, (jenjang,))
    results = cursor.fetchall()
    conn.close()
    return results

def show_jenjang_buttons():
    for widget in main_frame.winfo_children():
        widget.destroy()
    ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue").pack(pady=10)
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)    
    ttk.Label(main_frame, text="Jenjang Pendidikan di UI", font=('Verdana', 30)).pack(pady=10)
    
    jenjang_names = ["S1", "D3", "D4"]
    for name in jenjang_names:
        button = ttk.Button(main_frame, text=name, style="TButton",
                            command=lambda j=name: show_detail_jenjang(j))
        button.pack(pady=10)

    back_button = ttk.Button(main_frame, text="Kembali", command=reset_view, style="TButton")
    back_button.pack(pady=(20, 10), side='bottom')

def show_detail_jenjang(jenjang_name):
    results = query_program_pendidikan(jenjang_name)
    for widget in main_frame.winfo_children():
        widget.destroy()

    ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue").pack(pady=10)
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)
    ttk.Label(main_frame, text=f"Detail untuk Jenjang {jenjang_name}", font=('Verdana', 30)).pack(pady=10)

    style = ttk.Style()
    style.configure("Treeview", background="white", fieldbackground="white")
    style.map('Treeview', background=[('selected', 'brown')])
    style.map('Treeview.Heading', background=[('active', 'yellow')])

    tree = ttk.Treeview(main_frame, columns=("Rumpun", "Fakultas", "Biaya Terendah", "Biaya Tertinggi"), show="headings", height=15)
    tree.heading("Rumpun", text="Rumpun")
    tree.heading("Fakultas", text="Fakultas")
    tree.heading("Biaya Terendah", text="Uang Kuliah Tunggal Terendah")
    tree.heading("Biaya Tertinggi", text="Uang Kuliah Tunggal Tertinggi")
    
    fakultas_data = {}
    for rumpun, fakultas, biaya_terendah, biaya_tertinggi in results:
        if fakultas not in fakultas_data:
            fakultas_data[fakultas] = [rumpun, fakultas, biaya_terendah, biaya_tertinggi]
        else:
            existing_biaya_terendah, existing_biaya_tertinggi = fakultas_data[fakultas][2], fakultas_data[fakultas][3]
            fakultas_data[fakultas][2] = min(existing_biaya_terendah, biaya_terendah)
            fakultas_data[fakultas][3] = max(existing_biaya_tertinggi, biaya_tertinggi)
    
    for fakultas in fakultas_data.values():
        tree.insert("", "end", values=(fakultas[0], fakultas[1], fakultas[2], fakultas[3]))
    
    tree.pack(pady=10, fill='x', expand=True)

    back_button = ttk.Button(main_frame, text="Kembali", command=show_jenjang_buttons)
    back_button.pack(pady=(20,10), side='bottom')

def query_biaya_pendidikan(keyword):
    conn = sqlite3.connect('C:/Users/najwa/Downloads/Database_data/Database UI.db')
    cursor = conn.cursor()
    
    query = """
    SELECT b.ID_Biaya, b.Golongan, b.Harga
    FROM BiayaPendidikan b
    JOIN Rumpun r ON b.ID_Rumpun = r.ID_Rumpun
    JOIN Fakultas f ON f.ID_Rumpun = r.ID_Rumpun
    JOIN ProgramStudi ps ON f.ID_Fakultas = ps.ID_Fakultas
    WHERE ps.Nama_Prodi = ? OR f.Nama_Fakultas = ?
    """
    cursor.execute(query, (keyword, keyword))
    results = cursor.fetchall()
    conn.close()
    return results

def show_biaya_pendidikan_search():
    for widget in main_frame.winfo_children():
        widget.destroy()

    ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue").pack(pady=10)
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)
    ttk.Label(main_frame, text="Biaya Pendidikan di UI", font=('Verdana', 25)).pack(pady=10)
    highlight_label = tk.Label(main_frame, text="Cari melalui Nama Program Studi", font=('Verdana', 12), bg="yellow")
    highlight_label.pack(pady=5)    
    ttk.Label(main_frame, text="Contoh: Ilmu Aktuaria", font=('Verdana', 10)).pack(pady=10)
    search_entry = ttk.Entry(main_frame, width=50)
    search_entry.pack(pady=5)

    search_button = ttk.Button(main_frame, text="Cari", command=lambda: perform_search(search_entry.get()))
    search_button.pack(pady=20)

    back_button = ttk.Button(main_frame, text="Kembali", command=reset_view, style="TButton")
    back_button.pack(pady=(20, 10), side='bottom')

def perform_search(keyword):
    results = query_biaya_pendidikan(keyword)
    for widget in main_frame.winfo_children():
        widget.destroy()

    ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue").pack(pady=10)
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)
    ttk.Label(main_frame, text="Hasil Pencarian", font=('Verdana', 30)).pack(pady=20)

    if not results:
        ttk.Label(main_frame, text="‼️ Data Tidak Ditemukan  ‼️", font=('Verdana', 16), foreground="#8b0000").pack(pady=20)
    else:
        tree = ttk.Treeview(main_frame, columns=("Golongan", "Uang Kuliah Tunggal (Rp)"), show="headings", height=11)
        tree.heading("Golongan", text="Golongan")
        tree.heading("Uang Kuliah Tunggal (Rp)", text="Uang Kuliah Tunggal (Rp)")
        tree.column("Golongan", anchor="center", width=100)
        tree.column("Uang Kuliah Tunggal (Rp)", anchor="center", width=200)

        style = ttk.Style()
        style.configure("Treeview", background="white", fieldbackground="white")
        style.map('Treeview', background=[('selected', 'brown')])
        style.map('Treeview.Heading', background=[('active', 'yellow')])

        for id_biaya, golongan, harga in results:
            tree.insert("", "end", values=(golongan, harga))

        tree.pack(pady=10, fill='x', expand=True)

    back_button = ttk.Button(main_frame, text="Kembali", command=show_biaya_pendidikan_search)
    back_button.pack(pady=(20, 10), side='bottom')

def query_program_studi(keyword=None):
    conn = sqlite3.connect('C:/Users/najwa/Downloads/Database_data/Database UI.db')
    cursor = conn.cursor()
    if keyword:
        query = """
        SELECT ps.Nama_Prodi, ps.Akreditasi, ps.Daya_Tampung, f.Nama_Fakultas
        FROM ProgramStudi ps
        JOIN Fakultas f ON ps.ID_Fakultas = f.ID_Fakultas
        WHERE ps.Nama_Prodi LIKE ?
        ORDER BY ps.Nama_Prodi
        """
        cursor.execute(query, ('%' + keyword + '%',))
    else:
        query = """
        SELECT ps.Nama_Prodi, ps.Akreditasi, ps.Daya_Tampung, f.Nama_Fakultas
        FROM ProgramStudi ps
        JOIN Fakultas f ON ps.ID_Fakultas = f.ID_Fakultas
        ORDER BY ps.Nama_Prodi
        """
        cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

def query_prospek_kerja(prodi):
    conn = sqlite3.connect('C:/Users/najwa/Downloads/Database_data/Database UI.db')
    cursor = conn.cursor()
    query = """
    SELECT Nama_Prospek, Gaji_per_bulan
    FROM ProspekKerja
    JOIN ProgramStudi ON ProspekKerja.ID_Prodi = ProgramStudi.ID_Prodi
    WHERE ProgramStudi.Nama_Prodi = ?
    """
    cursor.execute(query, (prodi,))
    results = cursor.fetchall()
    conn.close()
    return results

def show_program_studi():
    for widget in main_frame.winfo_children():
        widget.destroy()

    bg_color = "#ffc067"

    ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue", background=bg_color).pack(pady=10)
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)
    ttk.Label(main_frame, text="Program Studi", font=('Verdana', 30), background=bg_color).pack(pady=15)

    search_frame = tk.Frame(main_frame, bg=bg_color)
    search_frame.pack(fill='x', pady=10, padx=5)
    ttk.Label(search_frame, text="Cari Program Studi:", font=('Verdana', 12), background=bg_color).pack(side='left')
    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.pack(side='left', padx=5)
    search_button = ttk.Button(search_frame, text="Cari", command=lambda: search_program_studi(search_entry.get()))
    search_button.pack(side='left')

    tree_frame = tk.Frame(main_frame, bg=bg_color)
    tree_frame.pack(fill='both', expand=True)
    
    global tree
    tree = ttk.Treeview(tree_frame, columns=("Nama Prodi", "Akreditasi", "Daya Tampung", "Asal Fakultas"), show="headings", height=11)
    tree.heading("Nama Prodi", text="Nama Program Studi")
    tree.heading("Akreditasi", text="Akreditasi")
    tree.heading("Daya Tampung", text="Daya Tampung")
    tree.heading("Asal Fakultas", text="Asal Fakultas")
    tree.column("Nama Prodi", anchor="center", width=200)
    tree.column("Akreditasi", anchor="center", width=100)
    tree.column("Daya Tampung", anchor="center", width=100)
    tree.column("Asal Fakultas", anchor="center", width=150)

    results = query_program_studi()
    for nama_prodi, akreditasi, daya_tampung, nama_fakultas in results:
        tree.insert("", "end", values=(nama_prodi, akreditasi, daya_tampung, nama_fakultas))
    
    style = ttk.Style()
    style.configure("Treeview", background="white", fieldbackground="white")
    style.map('Treeview', background=[('selected', 'brown')])
    style.map('Treeview.Heading', background=[('active', 'yellow')])
    
    tree.pack(pady=10, fill='both', expand=True)
    tree.bind("<Double-1>", lambda event: show_prospek_detail(tree))

    ttk.Label(main_frame, text="Klik baris untuk melihat detail informasi", font=('Verdana', 12), foreground="#8b0000", background="yellow").pack(pady=10, anchor="w")
    back_button = ttk.Button(main_frame, text="Kembali", command=reset_view)
    back_button.pack(pady=(20, 10), side='bottom')

def search_program_studi(keyword):
    for widget in main_frame.winfo_children():
        widget.destroy()

    bg_color = "#ffc067"

    ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue", background=bg_color).pack(pady=10)
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)
    ttk.Label(main_frame, text="Program Studi", font=('Verdana', 30), background=bg_color).pack(pady=15)

    search_frame = tk.Frame(main_frame, bg=bg_color)
    search_frame.pack(fill='x', pady=10, padx=5)
    ttk.Label(search_frame, text="Cari Program Studi:", font=('Verdana', 12), background=bg_color).pack(side='left')
    search_entry = ttk.Entry(search_frame, width=40)
    search_entry.pack(side='left', padx=5)
    search_entry.insert(0, keyword)
    search_button = ttk.Button(search_frame, text="Cari", command=lambda: search_program_studi(search_entry.get()))
    search_button.pack(side='left')

    tree_frame = tk.Frame(main_frame, bg=bg_color)
    tree_frame.pack(fill='both', expand=True)
    
    global tree
    tree = ttk.Treeview(tree_frame, columns=("Nama Prodi", "Akreditasi", "Daya Tampung", "Asal Fakultas"), show="headings", height=11)
    tree.heading("Nama Prodi", text="Nama Program Studi")
    tree.heading("Akreditasi", text="Akreditasi")
    tree.heading("Daya Tampung", text="Daya Tampung")
    tree.heading("Asal Fakultas", text="Asal Fakultas")
    tree.column("Nama Prodi", anchor="center", width=200)
    tree.column("Akreditasi", anchor="center", width=100)
    tree.column("Daya Tampung", anchor="center", width=100)
    tree.column("Asal Fakultas", anchor="center", width=150)

    results = query_program_studi(keyword)
    for nama_prodi, akreditasi, daya_tampung, nama_fakultas in results:
        tree.insert("", "end", values=(nama_prodi, akreditasi, daya_tampung, nama_fakultas))

    tree.pack(pady=10, fill='both', expand=True)
    tree.bind("<Double-1>", lambda event: show_prospek_detail(tree))

    ttk.Label(main_frame, text="Klik baris untuk melihat detail informasi", font=('Verdana', 12), foreground="#8b0000", background="yellow").pack(pady=10, anchor="w")
    back_button = ttk.Button(main_frame, text="Kembali", command=show_program_studi)
    back_button.pack(pady=(20, 10), side='bottom')

def show_prospek_detail(tree):
    selected_item = tree.selection()[0]
    prodi = tree.item(selected_item, 'values')[0]
    results = query_prospek_kerja(prodi)
    
    for widget in main_frame.winfo_children():
        widget.destroy()

    ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue").pack(pady=10)
    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)
    ttk.Label(main_frame, text=f"Prospek Kerja Program Studi {prodi}", font=('Verdana', 30)).pack(pady=10)

    tree = ttk.Treeview(main_frame, columns=("Nama Prospek", "Gaji per Bulan"), show="headings", height=2)
    tree.heading("Nama Prospek", text="Nama Prospek Kerja")
    tree.heading("Gaji per Bulan", text="Gaji per Bulan")
    tree.column("Nama Prospek", anchor="center", width=200)
    tree.column("Gaji per Bulan", anchor="center", width=150)

    for nama_prospek, gaji_per_bulan in results:
        tree.insert("", "end", values=(nama_prospek, gaji_per_bulan))

    tree.pack(pady=10, fill='x', expand=True)

    back_button = ttk.Button(main_frame, text="Kembali", command=show_program_studi)
    back_button.pack(pady=(20, 10), side='bottom')

def reset_view():
    for widget in main_frame.winfo_children():
        widget.destroy()
    initialize_main_view()

def initialize_main_view():
    global canvas, flying_text_instances, flying_text, option_var

    label_welcome = ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue")
    label_welcome.pack(pady=(20, 20))

    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)

    canvas = tk.Canvas(main_frame, height=100, bg="#ffc067", bd=0, highlightthickness=0)
    canvas.pack(fill='x', pady=20)

    flying_text = "Selamat Datang di UIAcademicPortal"
    flying_text_instances = []

    initial_text_x = root.winfo_width()
    flying_text_id = canvas.create_text(initial_text_x, 30, text=flying_text, font=('Verdana', 8), anchor='w')
    flying_text_instances.append((flying_text_id, initial_text_x))

    option_var = tk.StringVar(value="Informasi apa yang ingin Anda cari?")
    options = ["Biaya Pendidikan", "Program Pendidikan dan Fakultas", "Program Studi dan Prospek Kerja"]
    option_menu = ttk.Combobox(main_frame, textvariable=option_var, values=options, state="readonly", width=35)
    option_menu.pack(pady=20)
    option_menu.bind("<<ComboboxSelected>>", on_combobox_select)
    option_menu.bind("<FocusIn>", lambda e: option_var.set('') if option_var.get() == "Informasi apa yang ingin Anda cari?" else None)
    option_menu.bind("<FocusOut>", lambda e: option_var.set("Informasi apa yang ingin Anda cari?") if not option_var.get() else None)

    update_flying_text()

def on_combobox_select(event):
    option = option_var.get()
    if option == "Biaya Pendidikan":
        show_biaya_pendidikan_search()
    elif option == "Program Pendidikan dan Fakultas":
        show_jenjang_buttons()
    elif option == "Program Studi dan Prospek Kerja":
        show_program_studi()

def update_flying_text():
    global flying_text_instances

    for text_id, _ in flying_text_instances:
        canvas.move(text_id, -2, 0)

    if canvas.coords(flying_text_instances[0][0])[0] < -canvas.bbox(flying_text_instances[0][0])[2]:
        canvas.delete(flying_text_instances[0][0])
        flying_text_instances.pop(0)

    last_text_id, _ = flying_text_instances[-1]
    if canvas.coords(last_text_id)[0] < root.winfo_width() - 400:
        new_text_x = root.winfo_width()
        new_text_id = canvas.create_text(new_text_x, 30, text=flying_text, font=('Verdana', 8), anchor='w')
        flying_text_instances.append((new_text_id, new_text_x))

    canvas.after(50, update_flying_text)

def main():
    global root, main_frame, option_var, label_info, option_menu, canvas, flying_text, flying_text_instances

    create_db_and_tables()
    load_data()

    root = tk.Tk()
    root.title("UIAcademicPortal")
    root.geometry("900x600")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("Custom.TFrame", background="#ffc067")
    style.configure("TLabel", background="#ffc067", font=('Verdana', 12))
    style.configure("TButton", font=('Verdana', 12))

    main_frame = ttk.Frame(root, style="Custom.TFrame", padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    label_welcome = ttk.Label(main_frame, text="UIAcademicPortal", font=('Verdana', 50), foreground="dark blue")
    label_welcome.pack(pady=(20, 20))

    separator = ttk.Separator(main_frame, orient='horizontal')
    separator.pack(fill='x', padx=5, pady=5)

    canvas = tk.Canvas(main_frame, height=100, bg="#ffc067", bd=0, highlightthickness=0)
    canvas.pack(fill='x', pady=20)

    flying_text = "Selamat Datang di UIAcademicPortal"
    flying_text_instances = []

    initial_text_x = root.winfo_width()
    flying_text_id = canvas.create_text(initial_text_x, 30, text=flying_text, font=('Verdana', 8), anchor='w')
    flying_text_instances.append((flying_text_id, initial_text_x))

    option_var = tk.StringVar(value="Informasi apa yang ingin Anda cari?")
    options = ["Biaya Pendidikan", "Program Pendidikan dan Fakultas", "Program Studi dan Prospek Kerja"]
    option_menu = ttk.Combobox(main_frame, textvariable=option_var, values=options, state="readonly", width=35)
    option_menu.pack(pady=20)
    option_menu.bind("<<ComboboxSelected>>", on_combobox_select)
    option_menu.bind("<FocusIn>", lambda e: option_var.set('') if option_var.get() == "Informasi apa yang ingin Anda cari?" else None)
    option_menu.bind("<FocusOut>", lambda e: option_var.set("Informasi apa yang ingin Anda cari?") if not option_var.get() else None)

    label_info = ttk.Label(main_frame, text="")
    label_info.pack(pady=10, fill='x')

    update_flying_text()

    root.mainloop()

if __name__ == "__main__":
    main()