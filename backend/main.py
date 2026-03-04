# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import Session, relationship
from pydantic import BaseModel
from typing import Optional
import random
import httpx
from database import SessionLocal, engine, Base

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