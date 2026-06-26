from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import bcrypt
from jose import jwt
import sqlite3

router = APIRouter()

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"



# Create database if it doesn't exist
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE,
    password TEXT
)
""") 
cursor.execute("""
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT,
    query TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()


class User(BaseModel):
    email: str
    password: str 

class SearchHistory(BaseModel):
    email: str
    query: str


@router.post("/auth/register")
def register(user: User):

    hashed_password = bcrypt.hashpw(
    user.password.encode("utf-8"),
    bcrypt.gensalt()
).decode("utf-8")

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (user.email, hashed_password)
        )
        conn.commit()

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400,
                            detail="User already exists")

    finally:
        conn.close()

    return {"message": "User registered successfully"}


@router.post("/auth/login")
def login(user: User):

    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password FROM users WHERE email=?",
        (user.email,)
    )

    result = cursor.fetchone()
    conn.close()

    if not result:
        raise HTTPException(status_code=401,
                            detail="Invalid credentials")

    stored_password = result[0]

    if not bcrypt.checkpw(
    user.password.encode("utf-8"),
    stored_password.encode("utf-8")
):
        raise HTTPException(status_code=401,
                            detail="Invalid credentials")

    token = jwt.encode(
        {"sub": user.email},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    } 
@router.post("/history")
def save_history(item: SearchHistory):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO search_history (email, query) VALUES (?, ?)",
        (item.email, item.query)
    )

    conn.commit()
    conn.close()

    return {"message": "Search saved"}


@router.get("/history/{email}")
def get_history(email: str):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT query, created_at
        FROM search_history
        WHERE email = ?
        ORDER BY created_at DESC
        LIMIT 5
        """,
        (email,)
    )

    rows = cursor.fetchall()
    conn.close()

    history = [
        {
            "query": row[0],
            "created_at": row[1]
        }
        for row in rows
    ]

    return {"history": history}