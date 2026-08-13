"""
Admin panel to manage the UAMOTORS authorized users database.
Provides a GUI to view, add, remove, and import users from CSV.
"""

import os
import sys
import json
import base64
import csv
import tkinter as tk
from tkinter import messagebox, filedialog, ttk

# Hardcoded config values since the python backend was migrated to C#
TARGET_FOLDER = "UAMOTORS"
REL_DRIVE_DB_PATH = os.path.join("2026", "Design", "Electronics", "Data-Code telemetry", "auamotors_cad_alert", "authorized_users.uamotors")
MAC_DRIVE_UAMOTORS_PATH = "/Users/alejandro/Library/CloudStorage/GoogleDrive-al2242000248@azc.uam.mx/Shared drives/UAMOTORS"

def get_db_path():
    """Returns the absolute path to the Drive database."""
    if os.name != 'nt':
        base = MAC_DRIVE_UAMOTORS_PATH
    else:
        # Fallback to a default or ask user if needed on Windows
        base = os.path.join(os.path.expanduser("~"), "Google Drive", TARGET_FOLDER)
    
    return os.path.join(base, REL_DRIVE_DB_PATH)


class AdminPanel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("UAMOTORS CAD Alert - Admin Panel")
        self.geometry("600x450")
        self.db_path = get_db_path()
        self.db_data = {}
        
        self.setup_ui()
        self.load_db()

    def setup_ui(self):
        """Sets up the Tkinter user interface elements."""
        # Top frame for adding users
        add_frame = tk.LabelFrame(self, text="Agregar Nuevo Usuario")
        add_frame.pack(fill="x", padx=10, pady=5)
        
        # Inner frame to center the form
        inner_frame = tk.Frame(add_frame)
        inner_frame.pack(pady=10)
        
        tk.Label(inner_frame, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry_name = tk.Entry(inner_frame, width=35)
        self.entry_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(inner_frame, text="Correo:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry_email = tk.Entry(inner_frame, width=35)
        self.entry_email.grid(row=1, column=1, padx=5, pady=5)
        
        btn_add = tk.Button(inner_frame, text="Agregar Usuario", command=self.add_user, width=15)
        btn_add.grid(row=2, column=0, columnspan=2, pady=(10, 0))

        # Middle frame for user list
        list_frame = tk.LabelFrame(self, text="Usuarios Registrados")
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Barra de búsqueda
        search_frame = tk.Frame(list_frame)
        search_frame.pack(fill="x", padx=5, pady=5)
        tk.Label(search_frame, text="🔍 Buscar por correo:").pack(side="left")
        self.entry_search = tk.Entry(search_frame, width=30)
        self.entry_search.pack(side="left", padx=5)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_list())
        
        # Estilo para usar fuente monoespaciada y evitar el "zigzag"
        style = ttk.Style()
        style.configure("Treeview", font=("Menlo", 10))
        
        columns = ("email", "name")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Treeview")
        self.tree.heading("email", text="Correo Electrónico")
        self.tree.heading("name", text="Nombre")
        self.tree.column("email", width=250, anchor="w")
        self.tree.column("name", width=300, anchor="w")
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        # Bottom frame for actions
        action_frame = tk.Frame(self)
        action_frame.pack(fill="x", padx=10, pady=10)
        
        btn_remove = tk.Button(action_frame, text="Eliminar Seleccionado", command=self.remove_user)
        btn_remove.pack(side="left", padx=5)
        
        btn_import = tk.Button(action_frame, text="Importar CSV", command=self.import_csv)
        btn_import.pack(side="right", padx=5)

    def load_db(self):
        """Loads and decodes the database file."""
        if not os.path.exists(self.db_path):
            messagebox.showinfo("Aviso", f"No se encontró la base de datos en:\n{self.db_path}\nSe creará una nueva al guardar.")
            self.db_data = {}
            return

        try:
            with open(self.db_path, "rb") as f:
                encoded_bytes = f.read()
            json_str = base64.b64decode(encoded_bytes).decode("utf-8")
            self.db_data = json.loads(json_str)
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la base de datos:\n{e}")

    def save_db(self):
        """Encodes and saves the database file."""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            json_str = json.dumps(self.db_data, ensure_ascii=False, indent=2)
            encoded_bytes = base64.b64encode(json_str.encode("utf-8"))
            
            with open(self.db_path, "wb") as f:
                f.write(encoded_bytes)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar la base de datos:\n{e}")

    def refresh_list(self):
        """Refreshes the TreeView with current dictionary data."""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search_term = ""
        if hasattr(self, "entry_search"):
            search_term = self.entry_search.get().strip().lower()
            
        for email, info in self.db_data.items():
            if search_term in email:
                self.tree.insert("", "end", values=(email, info.get("nombre", "")))

    def add_user(self):
        """Adds a single user from the input fields."""
        name = self.entry_name.get().strip().upper()
        email = self.entry_email.get().strip().lower()
        
        if not name or not email or "@" not in email:
            messagebox.showwarning("Advertencia", "Por favor ingresa un nombre y un correo electrónico válido.")
            return
            
        self.db_data[email] = {"nombre": name}
        self.save_db()
        self.refresh_list()
        
        self.entry_name.delete(0, tk.END)
        self.entry_email.delete(0, tk.END)
        messagebox.showinfo("Éxito", f"Usuario {email} agregado correctamente.")

    def remove_user(self):
        """Removes the selected user from the list."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Selecciona un usuario de la lista para eliminar.")
            return
            
        item = selected[0]
        email = self.tree.item(item, "values")[0]
        
        if messagebox.askyesno("Confirmar", f"¿Estás seguro de que deseas eliminar a {email}?"):
            if email in self.db_data:
                del self.db_data[email]
                self.save_db()
                self.refresh_list()

    def import_csv(self):
        """Imports users from a selected CSV file."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=(("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*"))
        )
        
        if not file_path:
            return
            
        count = 0
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        email = row[0].strip().lower()
                        name = row[1].strip().upper()
                        
                        # Ignorar la fila si parece ser un encabezado
                        if email == "correo" or "email" in email or "@" not in email:
                            continue
                            
                        self.db_data[email] = {"nombre": name}
                        count += 1
            
            if count > 0:
                self.save_db()
                self.refresh_list()
                messagebox.showinfo("Éxito", f"Se importaron {count} usuarios correctamente.")
            else:
                messagebox.showwarning("Advertencia", "No se encontraron datos válidos en el CSV.")
                
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al importar:\n{e}")

if __name__ == "__main__":
    app = AdminPanel()
    app.mainloop()
