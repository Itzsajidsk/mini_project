import sys
import pymysql
from passlib.hash import sha256_crypt

DB = dict(host='localhost', user='root', password='root', db='flames_login', charset='utf8mb4')

def create_user(username: str, raw_password: str):
    hashed = sha256_crypt.hash(raw_password)
    conn = pymysql.connect(**DB)
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cur.fetchone():
                print(f"User '{username}' already exists.")
                return
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
            conn.commit()
            print(f"Created user '{username}' with provided password.")
    except Exception as e:
        print("Error:", e)
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python create_dummy_user.py <username> <password>")
        sys.exit(1)
    create_user(sys.argv[1], sys.argv[2])