# backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import random
import httpx
from database import SessionLocal, engine, Base

# 建立資料表
Base.metadata.create_all(bind=engine)

app = FastAPI()

# ==================== CORS 設定 ====================
# 允許前端 (如 localhost:5173) 跨網域來存取我們的 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 開發階段先允許所有來源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 取得資料庫連線的依賴函式
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==================== Pydantic 資料模型 ====================
class FlightSearchRequest(BaseModel):
    departure: str
    destination: str
    departDate: str
    returnDate: Optional[str] = None
    passengers: int

# ==================== API 路由 ====================
@app.get("/")
def read_root():
    return {
        "message": "旅遊網站後端已啟動，且資料庫連線成功！",
        "status": "success"
    }

# ✈️ 模擬機票搜尋 API (Mock API)
@app.post("/api/flights/search")
def search_mock_flights(request: FlightSearchRequest):
    try:
        # 準備一些假的航空公司與航班代碼
        airlines_pool = [
            {"name": "星宇航空 (STARLUX)", "code": "JX"},
            {"name": "長榮航空 (EVA Air)", "code": "BR"},
            {"name": "中華航空 (China Airlines)", "code": "CI"},
            {"name": "台灣虎航 (Tigerair)", "code": "IT"},
            {"name": "日本航空 (JAL)", "code": "JL"}
        ]
        
        mock_flights = []
        
        # 根據旅客人數隨機產生 5 筆看起來很真的機票資料
        for i in range(5):
            airline = random.choice(airlines_pool)
            # 隨機產生機票價格 (單人 5000 ~ 15000 不等，並乘上人數)
            base_price = random.randint(5000, 15000)
            total_price = base_price * request.passengers
            
            flight_data = {
                "id": f"FLIGHT_{i+100}",
                "airline": airline["name"],
                "flight_number": f"{airline['code']}{random.randint(100, 899)}",
                "departure": request.departure.upper(),
                "destination": request.destination.upper(),
                "depart_date": request.departDate,
                "return_date": request.returnDate,
                "passengers": request.passengers,
                "total_price_TWD": total_price,
                "currency": "TWD"
            }
            mock_flights.append(flight_data)
            
        # 模擬依照價格由低到高排序
        mock_flights.append({
             "id": "FLIGHT_CHEAPEST",
             "airline": "神秘廉航 (Mystery Air)",
             "flight_number": f"XX{random.randint(10, 99)}",
             "departure": request.departure.upper(),
             "destination": request.destination.upper(),
             "depart_date": request.departDate,
             "return_date": request.returnDate,
             "passengers": request.passengers,
             "total_price_TWD": 3999 * request.passengers, # 最便宜的防呆價格
             "currency": "TWD"
        })
        
        # 依照價格低到高排序
        mock_flights = sorted(mock_flights, key=lambda x: x["total_price_TWD"])

        return {
            "status": "success",
            "source": "Mock API (模擬資料)",
            "data": mock_flights
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"後端模擬資料發生錯誤: {str(e)}")


# 💰 真實即時匯率 API
@app.get("/api/exchange")
async def calculate_exchange(amount: float, from_currency: str, to_currency: str):
    # 使用免費開源的匯率 API，以 from_currency 為基準幣別
    url = f"https://open.er-api.com/v6/latest/{from_currency}"
    
    try:
        # 使用 httpx 發送非同步請求
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data = response.json()
            
            if data.get("result") == "success":
                rates = data.get("rates", {})
                
                if to_currency not in rates:
                    raise HTTPException(status_code=400, detail="不支援的目標幣別")
                
                # 取得目標匯率並計算總金額
                rate = rates[to_currency]
                converted_amount = round(amount * rate, 2) # 四捨五入到小數點第二位
                
                return {
                    "status": "success",
                    "from_currency": from_currency,
                    "to_currency": to_currency,
                    "original_amount": amount,
                    "converted_amount": converted_amount,
                    "rate": rate,
                    "last_update": data.get("time_last_update_utc") # API 最後更新時間
                }
            else:
                raise HTTPException(status_code=400, detail="無法取得即時匯率")
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯率伺服器連線失敗: {str(e)}")