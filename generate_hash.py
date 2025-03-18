import bcrypt

password = "YourSecurePassword"  # Replace with your actual password
hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

print("Hashed Password:", hashed_password)
