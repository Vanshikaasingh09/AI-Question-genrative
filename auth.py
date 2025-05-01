# auth.py

from fastapi import APIRouter, Form, HTTPException, Depends, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import jwt, JWTError, ExpiredSignatureError
from database import get_db_cursor, get_db_connection
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# ------------------- SIGNUP -------------------
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

# ------------------- LOGIN -------------------
@router.post("/login")
def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
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

    # Set JWT as HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production (HTTPS)
        samesite="Lax",
        max_age=3600
    )

    # ✅ Modified part — return the token to the client
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "✅ Login successful"
    }

# ------------------- GET CURRENT USER -------------------
@router.get("/me")
def read_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="❌ Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return {"username": username}
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="❌ Token expired")
    except JWTError:
        raise HTTPException(status_code=401, detail="❌ Invalid token")
