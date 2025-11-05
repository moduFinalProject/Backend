import csv
from app.database import SessionLocal
from app.models import Code

def seed_codes_from_csv(csv_path: str):
    db = SessionLocal()
    try:
        with open(csv_path, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            codes = []
            for row in reader:
                code = Code(**row)
                codes.append(code)

            db.add_all(codes)
            db.commit()
            print(f"{len(codes)}개의 코드 데이터를 성공적으로 추가했습니다.")
    except Exception as e:
        db.rollback()
        print("에러 발생:", e)
    finally:
        db.close()

if __name__ == "__main__":
    seed_codes_from_csv("seed_data/codes.csv")
