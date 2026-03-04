import os
import json
import httpx
import random
import asyncio
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel

# 引入 dotenv 與 Google Gemini 套件
import dotenv
import google.generativeai as genai

from database import SessionLocal, engine, Base

# ==================== Gemini AI 設定 ====================
# 載入 .env 檔案中的環境變數
dotenv.load_dotenv()

# 設定 Gemini API Key (請確保你有在 backend 資料夾下建立 .env 檔案並填入 GEMINI_API_KEY)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 初始化模型 (選用 flash 版本，速度最快)
ai_model = genai.GenerativeModel('gemini-1.5-flash')


# ==================== 資料庫模型 (DB Models) ====================
class DayPlanDB(Base):
    __tablename__ = "day_plans"
    id = Column(Integer, primary_key=True, index=True)
    day_number = Column(Integer)
    date = Column(String, default="")
    # 關聯到活動，當天刪除時底下的活動一併刪除
    activities = relationship("ActivityDB", back_populates="day", cascade="all, delete-orphan")

class ActivityDB(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    time = Column(String, default="10:00")
    title = Column(String)
    location = Column(String)
    day_id = Column(Integer, ForeignKey("day_plans.id"))
    day = relationship("DayPlanDB", back_populates="activities")

# 建立資料表
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== Pydantic 資料驗證模型 ====================
class DayPlanCreate(BaseModel):
    day_number: int
    date: str

class DayPlanUpdate(BaseModel):
    date: str

class ActivityCreate(BaseModel):
    day_id: int
    time: str
    title: str
    location: str

class ActivityUpdate(BaseModel):
    time: str
    title: str
    location: str

class FlightSearchRequest(BaseModel):
    departure: str
    destination: str
    departDate: str
    returnDate: Optional[str] = None
    passengers: int

class AIGenerateRequest(BaseModel):
    destination: str
    days: int
    start_date: str

# ==================== 行程表 CRUD API ====================

# 1. 取得所有行程
@app.get("/api/itinerary")
def get_itinerary(db: Session = Depends(get_db)):
    days = db.query(DayPlanDB).order_by(DayPlanDB.day_number).all()
    result = []
    for day in days:
        result.append({
            "id": day.id,
            "dayNumber": day.day_number,
            "date": day.date,
            # 確保傳給前端的活動會依照時間自動排序
            "activities": [
                {
                    "id": act.id,
                    "time": act.time,
                    "title": act.title,
                    "location": act.location
                } for act in sorted(day.activities, key=lambda x: x.time)
            ]
        })
    return result

# 2. 新增一天
@app.post("/api/itinerary/days")
def create_day(day: DayPlanCreate, db: Session = Depends(get_db)):
    new_day = DayPlanDB(day_number=day.day_number, date=day.date)
    db.add(new_day)
    db.commit()
    return {"status": "success"}

# 3. 更新日期
@app.put("/api/itinerary/days/{day_id}")
def update_day(day_id: int, day_data: DayPlanUpdate, db: Session = Depends(get_db)):
    day = db.query(DayPlanDB).filter(DayPlanDB.id == day_id).first()
    if day:
        day.date = day_data.date
        db.commit()
    return {"status": "success"}

# 4. 新增活動
@app.post("/api/itinerary/activities")
def create_activity(act: ActivityCreate, db: Session = Depends(get_db)):
    new_act = ActivityDB(time=act.time, title=act.title, location=act.location, day_id=act.day_id)
    db.add(new_act)
    db.commit()
    return {"status": "success"}

# 5. 更新活動
@app.put("/api/itinerary/activities/{act_id}")
def update_activity(act_id: int, act: ActivityUpdate, db: Session = Depends(get_db)):
    db_act = db.query(ActivityDB).filter(ActivityDB.id == act_id).first()
    if db_act:
        db_act.time = act.time
        db_act.title = act.title
        db_act.location = act.location
        db.commit()
    return {"status": "success"}

# 6. 刪除活動
@app.delete("/api/itinerary/activities/{act_id}")
def delete_activity(act_id: int, db: Session = Depends(get_db)):
    db_act = db.query(ActivityDB).filter(ActivityDB.id == act_id).first()
    if db_act:
        db.delete(db_act)
        db.commit()
    return {"status": "success"}

# 7. 真實 AI 智能排行程 (呼叫 Gemini API 並自動寫入資料庫)
@app.post("/api/itinerary/ai-generate")
async def generate_ai_itinerary(req: AIGenerateRequest, db: Session = Depends(get_db)):
    try:
        start_dt = datetime.strptime(req.start_date, "%Y-%m-%d")
        
        # 1. 精準的 Prompt 提示詞：要求 AI 扮演導遊，並嚴格限制輸出格式
        prompt = f"""
        你是一位專業的台灣旅遊規劃師。請為我規劃 {req.days} 天的【{req.destination}】旅遊行程。
        行程必須合理，考慮交通時間，並包含知名景點與在地美食。每天安排 3 到 4 個活動。
        
        請嚴格遵守以下規則：
        1. 絕對不要回傳任何 Markdown 語法 (如 ```json)。
        2. 絕對不要有任何開頭或結尾的問候語、解釋文字。
        3. 請直接回傳一個合法的 JSON 陣列 (Array)，格式必須完全符合以下結構：
        [
            {{
                "day_number": 1,
                "activities": [
                    {{"time": "09:00", "title": "活動標題", "location": "具體地點名稱"}}
                ]
            }}
        ]
        """
        
        # 2. 呼叫 Gemini 生成內容
        response = ai_model.generate_content(prompt)
        response_text = response.text.strip()
        
        # 3. 防呆處理：清除 AI 可能夾帶的 Markdown 標記
        if response_text.startswith("```"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
            
        # 4. 將 AI 回傳的純文字轉換為 Python 字典
        ai_itinerary_data = json.loads(response_text)

        # 5. 清除資料庫舊的行程 (為了讓畫面展示乾淨，實務上可做覆蓋或新增)
        db.query(DayPlanDB).delete()
        db.commit()

        # 6. 把 AI 給的資料結構化存入 PostgreSQL (或 SQLite)
        for day_data in ai_itinerary_data:
            day_num = day_data.get("day_number")
            # 算出當天的實際日期
            current_date = (start_dt + timedelta(days=day_num - 1)).strftime("%Y-%m-%d")
            
            # 建立天數紀錄
            new_day = DayPlanDB(day_number=day_num, date=current_date)
            db.add(new_day)
            db.commit()
            db.refresh(new_day)
            
            # 建立當天的所有活動
            for act in day_data.get("activities", []):
                new_act = ActivityDB(
                    time=act.get("time", "10:00"), 
                    title=act.get("title", "未命名行程"), 
                    location=act.get("location", "未定地點"), 
                    day_id=new_day.id
                )
                db.add(new_act)
                
        db.commit()
        return {"status": "success", "message": f"成功透過 AI 生成 {req.days} 天的 {req.destination} 行程"}

    except json.JSONDecodeError as e:
        print(f"JSON 解析失敗，AI 原始回傳內容:\n{response_text}")
        raise HTTPException(status_code=500, detail="AI 回傳的格式不正確，無法解析行程，請再試一次。")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== 其他 API (保留機票與匯率) ====================
@app.get("/")
def read_root():
    return {"message": "旅遊網站後端已啟動！", "status": "success"}

@app.post("/api/flights/search")
def search_mock_flights(request: FlightSearchRequest):
    return {"status": "success", "data": []}

@app.get("/api/exchange")
async def calculate_exchange(amount: float, from_currency: str, to_currency: str):
    url = f"https://open.er-api.com/v6/latest/{from_currency}"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            if data.get("result") == "success":
                rates = data.get("rates", {})
                if to_currency not in rates:
                    raise HTTPException(status_code=400, detail="不支援的目標幣別")
                rate = rates[to_currency]
                converted_amount = round(amount * rate, 2)
                return {
                    "status": "success",
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "original_amount": amount,
                    "converted_amount": converted_amount,
                    "rate": rate,
                    "last_update": data.get("time_last_update_utc")
                }
            else:
                raise HTTPException(status_code=400, detail="無法取得即時匯率")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"連線失敗: {str(e)}")