import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ---------------- BACKEND / DATABASE ----------------

conn = sqlite3.connect("railway_reservation_system.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS passengers (
    passenger_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    phone TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS trains (
    train_id INTEGER PRIMARY KEY AUTOINCREMENT,
    train_name TEXT NOT NULL,
    source TEXT NOT NULL,
    destination TEXT NOT NULL,
    fare REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    passenger_id INTEGER NOT NULL,
    train_id INTEGER NOT NULL,
    journey_date TEXT NOT NULL,
    fare REAL NOT NULL,
    FOREIGN KEY(passenger_id) REFERENCES passengers(passenger_id),
    FOREIGN KEY(train_id) REFERENCES trains(train_id)
)
""")

conn.commit()

# Separate login accounts for Client and Agent dashboards
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_accounts (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL
)
""")
conn.commit()

# Daily finance transaction records (demo only; no real money is transferred)
cursor.execute("""
CREATE TABLE IF NOT EXISTS finance_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER,
    transaction_type TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    transaction_date TEXT NOT NULL,
    notes TEXT
)
""")
conn.commit()


def add_sample_trains():
    cursor.execute("SELECT COUNT(*) FROM trains")
    count = cursor.fetchone()[0]

    if count == 0:
        trains = [
            ("Express Train", "Ongole", "Hyderabad", 450),
            ("Superfast Express", "Vijayawada", "Chennai", 350),
            ("Passenger Express", "Guntur", "Bangalore", 600),
            ("Intercity Express", "Ongole", "Vijayawada", 200)
        ]

        cursor.executemany("""
        INSERT INTO trains
        (train_name, source, destination, fare)
        VALUES (?, ?, ?, ?)
        """, trains)

        conn.commit()


add_sample_trains()


# ---------------- FRONTEND ----------------

root = tk.Tk()
root.title("Railway Reservation System")
root.geometry("850x650")
root.configure(bg="#eaf2f8")

title = tk.Label(
    root,
    text="RAILWAY RESERVATION SYSTEM",
    font=("Arial", 22, "bold"),
    bg="#154360",
    fg="white",
    pady=15
)
title.pack(fill="x")


def clear_screen():
    for widget in content.winfo_children():
        widget.destroy()


content = tk.Frame(root, bg="#eaf2f8")
content.pack(fill="both", expand=True, padx=20, pady=15)


def create_label(text, row, column=0):
    tk.Label(
        content,
        text=text,
        font=("Arial", 11),
        bg="#eaf2f8"
    ).grid(row=row, column=column, padx=10, pady=8, sticky="w")


def create_entry(row, column=1):
    entry = tk.Entry(content, font=("Arial", 11), width=30)
    entry.grid(row=row, column=column, padx=10, pady=8)
    return entry


# ---------------- 1. PASSENGER REGISTRATION ----------------

