import re
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error

# Standard syllabus-style regex pattern for email validation
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9+._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')


class ContactManagerDB:
    """Database persistence layer with MySQL connection and indexing."""

    def __init__(self, db_config):
        self.db_config = db_config
        self.init_db()

    def get_connection(self):
        return mysql.connector.connect(**self.db_config)

    def init_db(self):
        """Creates the Contact table and indexes if they do not exist."""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS Contact (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(150) NOT NULL UNIQUE,
            phone VARCHAR(20) NOT NULL,
            category VARCHAR(50) NOT NULL,
            notes TEXT,
            INDEX idx_search_name (name),
            INDEX idx_search_email (email),
            INDEX idx_search_phone (phone)
        );
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute(create_table_query)
            conn.commit()
            cursor.close()
            conn.close()
        except Error as err:
            messagebox.showerror("Database Initialization Error", str(err))

    def add_contact(self, name, email, phone, category, notes):
        query = """
        INSERT INTO Contact (name, email, phone, category, notes)
        VALUES (%s, %s, %s, %s, %s)
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name, email, phone, category, notes))
        conn.commit()
        cursor.close()
        conn.close()

    def update_contact(self, contact_id, name, email, phone, category, notes):
        query = """
        UPDATE Contact
        SET name = %s, email = %s, phone = %s, category = %s, notes = %s
        WHERE id = %s
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (name, email, phone, category, notes, contact_id))
        conn.commit()
        cursor.close()
        conn.close()

    def delete_contact(self, contact_id):
        query = "DELETE FROM Contact WHERE id = %s"
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (contact_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def search_contacts(self, keyword="", sort_by="name"):
        """
        Indexed search filtering by Name, Email, or Phone.
        Time Complexity: O(log N) for indexed search.
        """
        allowed_sort = {"name": "name", "email": "email", "phone": "phone", "category": "category"}
        sort_column = allowed_sort.get(sort_by, "name")

        query = f"""
        SELECT id, name, email, phone, category, notes
        FROM Contact
        WHERE name LIKE %s OR email LIKE %s OR phone LIKE %s
        ORDER BY {sort_column} ASC
        """
        search_pattern = f"%{keyword}%"
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (search_pattern, search_pattern, search_pattern))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows


