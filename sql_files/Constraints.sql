BEGIN
   EXECUTE IMMEDIATE 'ALTER TABLE Post_Likes DROP CONSTRAINT uq_user_post_like';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -2443 THEN
         RAISE;
      END IF;
END;
/

ALTER TABLE Post_Likes ADD CONSTRAINT uq_user_post_like UNIQUE (user_id, post_id);

-- FIX CASCADING UPON POST DELETION --




DECLARE
  v_constraint_name VARCHAR2(100);
BEGIN
  SELECT constraint_name INTO v_constraint_name
  FROM user_constraints
  WHERE table_name = 'FORUM_COMMENTS' AND constraint_type = 'R' AND r_constraint_name IN (
    SELECT constraint_name FROM user_constraints WHERE table_name = 'POSTS' AND constraint_type IN ('P', 'U')
  );
  
  EXECUTE IMMEDIATE 'ALTER TABLE Forum_Comments DROP CONSTRAINT ' || v_constraint_name;
  DBMS_OUTPUT.PUT_LINE('Usunięto stare ograniczenie z Forum_Comments.');
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('Nie znaleziono starego ograniczenia w Forum_Comments do usunięcia.');
END;


/
ALTER TABLE Forum_Comments ADD CONSTRAINT fk_comment_post FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE CASCADE;




DECLARE
  v_constraint_name VARCHAR2(100);
BEGIN
  SELECT constraint_name INTO v_constraint_name
  FROM user_constraints
  WHERE table_name = 'POST_LIKES' AND constraint_type = 'R' AND r_constraint_name IN (
    SELECT constraint_name FROM user_constraints WHERE table_name = 'POSTS' AND constraint_type IN ('P', 'U')
  );
  
  EXECUTE IMMEDIATE 'ALTER TABLE Post_Likes DROP CONSTRAINT ' || v_constraint_name;
  DBMS_OUTPUT.PUT_LINE('Usunięto stare ograniczenie z Post_Likes.');
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    DBMS_OUTPUT.PUT_LINE('Nie znaleziono starego ograniczenia w Post_Likes do usunięcia.');
END;
/

ALTER TABLE Post_Likes ADD CONSTRAINT fk_like_post FOREIGN KEY (post_id) REFERENCES Posts(post_id) ON DELETE CASCADE;