def passenger_registration():
    clear_screen()

    tk.Label(
        content,
        text="Passenger Registration",
        font=("Arial", 17, "bold"),
        bg="#eaf2f8"
    ).grid(row=0, column=0, columnspan=2, pady=15)

    create_label("Passenger Name:", 1)

    # Block digits and special symbols while typing or pasting a name.
    def valid_name_input(new_value):
        return new_value == "" or all(
            character.isalpha() or character.isspace()
            for character in new_value
        )

    name_validation = (root.register(valid_name_input), "%P")
    name = tk.Entry(
        content,
        font=("Arial", 11),
        width=30,
        validate="key",
        validatecommand=name_validation
    )
    name.grid(row=1, column=1, padx=10, pady=8)

    create_label("Age:", 2)
    age = create_entry(2)

    create_label("Gender:", 3)
    gender = ttk.Combobox(
        content,
        values=["Male", "Female", "Other"],
        state="readonly",
        width=27
    )
    gender.grid(row=3, column=1, padx=10, pady=8)

    create_label("Phone Number:", 4)
    phone = create_entry(4)

    def register():
        passenger_name = name.get().strip()
        passenger_age = age.get().strip()
        passenger_gender = gender.get()
        passenger_phone = phone.get().strip()

        if not all([
            passenger_name,
            passenger_age,
            passenger_gender,
            passenger_phone
        ]):
            messagebox.showerror("Error", "Please fill all fields")
            return

        # Allow only letters and spaces in the passenger name
        if not passenger_name.replace(" ", "").isalpha():
            messagebox.showerror(
                "Error",
                "Name must contain only letters and spaces"
            )
            return

        try:
            age_value = int(passenger_age)

            if age_value <= 0 or age_value > 120:
                messagebox.showerror(
                    "Error", "Enter a valid age"
                )
                return

            if not passenger_phone.isdigit() or len(passenger_phone) != 10:
                messagebox.showerror(
                    "Error", "Enter a valid 10-digit phone number"
                )
                return

            cursor.execute("""
            INSERT INTO passengers (name, age, gender, phone)
            VALUES (?, ?, ?, ?)
            """, (
                passenger_name,
                age_value,
                passenger_gender,
                passenger_phone
            ))

            conn.commit()

            messagebox.showinfo(
                "Success",
                f"Passenger registered successfully!\n"
                f"Passenger ID: {cursor.lastrowid}"
            )

            name.delete(0, tk.END)
            age.delete(0, tk.END)
            gender.set("")
            phone.delete(0, tk.END)

        except ValueError:
            messagebox.showerror("Error", "Age must be a number")

    tk.Button(
        content,
        text="Register Passenger",
        command=register,
        bg="#2471a3",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=5, column=1, pady=15)


# ---------------- 2. TRAIN DETAILS MANAGEMENT ----------------

def train_management():
    clear_screen()

    tk.Label(
        content,
        text="Train Details Management",
        font=("Arial", 17, "bold"),
        bg="#eaf2f8"
    ).pack(pady=10)

    form = tk.Frame(content, bg="#eaf2f8")
    form.pack()

    # Use known railway stations so random source/destination text cannot be entered.
    stations = [
        "Ongole", "Hyderabad", "Vijayawada", "Chennai", "Guntur",
        "Bangalore", "Visakhapatnam", "Tirupati", "Secunderabad",
        "Nellore", "Rajahmundry", "Warangal", "Mumbai", "Delhi",
        "Bengaluru", "Kolkata", "Pune", "Coimbatore", "Mysuru"
    ]

    tk.Label(form, text="Train Name:", bg="#eaf2f8", font=("Arial", 11)).grid(
        row=0, column=0, padx=10, pady=7, sticky="w"
    )
    train_name_entry = tk.Entry(form, width=28, font=("Arial", 11))
    train_name_entry.grid(row=0, column=1, padx=10, pady=7)

    tk.Label(form, text="Source:", bg="#eaf2f8", font=("Arial", 11)).grid(
        row=1, column=0, padx=10, pady=7, sticky="w"
    )
    source_box = ttk.Combobox(form, values=stations, state="readonly", width=26, font=("Arial", 11))
    source_box.grid(row=1, column=1, padx=10, pady=7)

    tk.Label(form, text="Destination:", bg="#eaf2f8", font=("Arial", 11)).grid(
        row=2, column=0, padx=10, pady=7, sticky="w"
    )
    destination_box = ttk.Combobox(form, values=stations, state="readonly", width=26, font=("Arial", 11))
    destination_box.grid(row=2, column=1, padx=10, pady=7)

    tk.Label(form, text="Fare:", bg="#eaf2f8", font=("Arial", 11)).grid(
        row=3, column=0, padx=10, pady=7, sticky="w"
    )
    fare_entry = tk.Entry(form, width=28, font=("Arial", 11))
    fare_entry.grid(row=3, column=1, padx=10, pady=7)

    # A simple project-level check to reject random names such as "emo".
    train_keywords = (
        "express", "train", "passenger", "superfast", "intercity",
        "vande bharat", "rajdhani", "shatabdi", "duronto", "garib rath", "mail"
    )

    def add_train():
        train_name = train_name_entry.get().strip()
        source = source_box.get().strip()
        destination = destination_box.get().strip()
        fare_text = fare_entry.get().strip()

        if not all([train_name, source, destination, fare_text]):
            messagebox.showerror("Error", "Please fill all train details")
            return

        # Letters and spaces only in train name; no digits or special symbols.
        if not train_name.replace(" ", "").isalpha():
            messagebox.showerror(
                "Invalid Train Name",
                "Train name must contain only letters and spaces."
            )
            return

        # Require a recognizable train type/name for this mini-project.
        if not any(keyword in train_name.lower() for keyword in train_keywords):
            messagebox.showerror(
                "Invalid Train Name",
                "Enter a valid-style train name, e.g. Ongole Express or Intercity Train."
            )
            return

        if source == destination:
            messagebox.showerror(
                "Invalid Route", "Source and destination must be different stations."
            )
            return

        try:
            fare = float(fare_text)
            if fare <= 0:
                messagebox.showerror("Invalid Fare", "Fare must be greater than zero.")
                return
        except ValueError:
            messagebox.showerror("Invalid Fare", "Fare must be a number, e.g. 200 or 350.50.")
            return

        cursor.execute(
            "INSERT INTO trains (train_name, source, destination, fare) VALUES (?, ?, ?, ?)",
            (train_name, source, destination, fare)
        )
        conn.commit()
        messagebox.showinfo("Success", "Train added successfully")

        train_name_entry.delete(0, tk.END)
        source_box.set("")
        destination_box.set("")
        fare_entry.delete(0, tk.END)
        show_trains()

    tk.Button(
        content,
        text="Add Train",
        command=add_train,
        bg="#239b56",
        fg="white",
        font=("Arial", 11, "bold")
    ).pack(pady=8)

    tree = ttk.Treeview(
        content,
        columns=("ID", "Name", "Source", "Destination", "Fare"),
        show="headings",
        height=8
    )

    for col in ("ID", "Name", "Source", "Destination", "Fare"):
        tree.heading(col, text=col)
        tree.column(col, width=135)

    tree.pack(fill="x", pady=10)

    def show_trains():
        for item in tree.get_children():
            tree.delete(item)
        cursor.execute("SELECT * FROM trains ORDER BY train_id")
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=row)

    show_trains()


