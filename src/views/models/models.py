# src/models/models.py
from src.db.database import get_db_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_role(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT role FROM Users WHERE username = %s", (username,))
        role = cursor.fetchone()
        return role[0] if role else None
    finally:
        cursor.close()
        conn.close()

def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM Users WHERE username = %s", (username,))
        if cursor.fetchone():
            return False
        password_hash = hash_password(password)
        cursor.execute("INSERT INTO Users (username, password_hash, role) VALUES (%s, %s, %s)",
                       (username, password_hash, 'buyer'))
        conn.commit()
        return True
    finally:
        cursor.close()
        conn.close()

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM Users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return user and user[0] == hash_password(password), user[1] if user else None

def add_product(name, price, image_blob, quantity):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO Products (name, price, image, quantity) VALUES (%s, %s, %s, %s)",
            (name, price, image_blob, quantity)
        )
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# src/models/models.py
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT product_id, name, price, image, quantity FROM Products")
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

