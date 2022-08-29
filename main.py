import models
import yfinance
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi import FastAPI, Request, Depends, BackgroundTasks
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from models import Stock

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

class StockRequest(BaseModel):
    symbol: str

def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close

@app.get("/")
def dashboard(request: Request, forward_pe = None, dividend_yield = None, ma50 = None, ma200 = None, db: Session = Depends(get_db)):
    """
    Displays the stock screener Dashboard
    """

    stocks = db.query(Stock) #?????

    if forward_pe:
        stocks = stocks.filter(Stock.forward_pe < forward_pe)

    if dividend_yield:
        stocks = stocks.filter(Stock.dividend_yield > dividend_yield)

    if ma50:
        stocks = stocks.filter(Stock.price > Stock.ma50)
    
    if ma200:
        stocks = stocks.filter(Stock.price > Stock.ma200)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "stocks": stocks,
        "dividend_yield": dividend_yield,
        "forward_pe": forward_pe,
        "ma50": ma50,
        "ma200": ma200
    })

def fetch_stock_data(id: int):
    db = SessionLocal()

    stock = db.query(Stock).filter(Stock.id == id).first()

    yahoo_data = yfinance.Ticker(stock.symbol)

    
    stock.price = yahoo_data.info['previousClose']
    stock.forward_pe = yahoo_data.info['forwardPE']
    stock.forward_eps = yahoo_data.info['forwardEps']
    stock.dividend_yield = yahoo_data.info['dividendYield']
    if stock.dividend_yield is not None:
        stock.dividend_yield = stock.dividend_yield * 100
    stock.ma50 = yahoo_data.info['fiftyDayAverage']
    stock.ma200 = yahoo_data.info['twoHundredDayAverage']
    
    db.add(stock)
    db.commit()


@app.post("/stock")
async def create_stock(stock_request: StockRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):  #Depends-function depends on getting session
    """
    Creates a stock and stores it in the DB
    """
    stock = Stock()
    stock.symbol = stock_request.symbol
    db.add(stock)
    db.commit()

    background_tasks.add_task(fetch_stock_data, stock.id)

    return {
        "code": "success",
        "message": "stock was added to the database"
    }
@app.post("/stock")

async def delete_stock(stock_request: StockRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):  #Depends-function depends on getting session
    """
    Deletes a stock and removes it from the DB
    """
    stock = Stock()
    stock.symbol = stock_request.symbol
    db.add(stock)
    db.delete(stock) #make sure deletes
    db.flush() #make sure completes deletion

    return {
        "code": "success",
        "message": "stock was removed to the database"
    }
