import pandas as pd
import pyodbc
import numpy as np

# تنظیمات اتصال به SQL Server
server = 'localhost'
db_name = 'GooglePlayStore'

connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={db_name};Integrated Security=True;Trusted_Connection=yes;'
conn = pyodbc.connect(connection_string)
cursor = conn.cursor()


file_path = 'Google-Playstore.csv'
# file_path = '1.csv'
df = pd.read_csv(file_path)

df = df.drop_duplicates()
df = df.dropna(subset=['App Name', 'App Id', 'Category', 'Developer Id'])

df['App Name'] = df['App Name'].astype(str).str.strip()
df['App Id'] = df['App Id'].astype(str).str.strip()
df['Category'] = df['Category'].astype(str).str.strip().str.split(" & ")
df['Developer Id'] = df['Developer Id'].astype(str).str.strip()

df['Price'] = df['Price'].astype(float).fillna(0).round(2)
df['Rating'] = df['Rating'].astype(float).fillna(0).round(2)

df['Rating Count'] = df['Rating Count'].replace(r'[\+,]', '', regex=True).fillna(0).astype(int)
df['Installs'] = df['Installs'].astype(str).str.replace(r'[\+,]', '', regex=True).replace("nan", 0).fillna(0).astype(int)
df['Minimum Installs'] = df['Minimum Installs'].replace(r'[\+,]', '', regex=True).fillna(0).astype(int)
df['Maximum Installs'] = df['Maximum Installs'].replace(r'[\+,]', '', regex=True).fillna(0).astype(int)

df['Free'] = df['Free'].astype(bool)
df['Ad Supported'] = df['Ad Supported'].astype(bool)
df['In App Purchases'] = df['In App Purchases'].astype(bool)
df['Editors Choice'] = df['Editors Choice'].astype(bool)

df['Released'] = pd.to_datetime(df['Released'], format='%b %d, %Y', errors='coerce').apply(lambda x: x.strftime('%Y-%m-%d') if not pd.isna(x) else None)
df['Last Updated'] = pd.to_datetime(df['Last Updated'], format='%b %d, %Y', errors='coerce').dt.strftime('%Y-%m-%d')
df['Scraped Time'] = pd.to_datetime(df['Scraped Time'], errors='coerce')

# df['Developer Website'] = df['Developer Website'].apply(lambda x: str(x) if pd.notna(x) else None)
text_columns = ['Privacy Policy', 'Currency', 'Size', 'Minimum Android', 'Content Rating', 'Developer Website']
df[text_columns] = df[text_columns].fillna("").astype(str)


print("✓ Data cleared.")

developers = df[['Developer Id', 'Developer Website', 'Developer Email']].dropna(subset=['Developer Id']).dropna(subset=['Developer Email']).drop_duplicates(subset=['Developer Id'])
for index, row in developers.iterrows():
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM Developers WHERE DeveloperName = ?)
        INSERT INTO Developers (DeveloperName, DeveloperWebsite, DeveloperEmail) 
        VALUES (?, ?, ?)""",
        row['Developer Id'], row['Developer Id'], row['Developer Website'], row['Developer Email'])

conn.commit()
print("   ✓ Developer imported.")

categories = set(cat for sublist in df["Category"].dropna() for cat in sublist)
for category in categories:
    cursor.execute("""
        IF NOT EXISTS (SELECT 1 FROM Categories WHERE CategoryName = ?)
        INSERT INTO Categories (CategoryName) VALUES (?)""",
        category, category)

conn.commit()
print("   ✓ Category imported.")

for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO Apps (AppID, AppName, Rating, RatingCount, Installs, MinInstalls, MaxInstalls, Free, Price, Currency,
                          Size, MinAndroid, DeveloperID, Released, LastUpdated, ContentRating, PrivacyPolicy, AdSupported, 
                          InAppPurchases, EditorsChoice, ScrapedTime)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 
                (SELECT DeveloperID FROM Developers WHERE DeveloperName = ?), ?, ?, ?, ?, ?, ?, ?, ?)
""",
    row['App Id'], row['App Name'], float(row['Rating']), row['Rating Count'], row['Installs'],
    row['Minimum Installs'], row['Maximum Installs'], row['Free'], float(row['Price']), row['Currency'], row['Size'],
    row['Minimum Android'], row['Developer Id'], row['Released'], row['Last Updated'], row['Content Rating'],
    row['Privacy Policy'], row['Ad Supported'], row['In App Purchases'], row['Editors Choice'], row['Scraped Time'])

    app_id = row["App Id"]
    if isinstance(row["Category"], list):
        for category in row["Category"]:
            f2.write("({0},(SELECT CategoryID FROM Categories WHERE CategoryName = {1})),".format(app_id, category))
            cursor.execute("""
    MERGE INTO AppCategories AS target
    USING (SELECT ?, CategoryID FROM Categories WHERE CategoryName = ?) AS source (AppID, CategoryID)
    ON target.AppID = source.AppID AND target.CategoryID = source.CategoryID
    WHEN NOT MATCHED THEN
        INSERT (AppID, CategoryID) VALUES (source.AppID, source.CategoryID);
            """, (app_id, category))

    if index % 1000 == 0:
        conn.commit()
    

print("   ✓ App imported.")
print("✓ Data imported successfully.")