# ---------------- 3. TICKET BOOKING ----------------

def ticket_booking():
    clear_screen()

    tk.Label(
        content,
        text="Ticket Booking",
        font=("Arial", 17, "bold"),
        bg="#eaf2f8"
    ).grid(row=0, column=0, columnspan=2, pady=15)

    create_label("Passenger ID:", 1)
    passenger_id = create_entry(1)

    create_label("Train ID:", 2)
    train_id = create_entry(2)

    create_label("Journey Date (YYYY-MM-DD):", 3)
    journey_date = create_entry(3)

    create_label("Payment Method:", 4)
    payment_method = ttk.Combobox(
        content, values=["UPI (Demo)", "Card (Demo)", "Cash (Demo)"],
        state="readonly", width=27
    )
    payment_method.grid(row=4, column=1, padx=10, pady=8)
    payment_method.set("UPI (Demo)")

    def book_ticket():
        pid = passenger_id.get().strip()
        tid = train_id.get().strip()
        date = journey_date.get().strip()

        if not pid or not tid or not date:
            messagebox.showerror("Error", "Fill all booking details")
            return

        try:
            pid = int(pid)
            tid = int(tid)

            # Validate date format and actual calendar date
            from datetime import datetime
            parsed_date = datetime.strptime(date, "%Y-%m-%d").date()

            if parsed_date < datetime.today().date():
                messagebox.showerror(
                    "Error", "Journey date cannot be in the past"
                )
                return

            cursor.execute(
                "SELECT passenger_id FROM passengers WHERE passenger_id=?",
                (pid,)
            )
            passenger = cursor.fetchone()

            if passenger is None:
                messagebox.showerror(
                    "Error", "Passenger ID not found. Register first."
                )
                return

            cursor.execute(
                "SELECT train_name, fare FROM trains WHERE train_id=?",
                (tid,)
            )
            train = cursor.fetchone()

            if train is None:
                messagebox.showerror("Error", "Train ID not found")
                return

            fare = train[1]

            cursor.execute("""
            INSERT INTO tickets
            (passenger_id, train_id, journey_date, fare)
            VALUES (?, ?, ?, ?)
            """, (pid, tid, date, fare))

            conn.commit()
            ticket_id = cursor.lastrowid

            # Record a simulated collection for the daily finance report.
            from datetime import datetime
            cursor.execute("""
                INSERT INTO finance_transactions
                (ticket_id, transaction_type, amount, payment_method,
                 payment_status, transaction_date, notes)
                VALUES (?, 'COLLECTION', ?, ?, 'SUCCESS (DEMO)', ?, ?)
            """, (
                ticket_id, fare, payment_method.get(),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Simulated payment only; no real money transferred"
            ))
            conn.commit()

            messagebox.showinfo(
                "Booking & Demo Payment Successful",
                f"Ticket booked successfully!\n"
                f"Ticket ID: {ticket_id}\n"
                f"Train: {train[0]}\n"
                f"Journey Date: {date}\n"
                f"Ticket Fare: Rs. {fare:.2f}\n"
                f"Payment Method: {payment_method.get()}\n"
                f"Payment Status: SUCCESS (DEMO)\n\n"
                "Demo only: no real money was transferred."
            )

            passenger_id.delete(0, tk.END)
            train_id.delete(0, tk.END)
            journey_date.delete(0, tk.END)

        except ValueError:
            messagebox.showerror(
                "Error",
                "Enter valid IDs and date in YYYY-MM-DD format"
            )

    tk.Button(
        content,
        text="Book Ticket + Demo Payment",
        command=book_ticket,
        bg="#2471a3",
        fg="white",
        font=("Arial", 11, "bold")
    ).grid(row=5, column=1, pady=15)


