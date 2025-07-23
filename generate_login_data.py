import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

def generate_login_data(num_records=1000):
    data = []
    base_time = datetime.now() - timedelta(days=1)

    for _ in range(num_records):
        timestamp = base_time + timedelta(seconds=random.randint(0, 86400))
        user_id = f"user_{random.randint(1, 50)}"
        ip_address = fake.ipv4_public()
        geo_location = fake.country()
        login_success = random.choices([0, 1], weights=[0.1, 0.9])[0]
        device = random.choice(["Windows", "Mac", "Android", "iOS", "Linux"])
        attempt_count = random.randint(1, 5) if login_success else random.randint(5, 20)

        data.append({
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "user_id": user_id,
            "ip_address": ip_address,
            "geo_location": geo_location,
            "login_success": login_success,
            "device": device,
            "attempt_count": attempt_count
        })

    df = pd.DataFrame(data)
    df.to_csv("data/login_logs.csv", index=False)
    print("[✔] Generated data/login_logs.csv with", num_records, "records.")

if __name__ == "__main__":
    generate_login_data(50000)
