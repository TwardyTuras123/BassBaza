import db_operations as db
import getpass

current_user = None

def show_main_menu():
    print("\n--- MENU GŁÓWNE FORUM WĘDKARSKIEGO ---")
    if current_user:
        print(f"Zalogowano jako: {current_user['username']} (Rola: {current_user['role']})")
        print("1. Wyświetl wszystkie posty")
        print("2. Wejdź do posta (podaj ID)")
        print("3. Dodaj nowy post")
        print("4. Mój Dziennik Połowów")
        print("5. Zaktualizuj stan wody (transakcja)")
        print("6. Wyświetl raport aktywności użytkowników")
        print("9. Wyloguj")
    else:
        print("1. Zaloguj się")
        print("2. Zarejestruj się")
        print("3. Wyświetl wszystkie posty")
    print("0. Zakończ")

def handle_login():
    global current_user
    username = input("Nazwa użytkownika: ")
    password = getpass.getpass("Hasło: ")
    user_data = db.login_user(username, password)
    if user_data:
        current_user = user_data

def handle_register():
    username = input("Wybierz nazwę użytkownika: ")
    email = input("Podaj adres email: ")
    password = getpass.getpass("Wybierz hasło: ")
    db.register_user(username, email, password)

def handle_show_posts():
    print("\n--- Lista wszystkich postów ---")
    posts = db.get_all_posts()
    if posts:
        print(f"{'ID':<4} | {'Tytuł':<40} | {'Autor':<15} | {'Koment.':<7} | {'Like':<5} | {'Data':<10}")
        print("-" * 90)
        for post in posts:
            post_id, title, author, comments, likes, created_at = post
            print(f"{post_id:<4} | {title:<40} | {author:<15} | {comments:<7} | {likes:<5} | {created_at.strftime('%Y-%m-%d')}")
    else:
        print("Brak postów do wyświetlenia.")

def handle_view_post():
    try:
        post_id = int(input("Podaj ID posta, który chcesz zobaczyć: "))
    except ValueError:
        print(">>> Nieprawidłowe ID.")
        return

    while True:
        post_details = db.get_post_details(post_id)
        if not post_details:
            print(">>> Post o podanym ID nie istnieje lub został usunięty.")
            return

        print("\n" + "="*80)
        print(f"POST: {post_details['TITLE']}")
        print(f"Autor: {post_details['AUTHOR_USERNAME']} | Data: {post_details['CREATED_AT'].strftime('%Y-%m-%d %H:%M')}")
        if post_details['UPDATED_AT']:
             print(f"Ostatnia edycja: {post_details['UPDATED_AT'].strftime('%Y-%m-%d %H:%M')}")
        if post_details['SPOT_NAME']:
            print(f"Dotyczy łowiska: {post_details['SPOT_NAME']}")
        print(f"Polubienia: {post_details['LIKES_COUNT']} | Komentarze: {post_details['COMMENTS_COUNT']}")
        print("-"*80)
        print(post_details['CONTENT'])
        print("="*80)

        print("\n--- Komentarze ---")
        comments = db.get_comments_for_post(post_id)
        if comments:
            for comment in comments:
                comment_id, content, author, created_at = comment
                print(f"  ID:{comment_id:<4} > [{created_at.strftime('%Y-%m-%d %H:%M')}] {author}: {content}")
        else:
            print("  Brak komentarzy.")

        is_author = current_user and current_user['user_id'] == post_details['AUTHOR_ID']
        is_admin = current_user and current_user['role'] == 'ADMIN'

        print("\n--- Co chcesz zrobić? ---")
        if current_user:
            print("1. Dodaj komentarz")
            print("2. Polub / Cofnij polubienie")
            if is_author:
                print("7. Edytuj ten post")
            if is_author or is_admin:
                print("8. Usuń komentarz")
                print("9. USUŃ TEN POST")
        print("0. Wróć do menu głównego")
        
        choice = input("Wybór: ")

        if choice == '1' and current_user:
            content = input("Wpisz treść komentarza: ")
            db.add_comment(post_id, current_user['user_id'], content)
        elif choice == '2' and current_user:
            db.toggle_like(post_id, current_user['user_id'])
        elif choice == '7' and is_author:
            print("\n--- Edycja posta ---")
            print("Wciśnij Enter, aby pozostawić starą wartość.")
            old_title = post_details['TITLE']
            new_title = input(f"Nowy tytuł [{old_title}]: ") or old_title
            
            old_content = post_details['CONTENT']
            print(f"Stara treść: {old_content}")
            new_content = input("Nowa treść: ") or old_content
            
            db.edit_post(post_id, current_user['user_id'], new_title, new_content)
        elif choice == '8' and (is_author or is_admin):
            try:
                comment_id_to_delete = int(input("Podaj ID komentarza do usunięcia: "))
                db.delete_comment(comment_id_to_delete, current_user['user_id'], current_user['role'])
            except ValueError:
                print(">>> Nieprawidłowe ID komentarza.")
        elif choice == '9' and (is_author or is_admin):
            confirm = input(f"Czy na pewno chcesz usunąć post ID:{post_id}? Tej operacji nie można cofnąć! (T/N): ").upper()
            if confirm == 'T':
                if db.delete_post(post_id, current_user['user_id'], current_user['role']):
                    break
            else:
                print(">>> Anulowano usuwanie.")
        elif choice == '0':
            break
        else:
            print(">>> Nieprawidłowa opcja.")