# ---------------- 4. TICKET CANCELLATION ----------------

def ticket_cancellation():
    clear_screen()

    tk.Label(
        content,
        text="Ticket Cancellation",
        font=("Arial", 17, "bold"),
        bg="#eaf2f8"
    ).pack(pady=20)

    tk.Label(
        content,
        text="Enter Ticket ID:",
        bg="#eaf2f8",
        font=("Arial", 11)
    ).pack(pady=5)

    ticket_id = tk.Entry(content, font=("Arial", 11))
    ticket_id.pack(pady=5)

    def cancel():
        value = ticket_id.get().strip()

        try:
            value = int(value)

            cursor.execute(
                "SELECT ticket_id, fare FROM tickets WHERE ticket_id=?",
                (value,)
            )
            ticket = cursor.fetchone()

            if ticket is None:
                messagebox.showerror("Error", "Ticket not found")
                return

            confirm = messagebox.askyesno(
                "Confirm Cancellation",
                "Are you sure you want to cancel this ticket?"
            )

            if confirm:
                from datetime import datetime
                cursor.execute("""
                    INSERT INTO finance_transactions
                    (ticket_id, transaction_type, amount, payment_method,
                     payment_status, transaction_date, notes)
                    VALUES (?, 'REFUND', ?, 'N/A', 'RECORDED (DEMO)', ?, ?)
                """, (
                    ticket[0], ticket[1],
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Demo refund record only; no real money refunded"
                ))
                cursor.execute(
                    "DELETE FROM tickets WHERE ticket_id=?",
                    (value,)
                )
                conn.commit()

                messagebox.showinfo(
                    "Cancellation Recorded",
                    f"Ticket cancelled successfully.\n"
                    f"Demo refund record: Rs. {ticket[1]:.2f}\n"
                    "No real money was refunded."
                )
                ticket_id.delete(0, tk.END)

        except ValueError:
            messagebox.showerror(
                "Error", "Enter a valid numeric Ticket ID"
            )

    tk.Button(
        content,
        text="Cancel Ticket",
        command=cancel,
        bg="#c0392b",
        fg="white",
        font=("Arial", 11, "bold")
    ).pack(pady=15)


# ---------------- 5. FARE CALCULATION ----------------

