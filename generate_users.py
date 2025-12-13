# Generate 1,000 Saudi Arabian users
# Run: python scripts/generate_users.py

from faker import Faker
from datetime import datetime, timedelta
import json
import random
import sqlite3

fake = Faker('ar_SA')
Faker.seed(42)

SAUDI_REGIONS = [
    "الرياض", "مكة المكرمة", "المدينة المنورة", "الشرقية", "عسير",
    "الحدود الشمالية", "جازان", "نجران", "الباحة", "القصيم", "الجوف"
]

SAUDI_CITIES = [
    "الرياض", "جدة", "الدمام", "الخبر", "الطائف", "المدينة", "مكة",
    "القطيف", "الأحساء", "الرس", "الزلفي", "الخرج"
]

NEIGHBORHOODS = [
    "الشاطئ الغربي", "السلام", "الناصرية", "العليا", "الملك فهد",
    "الرمال", "الحمادية", "الفيحاء", "الضباط", "النرجس"
]

def generate_phone():
    return f"05{random.randint(10000000, 99999999)}"

def generate_iqama():
    return f"{random.choice([1, 2])}{random.randint(10000000000, 99999999999)}"

def generate_national_id():
    return f"1{random.randint(10000000000, 99999999999)}"

def generate_users(count=1000):
    users = []
    for i in range(count):
        is_iqama = random.choice([True, False])
        user = {
            "id": i + 1,
            "name_ar": fake.name(),
            "phone": generate_phone(),
            "national_id": generate_national_id() if not is_iqama else None,
            "iqama_id": generate_iqama() if is_iqama else None,
            "id_type": "Iqama" if is_iqama else "National ID",
            "dob": fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat(),
            "city": random.choice(SAUDI_CITIES),
            "street": f"شارع {random.randint(1, 50)}",
            "house": random.randint(1, 999),
            "postal": f"{random.randint(10000, 99999)}"
        }
        users.append(user)
    return users

def save_json(users, filename='backend/data/users.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    print(f"✅ Saved {len(users)} users to {filename}")

if __name__ == "__main__":
    print("🚀 Generating 1,000 users...")
    users = generate_users(1000)
    save_json(users)