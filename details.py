import pandas as pd

# مسیر فایل CSV (آن را به مسیر دیتاست خود تغییر دهید)
file_path = 'Google-Playstore.csv'

# خواندن دیتاست
df = pd.read_csv(file_path)

# تعداد کل رکوردها
total_records = df.shape[0]

# نمایش نام ستون‌ها
columns = df.columns.tolist()

# بررسی تعداد مقادیر NaN در هر ستون
missing_values = df.isna().sum()

# نمایش نوع داده هر ستون
data_types = df.dtypes

# نمایش گزارش نهایی
print(f"total_records: {total_records}\n")
print("columns:")
print(columns, "\n")
print("missing_values:")
print(missing_values, "\n")
print("data_types:")
print(data_types, "\n")
