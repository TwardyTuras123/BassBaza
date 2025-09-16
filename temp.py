# Plik tymczasowy: update_mock_passwords.py
from auth import hash_password

# Hasła, które chcemy nadać naszym mockowym użytkownikom
mock_users = {
    'wedkarz_1': 'adam123',
    'rybak_stefan': 'ewa456',
    'anna_fish': 'janusz789',
    'wielki_fiszer': 'maupiszon123'
}

print("-- Skopiuj i wykonaj poniższe polecenia SQL w VS Code, aby zaktualizować hasła:")
for username, password in mock_users.items():
    hashed = hash_password(password)
    # Generujemy gotowe polecenie UPDATE
    print(f"UPDATE Users SET password_hash = '{hashed}' WHERE username = '{username}';")

print("COMMIT;")