def fare_calculation():
    clear_screen()

    tk.Label(
        content,
        text="Ticket Fare Calculation",
        font=("Arial", 17, "bold"),
        bg="#eaf2f8"
    ).pack(pady=15)

    tk.Label(
        content,
        text="Enter Train ID:",
        bg="#eaf2f8",
        font=("Arial", 11)
    ).pack(pady=5)

    train_id = tk.Entry(content, font=("Arial", 11))
    train_id.pack(pady=5)

    def calculate():
        try:
            tid = int(train_id.get().strip())

            cursor.execute("""
            SELECT train_name, source, destination, fare
            FROM trains WHERE train_id=?
            """, (tid,))

            train = cursor.fetchone()

            if train is None:
                messagebox.showerror("Error", "Train ID not found")
                return

            messagebox.showinfo(
                "Fare Details",
                f"Train: {train[0]}\n"
                f"Source: {train[1]}\n"
                f"Destination: {train[2]}\n"
                f"Ticket Fare: Rs. {train[3]:.2f}"
            )

        except ValueError:
            messagebox.showerror("Error", "Enter a valid Train ID")

    tk.Button(
        content,
        text="Calculate Fare",
        command=calculate,
        bg="#239b56",
        fg="white",
        font=("Arial", 11, "bold")
    ).pack(pady=15)


# ---------------- 6. PASSENGER LIST ----------------

def passenger_list():
    clear_screen()

    tk.Label(
        content,
        text="Passenger and Booking List",
        font=("Arial", 17, "bold"),
        bg="#eaf2f8"
    ).pack(pady=10)

    tree = ttk.Treeview(
        content,
        columns=(
            "Ticket ID",
            "Passenger ID",
            "Name",
            "Train",
            "Source",
            "Destination",
            "Date",
            "Fare"
        ),
        show="headings",
        height=15
    )

    for col in (
        "Ticket ID", "Passenger ID", "Name", "Train",
        "Source", "Destination", "Date", "Fare"
    ):
        tree.heading(col, text=col)
        tree.column(col, width=100)

    tree.pack(fill="both", expand=True, pady=10)

    cursor.execute("""
    SELECT
        tickets.ticket_id,
        passengers.passenger_id,
        passengers.name,
        trains.train_name,
        trains.source,
        trains.destination,
        tickets.journey_date,
        tickets.fare
    FROM tickets
    JOIN passengers
        ON tickets.passenger_id = passengers.passenger_id
    JOIN trains
        ON tickets.train_id = trains.train_id
    ORDER BY tickets.ticket_id
    """)

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)


# ---------------- 7. DAILY FINANCE LIST ----------------

