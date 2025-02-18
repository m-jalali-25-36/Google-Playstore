from fastapi import FastAPI, Query, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date, ForeignKey, DECIMAL, BigInteger
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from pydantic import BaseModel, EmailStr, condecimal

# Database Connection
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://localhost/GooglePlayStore?driver=SQL+Server&Trusted_Connection=yes"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()

# Database Models
class Developer(Base):
    __tablename__ = "Developers"
    DeveloperID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    DeveloperName = Column(String(255), unique=True, nullable=False)
    DeveloperEmail = Column(String(255))
    DeveloperWebsite = Column(String(500))
    apps = relationship("Apps", back_populates="developer")

class Category(Base):
    __tablename__ = "Categories"
    CategoryID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    CategoryName = Column(String(100), unique=True, nullable=False)
    
class App(Base):
    __tablename__ = "Apps"
    AppID = Column(String(255), primary_key=True)
    AppName = Column(String(255), nullable=False)
    Rating = Column(Float)
    RatingCount = Column(BigInteger)
    Installs = Column(BigInteger)
    MinInstalls = Column(BigInteger)
    MaxInstalls = Column(BigInteger)
    Price = Column(DECIMAL(10,2))
    Currency = Column(String(10))
    Size = Column(String(50))
    MinAndroid = Column(String(50))
    DeveloperID = Column(Integer, ForeignKey("Developers.DeveloperID"))
    ContentRating = Column(String(50))
    PrivacyPolicy = Column(String(500))
    Released = Column(Date)
    LastUpdated = Column(Date)
    ScrapedTime = Column(Date)
    Free = Column(Boolean)
    AdSupported = Column(Boolean)
    InAppPurchases = Column(Boolean)
    EditorsChoice = Column(Boolean)
    developer = relationship("Developer", back_populates="apps")

class AppCategory(Base):
    __tablename__ = "AppCategories"
    AppID = Column(String(255), ForeignKey("Apps.AppID"), primary_key=True)
    CategoryID = Column(Integer, ForeignKey("Categories.CategoryID"), primary_key=True)

# Pydantic Models
class DeveloperCreate(BaseModel):
    DeveloperName: str
    DeveloperEmail: EmailStr
    DeveloperWebsite: str

class AppCreate(BaseModel):
    AppID: str
    AppName: str
    Rating: float
    RatingCount: int
    Installs: int
    Price: condecimal(max_digits=10, decimal_places=2)
    Currency: str
    Free: bool
    DeveloperID: int

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI App
app = FastAPI()

@app.post("/developers/")
def create_developer(dev: DeveloperCreate, db: Session = Depends(get_db)):
    developer = Developer(**dev.dict())
    db.add(developer)
    db.commit()
    db.refresh(developer)
    return developer

@app.post("/apps/")
def create_app(app_data: AppCreate, db: Session = Depends(get_db)):
    app = App(**app_data.dict())
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

@app.get("/apps/{app_id}")
def get_app(app_id: str, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.AppID == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app

@app.get("/apps/")
def get_apps(
    page: int = Query(1, alias="page", ge=1),
    page_size: int = Query(10, alias="page_size", le=100),
    category: str = None,
    rating: float = None,
    price: float = None,
    content_rating: str = None,
    db: Session = Depends(get_db)):
    query = db.query(App)

    if category:
        query = query.filter(App.Category == category)
    if rating:
        query = query.filter(App.Rating >= rating)
    if price:
        query = query.filter(App.Price <= price)
    if content_rating:
        query = query.filter(App.ContentRating == content_rating)

    query = query.order_by(App.LastUpdated.desc())  

    return {
        "page": page,
        "page_size": page_size,
        "total": query.count(),
        "apps": query.offset((page - 1) * page_size).limit(page_size).all()
    }


@app.get("/apps/{app_id}")
def get_app(app_id: str, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.AppID == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    return app

@app.delete("/apps/{app_id}")
def delete_app(app_id: str, db: Session = Depends(get_db)):
    app = db.query(App).filter(App.AppID == app_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="App not found")
    db.delete(app)
    db.commit()
    return {"message": f"App {app_id} deleted successfully"}


