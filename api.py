from fastapi import FastAPI, HTTPException, Query, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional

class AppResponse(BaseModel):
    AppId: str
    AppName: str
    Category: str
    Rating: Optional[float]
    RatingCount: Optional[int]
    Installs: Optional[int]
    Free: bool
    Price: Optional[float]
    ContentRating: Optional[str]

    class Config:
        orm_mode = True  
DATABASE_URL = "mssql+pyodbc://localhost/GooglePlayStore?driver=SQL+Server+Native+Client+11.0"

engine = create_engine(DATABASE_URL, connect_args={"trusted_connection": "yes"})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class App(Base):
    __tablename__ = 'Apps'

    AppId = Column(String, primary_key=True, index=True)
    AppName = Column(String)
    Category = Column(String)
    Rating = Column(Float, nullable=True)
    RatingCount = Column(Integer, nullable=True)
    Installs = Column(Integer, nullable=True)
    Free = Column(Boolean)
    Price = Column(Float, nullable=True)
    ContentRating = Column(String, nullable=True)

class Category(Base):
    __tablename__ = 'Categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

app = FastAPI()

DEFAULT_PAGE_SIZE = 100

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/apps/", response_model=List[AppResponse])
def get_apps(
    category: str = Query(None, description="Filter by category"),
    min_rating: float = Query(None, description="Minimum rating"),
    max_price: float = Query(None, description="Maximum price"),
    page: int = Query(1, description="Page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, description="Items per page"),
    db: Session = Depends(get_db)
):
    query = db.query(App).join(Category, Category.name == App.Category)

    if category:
        query = query.filter(Category.name == category)
    if min_rating:
        query = query.filter(App.Rating >= min_rating)
    if max_price is not None:
        query = query.filter(App.Price <= max_price)

    total_count = query.count()
    apps = query.offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "apps": apps
    }

@app.get("/apps/ratings/")
def get_ratings_analysis(db: Session = Depends(get_db)):
    result = (
        db.query(Category.name, func.avg(App.Rating).label("avg_rating"))
        .join(App, App.Category == Category.name)
        .group_by(Category.name)
        .all()
    )
    return [{"category": row[0], "average_rating": row[1]} for row in result]

@app.post("/apps/")
def add_app(app: App, db: Session = Depends(get_db)):
    db.add(app)
    db.commit()
    db.refresh(app)
    return {"message": "اپلیکیشن با موفقیت اضافه شد"}

@app.delete("/apps/{app_id}")
def delete_app(app_id: str, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.AppId == app_id).first()
    if app is None:
        raise HTTPException(status_code=404, detail="App not found")
    db.delete(app)
    db.commit()
    return {"message": "اپلیکیشن با موفقیت حذف شد"}

@app.put("/apps/{app_id}")
def update_app(app_id: str, app: App, db: Session = Depends(get_db)):
    existing_app = db.query(App).filter(App.AppId == app_id).first()
    if existing_app is None:
        raise HTTPException(status_code=404, detail="App not found")
    
    existing_app.AppName = app.AppName
    existing_app.Category = app.Category
    existing_app.Rating = app.Rating
    existing_app.RatingCount = app.RatingCount
    existing_app.Installs = app.Installs
    existing_app.Free = app.Free
    existing_app.Price = app.Price
    existing_app.ContentRating = app.ContentRating
    
    db.commit()
    db.refresh(existing_app)
    return {"message": "اپلیکیشن با موفقیت به‌روزرسانی شد"}