def daily_finance_list():
    clear_screen()
    tk.Label(content, text="Daily Finance List",
             font=("Arial", 17, "bold"), bg="#eaf2f8").pack(pady=10)

    from datetime import datetime
    filter_frame = tk.Frame(content, bg="#eaf2f8")
    filter_frame.pack(pady=5)
    tk.Label(filter_frame, text="Date (YYYY-MM-DD):",
             font=("Arial", 10), bg="#eaf2f8").grid(row=0, column=0, padx=5)

    date_entry = tk.Entry(filter_frame, font=("Arial", 10), width=14)
    date_entry.grid(row=0, column=1, padx=5)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    columns = ("Txn ID", "Ticket ID", "Type", "Amount", "Method", "Status", "Date/Time")
    tree = ttk.Treeview(content, columns=columns, show="headings", height=12)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=105, anchor="center")
    tree.pack(fill="both", expand=True, pady=10)

    totals_label = tk.Label(content, text="", font=("Arial", 11, "bold"),
                            bg="#eaf2f8", justify="left")
    totals_label.pack(pady=5)

    def load_report():
        report_date = date_entry.get().strip()
        try:
            datetime.strptime(report_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid Date", "Use YYYY-MM-DD format.")
            return

        for item in tree.get_children():
            tree.delete(item)

        cursor.execute("""
            SELECT transaction_id, ticket_id, transaction_type, amount,
                   payment_method, payment_status, transaction_date
            FROM finance_transactions
            WHERE substr(transaction_date, 1, 10)=?
            ORDER BY transaction_id DESC
        """, (report_date,))
        rows = cursor.fetchall()

        collections = sum(row[3] for row in rows if row[2] == "COLLECTION")
        refunds = sum(row[3] for row in rows if row[2] == "REFUND")
        for row in rows:
            tree.insert("", tk.END, values=(
                row[0], row[1] if row[1] is not None else "-",
                row[2], f"Rs. {row[3]:.2f}", row[4], row[5], row[6]
            ))

        totals_label.config(
            text=f"Date: {report_date}    Transactions: {len(rows)}\n"
                 f"Total Collections: Rs. {collections:.2f}    "
                 f"Demo Refunds: Rs. {refunds:.2f}    "
                 f"Net Collection: Rs. {collections - refunds:.2f}\n"
                 "Demo records only; not actual bank/payment transactions."
        )

    tk.Button(filter_frame, text="Show Report", command=load_report,
              bg="#2471a3", fg="white", font=("Arial", 10, "bold")
              ).grid(row=0, column=2, padx=8)
    load_report()


# ---------------- LOGIN, CLIENT BOARD, AGENT BOARD ----------------

menu_frame = tk.Frame(root, bg="#d6eaf8")
# Menu is displayed only after a successful login.

current_role = None


def show_menu_buttons():
    for widget in menu_frame.winfo_children():
        widget.destroy()

    if current_role == "Agent":
        menu_buttons = [
            ("Passenger Registration", passenger_registration),
            ("Train Details", train_management),
            ("Ticket Booking", ticket_booking),
            ("Ticket Cancellation", ticket_cancellation),
            ("Fare Calculation", fare_calculation),
            ("Passenger List", passenger_list),
            ("Daily Finance List", daily_finance_list),
            ("Main Menu", home),
            ("Logout", logout)
        ]
    else:
        # Client board: passenger-facing features only; train management is agent-only.
        menu_buttons = [
            ("Passenger Registration", passenger_registration),
            ("Ticket Booking", ticket_booking),
            ("Ticket Cancellation", ticket_cancellation),
            ("Fare Calculation", fare_calculation),
            ("Passenger List", passenger_list),
            ("Main Menu", home),
            ("Logout", logout)
        ]

    for index, (label, command) in enumerate(menu_buttons):
        tk.Button(
            menu_frame, text=label, command=command,
            font=("Arial", 10, "bold"), bg="#1f618d", fg="white",
            width=18, height=2
        ).grid(row=index // 4, column=index % 4, padx=6, pady=6)


def show_home_page():
    clear_screen()
    heading = "Agent Dashboard" if current_role == "Agent" else "Client Dashboard"
    tk.Label(
        content, text=f"Welcome to Railway Reservation System\n{heading}",
        font=("Arial", 19, "bold"), bg="#eaf2f8", fg="#154360",
        justify="center"
    ).pack(pady=35)
    if current_role == "Agent":
        details = "Manage passengers, trains, bookings, cancellations, fares and passenger lists."
    else:
        details = "Register passenger details, book/cancel tickets and check train fares."
    tk.Label(content, text=details, font=("Arial", 12), bg="#eaf2f8",
             wraplength=650, justify="center").pack(pady=10)


def home():
    show_home_page()


def logout():
    global current_role
    current_role = None
    menu_frame.pack_forget()
    show_login_portal()


def show_login_portal():
    clear_screen()
    tk.Label(content, text="LOGIN / REGISTER", font=("Arial", 20, "bold"),
             bg="#eaf2f8", fg="#154360").pack(pady=20)
    tk.Label(content, text="Choose your portal", font=("Arial", 12),
             bg="#eaf2f8").pack(pady=8)
    buttons = tk.Frame(content, bg="#eaf2f8")
    buttons.pack(pady=15)
    tk.Button(buttons, text="CLIENT LOGIN", command=lambda: show_login_form("Client"),
              font=("Arial", 12, "bold"), bg="#1f618d", fg="white",
              width=18, height=2).grid(row=0, column=0, padx=12, pady=8)
    tk.Button(buttons, text="CLIENT REGISTER", command=show_client_register,
              font=("Arial", 12, "bold"), bg="#239b56", fg="white",
              width=18, height=2).grid(row=0, column=1, padx=12, pady=8)
    tk.Button(buttons, text="AGENT LOGIN", command=lambda: show_login_form("Agent"),
              font=("Arial", 12, "bold"), bg="#7d3c98", fg="white",
              width=18, height=2).grid(row=1, column=0, columnspan=2, padx=12, pady=8)
    tk.Label(content, text="Demo Agent Login: username = agent | password = agent123",
             font=("Arial", 10), bg="#eaf2f8", fg="#555555").pack(pady=15)


def show_login_form(role):
    clear_screen()
    tk.Label(content, text=f"{role} Login", font=("Arial", 18, "bold"),
             bg="#eaf2f8", fg="#154360").grid(row=0, column=0, columnspan=2, pady=18)
    create_label("Username:", 1)
    username_entry = create_entry(1)
    create_label("Password:", 2)
    password_entry = tk.Entry(content, font=("Arial", 11), width=30, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=8)

    def login():
        global current_role
        username = username_entry.get().strip()
        password = password_entry.get()
        if not username or not password:
            messagebox.showerror("Login Error", "Enter username and password")
            return
        if role == "Agent":
            if username == "agent" and password == "agent123":
                current_role = "Agent"
            else:
                messagebox.showerror("Login Error", "Invalid agent username or password")
                return
        else:
            cursor.execute("SELECT user_id FROM user_accounts WHERE username=? AND password=? AND role='Client'",
                           (username, password))
            if cursor.fetchone() is None:
                messagebox.showerror("Login Error", "Client account not found or password is incorrect")
                return
            current_role = "Client"
        menu_frame.pack(fill="x", padx=15, pady=5, before=content)
        show_menu_buttons()
        show_home_page()

    tk.Button(content, text="Sign In", command=login, bg="#e67e22", fg="white",
              font=("Arial", 11, "bold"), width=18).grid(row=3, column=1, pady=12)
    tk.Button(content, text="Back", command=show_login_portal, bg="#566573", fg="white",
              font=("Arial", 10, "bold"), width=12).grid(row=4, column=1, pady=5)


def show_client_register():
    clear_screen()
    tk.Label(content, text="Create Client Account", font=("Arial", 18, "bold"),
             bg="#eaf2f8", fg="#154360").grid(row=0, column=0, columnspan=2, pady=18)
    create_label("Choose Username:", 1)
    username_entry = create_entry(1)
    create_label("Choose Password:", 2)
    password_entry = tk.Entry(content, font=("Arial", 11), width=30, show="*")
    password_entry.grid(row=2, column=1, padx=10, pady=8)
    create_label("Confirm Password:", 3)
    confirm_entry = tk.Entry(content, font=("Arial", 11), width=30, show="*")
    confirm_entry.grid(row=3, column=1, padx=10, pady=8)

    def register_account():
        username = username_entry.get().strip()
        password = password_entry.get()
        confirm = confirm_entry.get()
        if not username or not password or not confirm:
            messagebox.showerror("Error", "Fill all fields")
            return
        if len(username) < 3 or len(password) < 4:
            messagebox.showerror("Error", "Username must be 3+ characters and password 4+ characters")
            return
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        try:
            cursor.execute("INSERT INTO user_accounts (username, password, role) VALUES (?, ?, 'Client')",
                           (username, password))
            conn.commit()
            messagebox.showinfo("Success", "Client account created. You can now log in.")
            show_login_form("Client")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This username already exists. Choose another.")

    tk.Button(content, text="Create Account", command=register_account, bg="#239b56", fg="white",
              font=("Arial", 11, "bold"), width=18).grid(row=4, column=1, pady=12)
    tk.Button(content, text="Back", command=show_login_portal, bg="#566573", fg="white",
              font=("Arial", 10, "bold"), width=12).grid(row=5, column=1, pady=5)


def close_app():
    conn.close()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)
show_login_portal()
root.mainloop()