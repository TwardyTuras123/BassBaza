ALTER TABLE FishingSpots ADD (
    is_locked CHAR(1) DEFAULT 'N' NOT NULL,
    locked_by_user_id NUMBER,
    CONSTRAINT chk_is_locked CHECK (is_locked IN ('Y', 'N')),
    CONSTRAINT fk_locked_by_user FOREIGN KEY (locked_by_user_id) REFERENCES Users(user_id)
);



CREATE OR REPLACE PROCEDURE UpdateWaterConditions (
    p_spot_id           IN NUMBER,
    p_user_id           IN NUMBER,
    p_temperature_c     IN NUMBER,
    p_water_level_cm    IN NUMBER,
    p_clarity_m         IN NUMBER,
    p_flow_rate_cms     IN NUMBER,
    p_result_code       OUT NUMBER, -- 0=sukces, 1=zablokowane, 2=nie znaleziono, 3=inny błąd
    p_result_message    OUT VARCHAR2
)
IS
    v_spot_exists NUMBER;
BEGIN
    -- Sprawdź, czy łowisko istnieje
    SELECT COUNT(*) INTO v_spot_exists FROM FishingSpots WHERE spot_id = p_spot_id;
    IF v_spot_exists = 0 THEN
        p_result_code := 2;
        p_result_message := 'BŁĄD: Łowisko o podanym ID nie istnieje.';
        RETURN;
    END IF;

    -- Spróbuj zablokować rekord łowiska.
    UPDATE FishingSpots
    SET is_locked = 'Y', locked_by_user_id = p_user_id
    WHERE spot_id = p_spot_id AND is_locked = 'N';

    -- Jeśli żaden wiersz nie został zaktualizowany, oznacza to, że był już zablokowany
    IF SQL%ROWCOUNT = 0 THEN
        p_result_code := 1;
        p_result_message := 'ZASÓB ZABLOKOWANY: To łowisko jest aktualnie edytowane przez innego użytkownika. Spróbuj później.';
        ROLLBACK;
        RETURN;
    END IF;

    -- Jeśli blokada się powiodła, wstaw nowe dane o stanie wody.
    INSERT INTO WaterConditions (spot_id, temperature_c, water_level_cm, clarity_m, flow_rate_cms)
    VALUES (p_spot_id, p_temperature_c, p_water_level_cm, p_clarity_m, p_flow_rate_cms);

    -- Zwolnij blokadę.
    UPDATE FishingSpots
    SET is_locked = 'N', locked_by_user_id = NULL
    WHERE spot_id = p_spot_id;

    COMMIT; -- Zatwierdź całą transakcję.
    p_result_code := 0;
    p_result_message := 'SUKCES: Stan wody zaktualizowano pomyślnie.';

EXCEPTION
    WHEN OTHERS THEN
        -- W przypadku nieoczekiwanego błędu, wycofaj wszystkie zmiany.
        ROLLBACK;
        p_result_code := 3;
        p_result_message := 'BŁĄD KRYTYCZNY: ' || SQLERRM;
END;
/


-- NOWA PROCEDURA: Przełączanie polubienia (Like/Unlike)
CREATE OR REPLACE PROCEDURE Toggle_Post_Like (
    p_post_id           IN NUMBER,
    p_user_id           IN NUMBER,
    p_action_taken      OUT VARCHAR2 -- Zwraca 'LIKED' lub 'UNLIKED'
)
IS
BEGIN
    DELETE FROM Post_Likes
    WHERE post_id = p_post_id AND user_id = p_user_id;
    IF SQL%ROWCOUNT = 0 THEN
        INSERT INTO Post_Likes (post_id, user_id) VALUES (p_post_id, p_user_id);
        p_action_taken := 'LIKED';
    ELSE
        p_action_taken := 'UNLIKED';
    END IF;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN
        ROLLBACK;
        p_action_taken := 'ERROR';
END;
/