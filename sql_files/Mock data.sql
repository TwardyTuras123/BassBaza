-- Mock Users
INSERT INTO Users (username, email, password_hash, registration_date) VALUES ('wedkarz_1', 'wedkarz1@example.com', 'hash1', TO_DATE('2023-01-15', 'YYYY-MM-DD'));
INSERT INTO Users (username, email, password_hash, registration_date) VALUES ('rybak_stefan', 'stefan@example.com', 'hash2', TO_DATE('2023-02-01', 'YYYY-MM-DD'));
INSERT INTO Users (username, email, password_hash, registration_date) VALUES ('anna_fish', 'anna@example.com', 'hash3', TO_DATE('2023-03-10', 'YYYY-MM-DD'));
INSERT INTO Users (username, email, password_hash, registration_date, role) VALUES ('wielki_fiszer', 'wielkif@example.com', 'hash4', TO_DATE('2023-01-01', 'YYYY-MM-DD'), 'ADMIN');
COMMIT;

-- Mock FishTypes
INSERT INTO FishTypes (name, description) VALUES ('Karp', 'Popularna ryba słodkowodna.');
INSERT INTO FishTypes (name, description) VALUES ('Szczupak', 'Drapieżna ryba słodkowodna.');
INSERT INTO FishTypes (name, description) VALUES ('Sum', 'Duża ryba drapieżna.');
COMMIT;

-- Mock FishingSpots
INSERT INTO FishingSpots (name, latitude, longitude, description, created_by_user_id) VALUES ('Jezioro Łebsko', 54.68, 17.52, 'Duże jezioro przymorskie, dobre na sandacza.', (SELECT user_id FROM Users WHERE username = 'wedkarz_1'));
INSERT INTO FishingSpots (name, latitude, longitude, description, created_by_user_id) VALUES ('Wisła - okolice Krakowa', 50.05, 19.94, 'Odcinek rzeki Wisły, bogaty w sumy.', (SELECT user_id FROM Users WHERE username = 'rybak_stefan'));
COMMIT;

-- Mock Posts
INSERT INTO Posts (user_id, spot_id, title, content) VALUES (
    (SELECT user_id FROM Users WHERE username = 'wedkarz_1'),
    (SELECT spot_id FROM FishingSpots WHERE name = 'Jezioro Łebsko'),
    'Relacja z Łebska - Sandacze!',
    'Wczorajsza wyprawa na Łebsko zaowocowała pięknymi sandaczami. Pogoda dopisała, brania były regularne!'
);
INSERT INTO Posts (user_id, spot_id, title, content) VALUES (
    (SELECT user_id FROM Users WHERE username = 'rybak_stefan'),
    NULL,
    'Moje najlepsze przynęty na suma',
    'Chciałbym podzielić się moimi sprawdzonymi przynętami na sumy. Od lat używam...'
);
COMMIT;

-- Mock Comments
INSERT INTO Comments (post_id, user_id, content) VALUES (
    (SELECT post_id FROM Posts WHERE title LIKE '%Sandacze%'),
    (SELECT user_id FROM Users WHERE username = 'anna_fish'),
    'Super! Gratuluję połowu. Jakie gumy używałeś?'
);
INSERT INTO Comments (post_id, user_id, content) VALUES (
    (SELECT post_id FROM Posts WHERE title LIKE '%przynęty na suma%'),
    (SELECT user_id FROM Users WHERE username = 'wedkarz_1'),
    'Ciekawe spostrzeżenia, dzięki za podzielenie się wiedzą!'
);
COMMIT;

-- Mock Catches
INSERT INTO Catches (user_id, spot_id, fish_type_id, weight_kg, length_cm, date_caught, photo_url) VALUES (
    (SELECT user_id FROM Users WHERE username = 'wedkarz_1'),
    (SELECT spot_id FROM FishingSpots WHERE name = 'Jezioro Łebsko'),
    (SELECT fish_type_id FROM FishTypes WHERE name = 'Szczupak'),
    3.5, 75.0, TO_DATE('2023-04-05 10:30:00', 'YYYY-MM-DD HH24:MI:SS'), 'http://example.com/photo1.jpg'
);
INSERT INTO Catches (user_id, spot_id, fish_type_id, weight_kg, length_cm, date_caught, photo_url) VALUES (
    (SELECT user_id FROM Users WHERE username = 'rybak_stefan'),
    (SELECT spot_id FROM FishingSpots WHERE name = 'Wisła - okolice Krakowa'),
    (SELECT fish_type_id FROM FishTypes WHERE name = 'Sum'),
    15.2, 120.0, TO_DATE('2023-04-10 18:00:00', 'YYYY-MM-DD HH24:MI:SS'), 'http://example.com/photo2.jpg'
);
COMMIT;

-- Mock WaterConditions
INSERT INTO WaterConditions (spot_id, temperature_c, water_level_cm, clarity_m, flow_rate_cms) VALUES (
    (SELECT spot_id FROM FishingSpots WHERE name = 'Jezioro Łebsko'),
    12.5, 150.2, 2.5, 0.0 -- Jezioro, brak przepływu
);
INSERT INTO WaterConditions (spot_id, temperature_c, water_level_cm, clarity_m, flow_rate_cms) VALUES (
    (SELECT spot_id FROM FishingSpots WHERE name = 'Wisła - okolice Krakowa'),
    10.1, 320.0, 1.0, 50.5
);
COMMIT;

-- Zhashowane Hasła

UPDATE Users SET password_hash = '$2b$12$WMhyqtsOPjtV6ObML0MUl.Iuzpn3G8i81GbmPppO40mx7.6MDJRoS' WHERE username = 'wedkarz_1';
UPDATE Users SET password_hash = '$2b$12$AGjaVZUuHqNVwuPlISK6gu9VvmOhfOhN7tRPGe5klzeYhIcOgjHEi' WHERE username = 'rybak_stefan';
UPDATE Users SET password_hash = '$2b$12$R5RoWKTJBOS2NPtCDUQsBulRUPnk1d7pQFq3CTo7/gi7NOaTRlyua' WHERE username = 'anna_fish';
UPDATE Users SET password_hash = '$2b$12$fa8UyVNBq6Tf1Fs3rjCDVumRSJ33nIjUHpR513cpDnd4bMC3OPyZK' WHERE username = 'wielki_fiszer';
COMMIT;