# auth.py

from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt
from database import get_db_cursor, get_db_connection
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta 



load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

@router.post("/signup")
def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    cursor, conn = get_db_cursor() 
    hashed_pw = pwd_context.hash(password)

    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                       (username, email, hashed_pw))
        conn.commit()
        return {"message": "✅ User registered successfully!"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    cursor, conn = get_db_cursor()  

   
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (form_data.username,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(status_code=400, detail="❌ Invalid username or password")

    hashed_password = result[0]

    if not pwd_context.verify(form_data.password, hashed_password):
        raise HTTPException(status_code=400, detail="❌ Invalid username or password")

    # Create JWT token
    access_token = jwt.encode(
        {"sub": form_data.username, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"access_token": access_token, "token_type": "bearer"}