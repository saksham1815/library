import tkinter as tk
from tkinter import messagebox
import sqlite3
from PIL import Image, ImageTk

# Create the database and books table
def create_database():
    conn = sqlite3.connect('library.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS books
                      (id INTEGER PRIMARY KEY,
                       title TEXT NOT NULL,
                       author TEXT NOT NULL,
                       copies INTEGER NOT NULL)''')
    conn.commit()
    conn.close()

create_database()

class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.attributes('-fullscreen', True)  # Start in full-screen mode
        
        window_width = 700
        window_height = 450

        # Get the screen dimension
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        # Find the center point
        center_x = int(screen_width/2 - window_width/2)
        center_y = int(screen_height/2 - window_height/2)
        root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

        # Load the background image
        self.original_bg_image = Image.open("gaura.jpeg")  # Replace with your image path
        self.bg_image = ImageTk.PhotoImage(self.original_bg_image)

        # Create Canvas and place background image
        self.canvas = tk.Canvas(root, width=root.winfo_screenwidth(), height=root.winfo_screenheight())
        self.canvas.pack(fill="both", expand=True)
        self.bg_img = self.canvas.create_image(0, 0, image=self.bg_image, anchor="nw")

        # Resize background when the window size changes
        self.root.bind("<Configure>", self.resize_bg)

        # Add custom window controls
        self.add_window_controls()

        # Database connection
        self.conn = sqlite3.connect('library.db')
        self.cursor = self.conn.cursor()

        # GUI Elements
        self.title_label = tk.Label(root, text="Title:", font=('Helvetica', 12), bg='lightyellow')
        self.canvas.create_window(250, 50, window=self.title_label)
        self.title_entry = tk.Entry(root, font=('Helvetica', 12))
        self.canvas.create_window(400, 50, window=self.title_entry)

        self.author_label = tk.Label(root, text="Author:", font=('Helvetica', 12), bg='lightyellow')
        self.canvas.create_window(250, 100, window=self.author_label)
        self.author_entry = tk.Entry(root, font=('Helvetica', 12))
        self.canvas.create_window(400, 100, window=self.author_entry)

        self.copies_label = tk.Label(root, text="Copies:", font=('Helvetica', 12), bg='lightyellow')
        self.canvas.create_window(250, 150, window=self.copies_label)
        self.copies_entry = tk.Entry(root, font=('Helvetica', 12))
        self.canvas.create_window(400, 150, window=self.copies_entry)

        self.add_button = tk.Button(root, text="Add Book", command=self.add_book, font=('Helvetica', 12), bg='lightgreen')
        self.canvas.create_window(300, 200, window=self.add_button)

        self.display_button = tk.Button(root, text="Display Books", command=self.display_books, font=('Helvetica', 12), bg='lightblue')
        self.canvas.create_window(300, 250, window=self.display_button)

        self.issue_button = tk.Button(root, text="Issue Book", command=self.issue_book, font=('Helvetica', 12), bg='lightcoral')
        self.canvas.create_window(300, 300, window=self.issue_button)

        self.return_button = tk.Button(root, text="Return Book", command=self.return_book, font=('Helvetica', 12), bg='lightgoldenrod')
        self.canvas.create_window(300, 350, window=self.return_button)

        self.exit_button = tk.Button(root, text="Exit", command=self.root.quit, font=('Helvetica', 12), bg='red', fg='white')
        self.canvas.create_window(300, 400, window=self.exit_button)

    def add_window_controls(self):
        # Create Minimize, Maximize, and Close buttons
        self.minimize_button = tk.Button(self.root, text="_", command=self.minimize_window)
        self.maximize_button = tk.Button(self.root, text="[]", command=self.toggle_fullscreen)
        self.close_button = tk.Button(self.root, text="X", command=self.root.quit)

        # Place the buttons on the canvas
        self.canvas.create_window(750, 10, window=self.minimize_button)
        self.canvas.create_window(780, 10, window=self.maximize_button)
        self.canvas.create_window(810, 10, window=self.close_button)

    def minimize_window(self):
        self.root.iconify()

    def toggle_fullscreen(self):
        is_fullscreen = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not is_fullscreen)

    def resize_bg(self, event):
        # Resize the background image to fit the new window size
        new_width = event.width
        new_height = event.height
        resized_bg = self.original_bg_image.resize((new_width, new_height), Image.ANTIALIAS)
        self.bg_image = ImageTk.PhotoImage(resized_bg)
        self.canvas.itemconfig(self.bg_img, image=self.bg_image)

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        copies = self.copies_entry.get()

        if not title or not author or not copies.isdigit():
            messagebox.showwarning("Input Error", "Please enter valid details.")
            return

        self.cursor.execute("INSERT INTO books (title, author, copies) VALUES (?, ?, ?)", 
                            (title, author, int(copies)))
        self.conn.commit()
        messagebox.showinfo("Success", f"Book '{title}' added successfully.")
        self.clear_entries()

    def display_books(self):
        self.cursor.execute("SELECT * FROM books")
        books = self.cursor.fetchall()
        if not books:
            messagebox.showinfo("No Books", "No books available in the library.")
            return

        display_window = tk.Toplevel(self.root)
        display_window.title("Available Books")
        display_window.geometry("400x400")
        
        text_area = tk.Text(display_window, font=('Helvetica', 12))
        text_area.pack()

        for book in books:
            text_area.insert(tk.END, f"Title: {book[1]}, Author: {book[2]}, Copies: {book[3]}\n")

    def issue_book(self):
        title = self.title_entry.get()
        if not title:
            messagebox.showwarning("Input Error", "Please enter the title of the book to issue.")
            return

        self.cursor.execute("SELECT * FROM books WHERE title = ? AND copies > 0", (title,))
        book = self.cursor.fetchone()

        if book:
            self.cursor.execute("UPDATE books SET copies = copies - 1 WHERE id = ?", (book[0],))
            self.conn.commit()
            messagebox.showinfo("Success", f"Book '{title}' issued successfully.")
        else:
            messagebox.showwarning("Unavailable", f"Book '{title}' is not available.")

    def return_book(self):
        title = self.title_entry.get()
        if not title:
            messagebox.showwarning("Input Error", "Please enter the title of the book to return.")
            return

        self.cursor.execute("SELECT * FROM books WHERE title = ?", (title,))
        book = self.cursor.fetchone()

        if book:
            self.cursor.execute("UPDATE books SET copies = copies + 1 WHERE id = ?", (book[0],))
            self.conn.commit()
            messagebox.showinfo("Success", f"Book '{title}' returned successfully.")
        else:
            messagebox.showwarning("Not Found", f"Book '{title}' does not belong to this library.")

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.copies_entry.delete(0, tk.END)

def main():
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
