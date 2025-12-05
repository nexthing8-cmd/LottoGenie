from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime, timedelta
import math
from typing import Optional

from src.database import get_connection
from src.analyst import run_analyst
from src.visualizer import get_frequency_data, get_trend_data
from src.auth import (
    create_user, authenticate_user, create_access_token, 
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Ensure templates directory exists
import os
if not os.path.exists("templates"):
    os.makedirs("templates")

# Auth Routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(username: str = Form(...), password: str = Form(...)):
    if create_user(username, password):
        return JSONResponse(content={"message": "User created successfully"}, status_code=200)
    else:
        raise HTTPException(status_code=400, detail="Username already exists")

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user['username']}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Helper to get user from cookie (for web pages)
async def get_current_user_from_cookie(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = await get_current_user_from_cookie(request)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get latest result
    cursor.execute('SELECT * FROM history ORDER BY round_no DESC LIMIT 1')
    latest_result = cursor.fetchone()
    
    # Get next round prediction if exists
    # If user is logged in, show their predictions.
    recent_predictions = []
    if user:
        cursor.execute('SELECT * FROM my_predictions WHERE user_id = %s ORDER BY created_at DESC LIMIT 5', (user['id'],))
        recent_predictions = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "latest_result": latest_result,
        "predictions": recent_predictions,
        "user": user
    })

@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request):
    user = await get_current_user_from_cookie(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM my_predictions WHERE user_id = %s ORDER BY created_at DESC', (user['id'],))
    predictions = cursor.fetchall()
    conn.close()
    
    return templates.TemplateResponse("mypage.html", {"request": request, "user": user, "predictions": predictions})

@app.post("/delete_prediction/{id}")
async def delete_prediction(id: int, request: Request):
    user = await get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM my_predictions WHERE id = %s AND user_id = %s', (id, user['id']))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/mypage", status_code=303)

@app.post("/update_memo/{id}")
async def update_memo(id: int, request: Request, memo: str = Form(None)):
    user = await get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE my_predictions SET memo = %s WHERE id = %s AND user_id = %s', (memo, id, user['id']))
    conn.commit()
    conn.close()
    
    return RedirectResponse(url="/mypage", status_code=303)

@app.post("/delete_account")
async def delete_account(request: Request):
    user = await get_current_user_from_cookie(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    conn = get_connection()
    try:
        cursor = conn.cursor()
        
        # 1. Delete associated predictions
        cursor.execute('DELETE FROM my_predictions WHERE user_id = %s', (user['id'],))
        
        # 2. Delete user
        cursor.execute('DELETE FROM users WHERE id = %s', (user['id'],))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete account")
    finally:
        conn.close()
    
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, page: int = 1, limit: int = 10, search_round: Optional[int] = None):
    user = await get_current_user_from_cookie(request)
    
    # Validate limit to avoid abuse
    if limit not in [10, 25, 50]:
        limit = 10

    conn = get_connection()
    cursor = conn.cursor()
    
    if search_round:
        # Search specific round
        cursor.execute('SELECT * FROM history WHERE round_no = %s', (search_round,))
        history_items = cursor.fetchall()
        total_pages = 1
        current_page = 1
        total_count = len(history_items)
    else:
        # Normal pagination
        offset = (page - 1) * limit
        
        # Get total count
        cursor.execute('SELECT COUNT(*) as count FROM history')
        total_count = cursor.fetchone()['count']
        total_pages = math.ceil(total_count / limit)
        current_page = page
        
        # Get items
        cursor.execute('SELECT * FROM history ORDER BY round_no DESC LIMIT %s OFFSET %s', (limit, offset))
        history_items = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("history.html", {
        "request": request, 
        "user": user, 
        "history": history_items,
        "page": current_page,
        "total_pages": total_pages,
        "limit": limit,
        "search_round": search_round if search_round else ""
    })

@app.get("/analysis", response_class=HTMLResponse)
async def analysis(request: Request):
    user = await get_current_user_from_cookie(request)
    freq_data = get_frequency_data()
    trend_data = get_trend_data()
    
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "freq_data": freq_data,
        "trend_data": trend_data,
        "user": user
    })

@app.post("/predict")
async def generate_prediction(user: dict = Depends(get_current_user)):
    # Now requires login (Bearer token in header)
    # But our web frontend uses cookies.
    # We need a dependency that checks cookie if header is missing, or frontend needs to send header.
    # For simplicity in this demo, let's allow cookie auth for this endpoint too if called from browser JS.
    pass

# Wrapper for web-based prediction call
@app.post("/predict_web")
async def generate_prediction_web(request: Request):
    user = await get_current_user_from_cookie(request)
    if not user:
         raise HTTPException(status_code=401, detail="Not authenticated")
    
    print(f"User ID: {user['id']}") # Debug
    run_analyst(user_id=user['id'])
    return {"message": "Prediction generated successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
