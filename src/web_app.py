from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
import uvicorn
from datetime import datetime, timedelta
import math
from typing import Optional
from urllib.parse import quote

from src.database import get_connection
from src.analyst import run_analyst
from src.visualizer import get_frequency_data, get_trend_data, get_winner_count_data
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
    
    prizes = []
    if latest_result:
        # Get prizes for this round
        cursor.execute('SELECT * FROM prizes WHERE round_no = %s ORDER BY rank_no ASC', (latest_result['round_no'],))
        prizes = cursor.fetchall()

    # Get next round prediction if exists
    # If user is logged in, show their predictions.
    recent_predictions = []
    if user:
        cursor.execute('SELECT * FROM my_predictions WHERE user_id = %s AND is_deleted = 0 ORDER BY created_at DESC LIMIT 5', (user['id'],))
        recent_predictions = cursor.fetchall()
    
    conn.close()
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "latest_result": latest_result,
        "prizes": prizes,
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
    cursor.execute('SELECT * FROM my_predictions WHERE user_id = %s AND is_deleted = 0 ORDER BY created_at DESC', (user['id'],))
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
    cursor.execute('UPDATE my_predictions SET is_deleted = 1 WHERE id = %s AND user_id = %s', (id, user['id']))
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
        
        # 1. Soft delete associated predictions
        cursor.execute('UPDATE my_predictions SET is_deleted = 1 WHERE user_id = %s', (user['id'],))
        
        # 2. Soft delete user
        cursor.execute('UPDATE users SET is_deleted = 1 WHERE id = %s', (user['id'],))
        
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

@app.get("/history/{round_no}", response_class=HTMLResponse)
async def history_detail(request: Request, round_no: int):
    user = await get_current_user_from_cookie(request)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get round history
    cursor.execute('SELECT * FROM history WHERE round_no = %s', (round_no,))
    history_item = cursor.fetchone()
    
    if not history_item:
        conn.close()
        raise HTTPException(status_code=404, detail="Round not found")
        
    # Get prizes
    cursor.execute('SELECT * FROM prizes WHERE round_no = %s ORDER BY rank_no ASC', (round_no,))
    prizes = cursor.fetchall()
    
    # Get winning stores
    cursor.execute('SELECT * FROM winning_stores WHERE round_no = %s', (round_no,))
    stores = cursor.fetchall()
    
    # Add Naver Map URL for each store
    for store in stores:
        if store.get('address'):
            # 주소만 사용해서 네이버 지도 검색 URL 생성 (주소가 더 정확한 위치 정보 제공)
            search_query = store.get('address', '').strip()
            store['map_url'] = f"https://map.naver.com/v5/search/{quote(search_query)}"
        else:
            store['map_url'] = None
    
    conn.close()
    
    return templates.TemplateResponse("history_detail.html", {
        "request": request,
        "user": user,
        "item": history_item,
        "prizes": prizes,
        "stores": stores
    })

@app.get("/analysis", response_class=HTMLResponse)
async def analysis(request: Request):
    user = await get_current_user_from_cookie(request)
    freq_data = get_frequency_data()
    recent_freq_data = get_frequency_data(limit=20)
    trend_data = get_trend_data(last_n_rounds=None)  # 전체 데이터 로드
    winner_data = get_winner_count_data()
    
    return templates.TemplateResponse("analysis.html", {
        "request": request,
        "freq_data": freq_data,
        "recent_freq_data": recent_freq_data,
        "trend_data": trend_data,
        "winner_data": winner_data,
        "user": user
    })

@app.post("/predict")
async def generate_prediction(user: dict = Depends(get_current_user)):
    # Check for Saturday block time
    now = datetime.now()
    # Weekday: Monday is 0, Sunday is 6. Saturday is 5.
    if now.weekday() == 5:
        current_time = now.time()
        start_time = datetime.strptime("19:30:00", "%H:%M:%S").time()
        end_time = datetime.strptime("21:30:00", "%H:%M:%S").time()
        
        if start_time <= current_time <= end_time:
            raise HTTPException(
                status_code=400, 
                detail="매주 토요일 19:30 ~ 21:30 사이에는 복권 발행 마감으로 인해 예측 번호를 생성할 수 없습니다."
            )

    run_analyst(user_id=user['id'])
    return {"message": "Prediction generated successfully"}

# Wrapper for web-based prediction call
@app.post("/predict_web")
async def generate_prediction_web(request: Request):
    user = await get_current_user_from_cookie(request)
    if not user:
         raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check for Saturday block time
    now = datetime.now()
    if now.weekday() == 5:
        current_time = now.time()
        start_time = datetime.strptime("19:30:00", "%H:%M:%S").time()
        end_time = datetime.strptime("21:30:00", "%H:%M:%S").time()
        
        if start_time <= current_time <= end_time:
             # Return JSON response with error logic for frontend to handle
             return JSONResponse(
                 status_code=400, 
                 content={"detail": "매주 토요일 19:30 ~ 21:30 사이에는 복권 발행 마감으로 인해 예측 번호를 생성할 수 없습니다."}
             )
    
    print(f"User ID: {user['id']}") # Debug
    run_analyst(user_id=user['id'])
    return {"message": "Prediction generated successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
