from werkzeug.security import generate_password_hash
import sqlite3

DB = "reservations.db"

with sqlite3.connect(DB) as con:
        # add apartments Whg 31.1 to Whg 31.5
        for i in range(1, 6):
            con.execute("INSERT INTO apartments (name) VALUES (?)",
                        (f"Whg 31.{i}",))

with sqlite3.connect(DB) as con:
        con.execute("INSERT INTO users (username, password, apartment_id) VALUES (?, ?, ?)",
                    ("alice", generate_password_hash("password123"), "1"))
        con.execute("INSERT INTO users (username, password, apartment_id) VALUES (?, ?, ?)",
                    ("bob", generate_password_hash("password456"), "2"))
        con.commit()