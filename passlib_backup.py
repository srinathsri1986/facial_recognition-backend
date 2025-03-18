from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

hashed_password = pwd_context.hash("Raghav123!")
print(hashed_password)  # Copy this and update the DB
