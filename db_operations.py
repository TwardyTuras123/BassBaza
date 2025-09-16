import oracledb
from db_config import USER, PASSWORD, DSN
from auth import hash_password, check_password

# --- AUTH & USER MANAGEMENT ---
def register_user(username, email, plain_password, role='USER'):
    hashed_pw = hash_password(plain_password)
    sql = "INSERT INTO Users (username, email, password_hash, role) VALUES (:u, :e, :p, :r)"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, u=username, e=email, p=hashed_pw, r=role)
                connection.commit()
                print(f">>> Użytkownik {username} został pomyślnie zarejestrowany!")
    except oracledb.DatabaseError as e:
        err_obj, = e.args
        print(f"Błąd rejestracji: {err_obj.message}")

def login_user(username, plain_password):
    sql = "SELECT user_id, username, role, password_hash FROM Users WHERE username = :u"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, u=username)
                result = cursor.fetchone()
                if not result: return None
                user_id, db_username, role, stored_hash = result
                if check_password(plain_password, stored_hash):
                    print(f">>> Witaj, {db_username}! Zalogowano pomyślnie.")
                    return {"user_id": user_id, "username": db_username, "role": role}
                else:
                    print(">>> Błąd: Nieprawidłowe hasło.")
                    return None
    except oracledb.Error as e:
        print(f"Błąd podczas logowania: {e}")
        return None

# --- CRUD & POST INTERACTION ---
def get_all_posts():
    sql = "SELECT post_id, title, author_username, comments_count, likes_count, created_at FROM V_PostDetails ORDER BY created_at DESC"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
    except oracledb.Error as e:
        print(f"Błąd podczas pobierania postów: {e}")
        return []

def get_post_details(post_id):
    sql = "SELECT * FROM V_PostDetails WHERE post_id = :pid"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, pid=post_id)
                desc = [d[0] for d in cursor.description]
                row_tuple = cursor.fetchone()
                if not row_tuple: return None
                post_dict = dict(zip(desc, row_tuple))
                if 'CONTENT' in post_dict and isinstance(post_dict['CONTENT'], oracledb.LOB):
                    post_dict['CONTENT'] = post_dict['CONTENT'].read()
                return post_dict
    except oracledb.Error as e:
        print(f"Błąd podczas pobierania szczegółów posta: {e}")
        return None

def get_comments_for_post(post_id):
    sql = "SELECT c.comment_id, c.content, u.username, c.created_at FROM Forum_Comments c JOIN Users u ON c.user_id = u.user_id WHERE c.post_id = :pid ORDER BY c.created_at ASC"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, pid=post_id)
                return cursor.fetchall()
    except oracledb.Error as e:
        print(f"Błąd podczas pobierania komentarzy: {e}")
        return []

def add_post(user_id, title, content):
    sql = "INSERT INTO Posts (user_id, title, content) VALUES (:1, :2, :3)"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [user_id, title, content])
                connection.commit()
                print(">>> Post został dodany pomyślnie!")
    except oracledb.Error as e:
        print(f"Błąd podczas dodawania posta: {e}")

def add_comment(post_id, user_id, content):
    sql = 'INSERT INTO Forum_Comments (post_id, user_id, content) VALUES (:1, :2, :3)'
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [post_id, user_id, content])
                connection.commit()
                print(">>> Komentarz został dodany.")
                return True
    except oracledb.Error as e:
        print(f"Błąd podczas dodawania komentarza: {e}")
        return False

def toggle_like(post_id, user_id):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                action_taken = cursor.var(str, 10)
                cursor.callproc("Toggle_Post_Like", [post_id, user_id, action_taken])
                result = action_taken.getvalue()
                if result == 'LIKED':
                    print(">>> Post został polubiony!")
                elif result == 'UNLIKED':
                    print(">>> Polubienie zostało cofnięte.")
                else:
                    print(">>> Wystąpił błąd podczas operacji polubienia.")
    except oracledb.Error as e:
        print(f"Błąd krytyczny podczas przełączania polubienia: {e}")

def delete_post(post_id, user_id, user_role):
    sql = "DELETE FROM Posts WHERE post_id = :1 AND (user_id = :2 OR :3 = 'ADMIN')"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [post_id, user_id, user_role])
                connection.commit()
                if cursor.rowcount > 0:
                    print(">>> Post został usunięty.")
                    return True
                else:
                    print(">>> Nie masz uprawnień do usunięcia tego posta lub post nie istnieje.")
                    return False
    except oracledb.Error as e:
        print(f"Błąd podczas usuwania posta: {e}")
        return False

