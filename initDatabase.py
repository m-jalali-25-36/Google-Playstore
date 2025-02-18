import pandas as pd
import pyodbc

# تنظیمات اتصال به SQL Server
server = 'localhost'
db_name = 'GooglePlayStore'

connection_string = f'DRIVER={{SQL Server}};SERVER={server};Integrated Security=TrueTrusted_Connection=yes;'

conn = pyodbc.connect(connection_string, autocommit=True)
cursor = conn.cursor()

cursor.execute(f"IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '{db_name}') CREATE DATABASE {db_name};")
print("✔ Database created.")
conn.close()

connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={db_name};Integrated Security=True;Trusted_Connection=yes;'
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

# cursor.execute("DROP TABLE IF EXISTS AppCategories;")
# cursor.execute("DROP TABLE IF EXISTS Apps;")
# cursor.execute("DROP TABLE IF EXISTS Categories;")
# cursor.execute("DROP TABLE IF EXISTS Developers;")

# ایجاد جداول
cursor.execute("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Developers')
CREATE TABLE Developers (
    DeveloperID INT IDENTITY(1,1) PRIMARY KEY,
    DeveloperName NVARCHAR(255) UNIQUE,
    DeveloperEmail NVARCHAR(255),
    DeveloperWebsite NVARCHAR(500)
);
""")

cursor.execute("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Categories')
CREATE TABLE Categories (
    CategoryID INT IDENTITY(1,1) PRIMARY KEY,
    CategoryName NVARCHAR(100) UNIQUE NOT NULL
);
""")

cursor.execute("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'Apps') BEGIN
CREATE TABLE Apps (
    AppID NVARCHAR(255) PRIMARY KEY,
    AppName NVARCHAR(255) NOT NULL,
    Rating FLOAT CHECK (Rating BETWEEN 0 AND 5),
    RatingCount BIGINT CHECK (RatingCount >= 0),
    Installs BIGINT CHECK (Installs >= 0),
    MinInstalls BIGINT CHECK (MinInstalls >= 0),
    MaxInstalls BIGINT CHECK (MaxInstalls >= 0),
    Price DECIMAL(10,2) CHECK (Price >= 0),
    Currency NVARCHAR(10),
    Size NVARCHAR(50),
    MinAndroid NVARCHAR(50),
    DeveloperID INT,
    ContentRating NVARCHAR(50),
    PrivacyPolicy NVARCHAR(500),
    Released DATE,
    LastUpdated DATE,
    ScrapedTime DATETIME,
    Free BIT,
    AdSupported BIT,
    InAppPurchases BIT,
    EditorsChoice BIT,
    FOREIGN KEY (DeveloperID) REFERENCES Developers(DeveloperID),
);
CREATE INDEX idx_rating ON Apps(Rating);
CREATE INDEX idx_price ON Apps(Price);
CREATE INDEX idx_content_rating ON Apps(ContentRating);
CREATE INDEX idx_installs ON Apps(Installs);
CREATE INDEX idx_last_updated ON Apps(LastUpdated);
END
""")

cursor.execute("""
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'AppCategories')
CREATE TABLE AppCategories (
    AppID NVARCHAR(255),
    CategoryID INT,
    PRIMARY KEY (AppID, CategoryID),
    FOREIGN KEY (CategoryID) REFERENCES Categories(CategoryID),
    FOREIGN KEY (AppID) REFERENCES Apps(AppID)
);
""")


conn.commit()
print("✔ Tables and indexes were created successfully.")
