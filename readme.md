# Google Play Store Data Analysis

## Overview
This project analyzes Google Play Store data to provide insights into app categories, ratings, and trends. The dataset consists of over 2 million records and is processed using **SQL Server** and **Python**. The project includes database creation, data cleaning, API development, and a Streamlit dashboard for visualization.

## Project Structure
The project is divided into multiple Python scripts, each responsible for a specific task:

1. **Database Setup (`initDatabase.py`)**
   - Creates the SQL Server database and tables.
   
2. **Data Cleaning & Insertion (`importData.py`)**
   - Reads the dataset.
   - Cleans and standardizes the data.
   - Inserts cleaned data into the database.
   
3. **API (`api.py`)**
   - Provides endpoints for retrieving app data.
   - Enables filtering by category, rating, and other attributes.

4. **Dashboard (`dashboard.py`)**
   - Uses Streamlit to visualize app data.
   - Includes interactive filters and charts.

## Database Schema
The database consists of tables for apps, categories, and developers. The main table, `Apps`, contains the following columns:


## Indexing for Performance Optimization
Since the dataset contains over 2 million records, indexing is applied to improve query performance. Key indexing strategies include:
- **Clustered Index** on `App Id` (Primary Key)
- **Non-Clustered Indexes** on frequently filtered columns such as `Category`, `Rating`, and `Installs`
- **Covering Indexes** for optimizing specific queries
- **Partitioning** on `Released` year to speed up time-based analysis

## How to Run the Project
### Prerequisites
- **SQL Server** (Ensure the database is set up)
- **Python 3.x**
  ```sh
  pipenv install
  pipenv shell
  ```

### Steps to Execute
1. **Set Up Database:**
   ```sh
   py initDatabase.py
   ```
2. **Process & Insert Data:**
   ```sh
   py importData.py
   ```
3. **Run API Server:**
   ```sh
   py api.py
   ```
4. **Launch Dashboard:**
   ```sh
   py dashboard.py
   ```
   OR run all services together using:
   ```sh
   run.bat
   ```