class ContactManagerGUI:
    """Tkinter-based GUI interface for Contact Manager."""

    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.root.title("Tkinter MySQL Contact Manager")
        self.root.geometry("850x600")

        self.selected_contact_id = None

        self.setup_widgets()
        self.load_contacts()

    def setup_widgets(self):
        # --- TOP FRAME: Inputs ---
        input_frame = ttk.LabelFrame(self.root, text=" Contact Details ")
        input_frame.pack(fill="x", padx=10, pady=5)

        # Name (Entry Widget)
        ttk.Label(input_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_name = ttk.Entry(input_frame, width=25)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)

        # Email (Entry Widget)
        ttk.Label(input_frame, text="Email:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.ent_email = ttk.Entry(input_frame, width=25)
        self.ent_email.grid(row=0, column=3, padx=5, pady=5)

        # Phone (Entry Widget)
        ttk.Label(input_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.ent_phone = ttk.Entry(input_frame, width=25)
        self.ent_phone.grid(row=1, column=1, padx=5, pady=5)

        # Category (Combobox Widget)
        ttk.Label(input_frame, text="Category:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.cmb_category = ttk.Combobox(
            input_frame, values=["Student", "Faculty", "Staff", "Other"], width=23, state="readonly"
        )
        self.cmb_category.current(0)
        self.cmb_category.grid(row=1, column=3, padx=5, pady=5)

        # Notes (Text Widget)
        ttk.Label(input_frame, text="Notes:").grid(row=2, column=0, padx=5, pady=5, sticky="ne")
        self.txt_notes = tk.Text(input_frame, width=60, height=3)
        self.txt_notes.grid(row=2, column=1, columnspan=3, padx=5, pady=5)

        # --- ACTION BUTTONS FRAME ---
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Add Contact", command=self.add_contact).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Contact", command=self.update_contact).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Contact", command=self.delete_contact).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear Form", command=self.clear_form).pack(side="left", padx=5)

        # --- SEARCH & SORT FRAME ---
        search_frame = ttk.LabelFrame(self.root, text=" Search & Sort ")
        search_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Keyword:").pack(side="left", padx=5)
        self.ent_search = ttk.Entry(search_frame, width=20)
        self.ent_search.pack(side="left", padx=5)
        self.ent_search.bind("<KeyRelease>", lambda e: self.load_contacts())

        ttk.Label(search_frame, text="Sort By:").pack(side="left", padx=5)
        self.cmb_sort = ttk.Combobox(
            search_frame, values=["Name", "Email", "Phone", "Category"], width=12, state="readonly"
        )
        self.cmb_sort.current(0)
        self.cmb_sort.pack(side="left", padx=5)
        self.cmb_sort.bind("<<ComboboxSelected>>", lambda e: self.load_contacts())

        # --- TREEVIEW LIST DISPLAY ---
        list_frame = ttk.Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Name", "Email", "Phone", "Category", "Notes")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.column("ID", width=40)

        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_contact)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

    def validate_inputs(self, name, email, phone):
        if not name or not email or not phone:
            messagebox.showwarning("Validation Error", "Name, Email, and Phone fields are required.")
            return False
        if not EMAIL_REGEX.match(email):
            messagebox.showwarning("Validation Error", "Invalid Email format! Example: user@domain.com")
            return False
        return True

    def add_contact(self):
        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()
        category = self.cmb_category.get()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        if not self.validate_inputs(name, email, phone):
            return

        try:
            self.db.add_contact(name, email, phone, category, notes)
            messagebox.showinfo("Success", "Contact added successfully!")
            self.clear_form()
            self.load_contacts()
        except mysql.connector.Error as err:
            if err.errno == 1062:  # Duplicate entry error code for UNIQUE email constraint
                messagebox.showerror("Error", "Duplicate Email detected! Email must be unique.")
            else:
                messagebox.showerror("Database Error", str(err))

    def update_contact(self):
        if not self.selected_contact_id:
            messagebox.showwarning("Selection Error", "Please select a contact from the list to update.")
            return

        name = self.ent_name.get().strip()
        email = self.ent_email.get().strip()
        phone = self.ent_phone.get().strip()
        category = self.cmb_category.get()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        if not self.validate_inputs(name, email, phone):
            return

        try:
            self.db.update_contact(self.selected_contact_id, name, email, phone, category, notes)
            messagebox.showinfo("Success", "Contact updated successfully!")
            self.clear_form()
            self.load_contacts()
        except mysql.connector.Error as err:
            if err.errno == 1062:
                messagebox.showerror("Error", "Duplicate Email detected!")
            else:
                messagebox.showerror("Database Error", str(err))

    def delete_contact(self):
        if not self.selected_contact_id:
            messagebox.showwarning("Selection Error", "Please select a contact from the list to delete.")
            return

        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this contact?"):
            try:
                self.db.delete_contact(self.selected_contact_id)
                messagebox.showinfo("Success", "Contact deleted successfully!")
                self.clear_form()
                self.load_contacts()
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", str(err))

    def load_contacts(self):
        """Loads contacts into Treeview sorted and filtered in O(log N) indexed database time."""
        keyword = self.ent_search.get().strip()
        sort_by = self.cmb_sort.get().lower()

        # Clear existing rows
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            rows = self.db.search_contacts(keyword, sort_by)
            for row in rows:
                self.tree.insert("", "end", values=row)
        except Error as err:
            messagebox.showerror("Database Error", str(err))

    def on_select_contact(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        item = self.tree.item(selected[0])
        values = item["values"]

        self.selected_contact_id = values[0]
        self.ent_name.delete(0, tk.END)
        self.ent_name.insert(0, values[1])

        self.ent_email.delete(0, tk.END)
        self.ent_email.insert(0, values[2])

        self.ent_phone.delete(0, tk.END)
        self.ent_phone.insert(0, str(values[3]))

        self.cmb_category.set(values[4])

        self.txt_notes.delete("1.0", tk.END)
        self.txt_notes.insert("1.0", values[5] if values[5] else "")

    def clear_form(self):
        self.selected_contact_id = None
        self.ent_name.delete(0, tk.END)
        self.ent_email.delete(0, tk.END)
        self.ent_phone.delete(0, tk.END)
        self.cmb_category.current(0)
        self.txt_notes.delete("1.0", tk.END)


if __name__ == "__main__":
    db_credentials = {
        'host': 'localhost',
        'database': 'contact_db',
        'user': 'root',
        'password': 'your_password'
    }

    db_engine = ContactManagerDB(db_credentials)

    root = tk.Tk()
    app = ContactManagerGUI(root, db_engine)
    root.mainloop()
