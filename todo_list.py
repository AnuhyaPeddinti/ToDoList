import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

# Database setup
def create_connection():
    conn = sqlite3.connect('todo_list.db')
    return conn

def create_table(conn):
    sql_create_tasks_table = '''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        category TEXT,
        due_date TEXT,
        priority INTEGER,
        status TEXT
    );
    '''
    conn.execute(sql_create_tasks_table)
    conn.commit()

def add_task(title, description, category, due_date, priority):
    conn = create_connection()
    sql = '''
    INSERT INTO tasks (title, description, category, due_date, priority, status)
    VALUES (?, ?, ?, ?, ?, ?)
    '''
    conn.execute(sql, (title, description, category, due_date, priority, 'incomplete'))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = create_connection()
    sql = 'DELETE FROM tasks WHERE id=?'
    conn.execute(sql, (task_id,))
    conn.commit()
    conn.close()

def update_task(task_id, title=None, description=None, category=None, due_date=None, priority=None, status=None):
    conn = create_connection()
    sql = 'UPDATE tasks SET title=?, description=?, category=?, due_date=?, priority=?, status=? WHERE id=?'
    task = conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
    updated_task = (
        title if title else task[1],
        description if description else task[2],
        category if category else task[3],
        due_date if due_date else task[4],
        priority if priority else task[5],
        status if status else task[6],
        task_id
    )
    conn.execute(sql, updated_task)
    conn.commit()
    conn.close()

def view_tasks(filter_by=None, value=None):
    conn = create_connection()
    sql = 'SELECT * FROM tasks'
    if filter_by and value:
        sql += f' WHERE {filter_by}=?'
        tasks = conn.execute(sql, (value,)).fetchall()
    else:
        tasks = conn.execute(sql).fetchall()
    conn.close()
    return tasks

def mark_task_complete(task_id):
    update_task(task_id, status='complete')

# GUI setup
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("To-Do List Application")
        
        self.title_var = tk.StringVar()
        self.description_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.due_date_var = tk.StringVar()
        self.priority_var = tk.IntVar(value=1)

        self.create_widgets()
        self.load_tasks()

    def create_widgets(self):
        # Styling
        self.root.configure(bg='#f0f8ff')
        style = ttk.Style()
        style.configure("Treeview", font=('Helvetica', 12), rowheight=25)
        style.configure("Treeview.Heading", font=('Helvetica', 14, 'bold'))

        form_frame = tk.Frame(self.root, bg='#f0f8ff')
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Title", font=('Helvetica', 12), bg='#f0f8ff').grid(row=0, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.title_var, font=('Helvetica', 12)).grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Description", font=('Helvetica', 12), bg='#f0f8ff').grid(row=1, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.description_var, font=('Helvetica', 12)).grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Category", font=('Helvetica', 12), bg='#f0f8ff').grid(row=2, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.category_var, font=('Helvetica', 12)).grid(row=2, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Due Date (YYYY-MM-DD)", font=('Helvetica', 12), bg='#f0f8ff').grid(row=3, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.due_date_var, font=('Helvetica', 12)).grid(row=3, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Priority (1-5)", font=('Helvetica', 12), bg='#f0f8ff').grid(row=4, column=0, padx=5, pady=5)
        tk.Entry(form_frame, textvariable=self.priority_var, font=('Helvetica', 12)).grid(row=4, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="Add Task", command=self.add_task, font=('Helvetica', 12), bg='#add8e6').grid(row=5, column=0, columnspan=2, pady=10)

        self.tree = ttk.Treeview(self.root, columns=("ID", "Title", "Description", "Category", "Due Date", "Priority", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Title", text="Title")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Due Date", text="Due Date")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Status", text="Status")
        self.tree.pack(pady=10)

        button_frame = tk.Frame(self.root, bg='#f0f8ff')
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Delete Task", command=self.delete_task, font=('Helvetica', 12), bg='#ffa07a').grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Update Task", command=self.update_task, font=('Helvetica', 12), bg='#90ee90').grid(row=0, column=1, padx=5)
        tk.Button(button_frame, text="Mark Complete", command=self.mark_task_complete, font=('Helvetica', 12), bg='#d3d3d3').grid(row=0, column=2, padx=5)
        tk.Button(button_frame, text="Filter Tasks", command=self.filter_tasks, font=('Helvetica', 12), bg='#afeeee').grid(row=0, column=3, padx=5)
        tk.Button(button_frame, text="Show All Tasks", command=self.load_tasks, font=('Helvetica', 12), bg='#afeeee').grid(row=0, column=4, padx=5)

    def add_task(self):
        title = self.title_var.get()
        description = self.description_var.get()
        category = self.category_var.get()
        due_date = self.due_date_var.get()
        priority = self.priority_var.get()

        if title and due_date and (1 <= priority <= 5):
            add_task(title, description, category, due_date, priority)
            self.load_tasks()
            self.clear_form()
        else:
            messagebox.showwarning("Input Error", "Please fill in all fields correctly.")

    def delete_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)["values"][0]
            delete_task(task_id)
            self.load_tasks()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to delete.")

    def update_task(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)["values"][0]
            title = self.title_var.get()
            description = self.description_var.get()
            category = self.category_var.get()
            due_date = self.due_date_var.get()
            priority = self.priority_var.get()

            update_task(task_id, title, description, category, due_date, priority)
            self.load_tasks()
            self.clear_form()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to update.")

    def mark_task_complete(self):
        selected_item = self.tree.selection()
        if selected_item:
            task_id = self.tree.item(selected_item)["values"][0]
            mark_task_complete(task_id)
            self.load_tasks()
        else:
            messagebox.showwarning("Selection Error", "Please select a task to mark complete.")

    def load_tasks(self):
        tasks = view_tasks()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for task in tasks:
            self.tree.insert("", "end", values=task)

    def filter_tasks(self):
        filter_by = simpledialog.askstring("Filter", "Filter by (category/due_date/status/priority):")
        value = simpledialog.askstring("Filter", f"Enter value for {filter_by}:")
        tasks = view_tasks(filter_by, value)
        for i in self.tree.get_children():
            self.tree.delete(i)
        for task in tasks:
            self.tree.insert("", "end", values=task)

    def clear_form(self):
        self.title_var.set("")
        self.description_var.set("")
        self.category_var.set("")
        self.due_date_var.set("")
        self.priority_var.set(1)

if __name__ == "__main__":
    conn = create_connection()
    create_table(conn)
    conn.close()

    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