def delete_comment(comment_id, user_id, user_role):
    sql = "DELETE FROM Forum_Comments WHERE comment_id = :1 AND (user_id = :2 OR :3 = 'ADMIN')"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [comment_id, user_id, user_role])
                connection.commit()
                if cursor.rowcount > 0:
                    print(">>> Komentarz został usunięty.")
                    return True
                else:
                    print(">>> Nie masz uprawnień do usunięcia tego komentarza lub komentarz nie istnieje.")
                    return False
    except oracledb.Error as e:
        print(f"Błąd podczas usuwania komentarza: {e}")
        return False

def edit_post(post_id, user_id, new_title, new_content):
    sql = "UPDATE Posts SET title = :1, content = :2 WHERE post_id = :3 AND user_id = :4"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [new_title, new_content, post_id, user_id])
                connection.commit()
                if cursor.rowcount > 0:
                    print(">>> Post został pomyślnie zaktualizowany.")
                    return True
                else:
                    print(">>> Nie masz uprawnień do edycji tego posta lub post nie istnieje.")
                    return False
    except oracledb.Error as e:
        print(f"Błąd podczas edycji posta: {e}")
        return False

# --- NOWE FUNKCJE DZIENNIKA POŁOWÓW ---

def get_user_catches(user_id):
    """Pobiera wszystkie połowy danego użytkownika z widoku."""
    sql = "SELECT catch_id, fish_name, weight_kg, length_cm, spot_name, date_caught FROM V_CatchDetails WHERE user_id = :1 ORDER BY date_caught DESC"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [user_id])
                return cursor.fetchall()
    except oracledb.Error as e:
        print(f"Błąd podczas pobierania połowów: {e}")
        return []

def add_catch(user_id, spot_id, fish_type_id, weight, length):
    """Dodaje nowy połów do bazy."""
    sql = "INSERT INTO Catches (user_id, spot_id, fish_type_id, weight_kg, length_cm) VALUES (:1, :2, :3, :4, :5)"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [user_id, spot_id, fish_type_id, weight, length])
                connection.commit()
                print(">>> Nowy połów został dodany do dziennika!")
                return True
    except oracledb.Error as e:
        print(f"Błąd podczas dodawania połowu: {e}")
        return False

def edit_catch(catch_id, user_id, new_weight, new_length):
    """Edytuje istniejący połów, tylko jeśli użytkownik jest jego właścicielem."""
    sql = "UPDATE Catches SET weight_kg = :1, length_cm = :2 WHERE catch_id = :3 AND user_id = :4"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [new_weight, new_length, catch_id, user_id])
                connection.commit()
                if cursor.rowcount > 0:
                    print(">>> Połów został zaktualizowany.")
                    return True
                else:
                    print(">>> Nie masz uprawnień do edycji tego połowu lub połów nie istnieje.")
                    return False
    except oracledb.Error as e:
        print(f"Błąd podczas edycji połowu: {e}")
        return False

def delete_catch(catch_id, user_id):
    """Usuwa połów, tylko jeśli użytkownik jest jego właścicielem."""
    sql = "DELETE FROM Catches WHERE catch_id = :1 AND user_id = :2"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql, [catch_id, user_id])
                connection.commit()
                if cursor.rowcount > 0:
                    print(">>> Połów został usunięty z dziennika.")
                    return True
                else:
                    print(">>> Nie masz uprawnień do usunięcia tego połowu lub połów nie istnieje.")
                    return False
    except oracledb.Error as e:
        print(f"Błąd podczas usuwania połowu: {e}")
        return False

# --- FUNKCJE POMOCNICZE DO WYBORU ---
def get_all_fishing_spots_list():
    sql = "SELECT spot_id, name FROM FishingSpots ORDER BY name"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
    except oracledb.Error as e:
        print(f"Błąd podczas pobierania listy łowisk: {e}")
        return []

def get_all_fish_types_list():
    sql = "SELECT fish_type_id, name FROM FishTypes ORDER BY name"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
    except oracledb.Error as e:
        print(f"Błąd podczas pobierania listy gatunków: {e}")
        return []


# --- TRANSACTIONAL OPERATION --- 
def update_water_conditions_transaction(spot_id, user_id, temp, level, clarity, flow):
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                result_code = cursor.var(int)
                result_message = cursor.var(str, 200)
                cursor.callproc("UpdateWaterConditions", [spot_id, user_id, temp, level, clarity, flow, result_code, result_message])
                print(f">>> Odpowiedź z bazy danych: {result_message.getvalue()}")
    except oracledb.Error as e:
        print(f"Błąd podczas wywoływania transakcji: {e}")

# --- REPORTING OPERATION --- 
def get_user_activity_report():
    sql = "SELECT username, role, total_posts, total_comments, total_activity FROM V_UserActivityReport ORDER BY total_activity DESC"
    try:
        with oracledb.connect(user=USER, password=PASSWORD, dsn=DSN) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql)
                return cursor.fetchall()
    except oracledb.Error as e:
        print(f"Błąd podczas generowania raportu: {e}")
        return []