def handle_add_post():
    if not current_user:
        print(">>> Musisz być zalogowany, aby dodać post.")
        return
    title = input("Tytuł posta: ")
    content = input("Treść posta: ")
    db.add_post(user_id=current_user['user_id'], title=title, content=content)

def handle_fishing_log():
    """Obsługuje interakcje z dziennikiem połowów użytkownika."""
    if not current_user:
        print(">>> Ta funkcja wymaga zalogowania.")
        return

    while True:
        print(f"\n--- Dziennik Połowów: {current_user['username']} ---")
        catches = db.get_user_catches(current_user['user_id'])
        if catches:
            print(f"{'ID':<4} | {'Gatunek':<15} | {'Waga (kg)':<10} | {'Dł. (cm)':<10} | {'Miejsce':<25} | {'Data':<10}")
            print("-" * 80)
            for catch in catches:
                catch_id, fish, weight, length, spot, date = catch
                print(f"{catch_id:<4} | {fish:<15} | {weight:<10.2f} | {length:<10.2f} | {spot:<25} | {date.strftime('%Y-%m-%d')}")
        else:
            print("Twój dziennik jest pusty.")
        
        print("\n--- Co chcesz zrobić? ---")
        print("1. Dodaj nowy połów")
        print("2. Edytuj połów")
        print("3. Usuń połów")
        print("0. Wróć do menu głównego")
        
        choice = input("Wybór: ")

        if choice == '1':
            print("\n--- Dodawanie nowego połowu ---")
            spots = db.get_all_fishing_spots_list()
            fish_types = db.get_all_fish_types_list()
            print("Dostępne łowiska:")
            for spot_id, name in spots: print(f"  ID: {spot_id} - {name}")
            print("Dostępne gatunki ryb:")
            for fish_id, name in fish_types: print(f"  ID: {fish_id} - {name}")
            try:
                spot_id = int(input("Podaj ID łowiska: "))
                fish_id = int(input("Podaj ID gatunku ryby: "))
                weight = float(input("Podaj wagę w kg (np. 3.5): "))
                length = float(input("Podaj długość w cm (np. 75.5): "))
                db.add_catch(current_user['user_id'], spot_id, fish_id, weight, length)
            except ValueError:
                print(">>> Błędne dane. Upewnij się, że podajesz liczby.")
        
        elif choice == '2':
            try:
                catch_id = int(input("Podaj ID połowu do edycji: "))
                new_weight = float(input("Podaj nową wagę w kg: "))
                new_length = float(input("Podaj nową długość w cm: "))
                db.edit_catch(catch_id, current_user['user_id'], new_weight, new_length)
            except ValueError:
                print(">>> Błędne dane. Upewnij się, że podajesz liczby.")
        
        elif choice == '3':
            try:
                catch_id = int(input("Podaj ID połowu do usunięcia: "))
                confirm = input(f"Czy na pewno chcesz usunąć połów ID:{catch_id}? (T/N): ").upper()
                if confirm == 'T':
                    db.delete_catch(catch_id, current_user['user_id'])
            except ValueError:
                print(">>> Błędne ID połowu.")
        
        elif choice == '0':
            break
        
        else:
            print(">>> Nieprawidłowa opcja.")

def handle_update_water():
    if not current_user:
        print(">>> Musisz być zalogowany, aby wykonać tę operację.")
        return
    print("\n--- Aktualizacja stanu wody (transakcja) ---")
    try:
        spot_id = int(input("Podaj ID łowiska (np. 1 dla Jeziora Łebsko): "))
        temp = float(input("Nowa temperatura wody (np. 15.5): "))
        level = float(input("Nowy poziom wody w cm (np. 250.0): "))
        clarity = float(input("Nowa przejrzystość w m (np. 1.5): "))
        flow = float(input("Nowy przepływ w m3/s (np. 0.0 dla jeziora): "))
        db.update_water_conditions_transaction(spot_id, current_user['user_id'], temp, level, clarity, flow)
    except ValueError:
        print(">>> Błędne dane. Wprowadź prawidłowe liczby.")

def handle_show_report():
    print("\n--- Raport Aktywności Użytkowników ---")
    report_data = db.get_user_activity_report()
    if report_data:
        print(f"{'Użytkownik':<20} {'Rola':<12} {'Posty':<7} {'Koment.':<9} {'Suma':<5}")
        print("-" * 70)
        for row in report_data:
            print(f"{row[0]:<20} {row[1]:<12} {row[2]:<7} {row[3]:<9} {row[4]:<5}")
    else:
        print("Nie udało się wygenerować raportu.")

def main():
    global current_user
    while True:
        show_main_menu()
        choice = input("Wybierz opcję: ")

        if current_user:
            if choice == '1': handle_show_posts()
            elif choice == '2': handle_view_post()
            elif choice == '3': handle_add_post()
            elif choice == '4': handle_fishing_log()
            elif choice == '5': handle_update_water()
            elif choice == '6': handle_show_report()
            elif choice == '9':
                print(f">>> Wylogowano użytkownika {current_user['username']}.")
                current_user = None
            elif choice == '0': break
            else: print("Nieprawidłowa opcja.")
        else:
            if choice == '1': handle_login()
            elif choice == '2': handle_register()
            elif choice == '3': handle_show_posts()
            elif choice == '0': break
            else: print("Nieprawidłowa opcja.")

    print("Do zobaczenia!")

if __name__ == "__main__":
    main()