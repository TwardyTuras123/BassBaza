CREATE OR REPLACE VIEW V_UserActivityReport AS
SELECT
    u.username,
    u.role,
    COUNT(DISTINCT p.post_id) AS total_posts,
    COUNT(DISTINCT c.comment_id) AS total_comments,
    (COUNT(DISTINCT p.post_id) + COUNT(DISTINCT c.comment_id)) AS total_activity
FROM Users u
LEFT JOIN Posts p ON u.user_id = p.user_id
LEFT JOIN Forum_Comments c ON u.user_id = c.user_id
GROUP BY u.username, u.role;


CREATE OR REPLACE VIEW V_PostDetails AS
SELECT
    p.post_id,
    p.title,
    p.content,
    p.created_at,
    p.updated_at,
    u.user_id AS author_id,
    u.username AS author_username,
    fs.spot_id,
    fs.name AS spot_name,
    (SELECT COUNT(*) FROM Forum_Comments c WHERE c.post_id = p.post_id) AS comments_count,
    (SELECT COUNT(*) FROM Post_Likes l WHERE l.post_id = p.post_id) AS likes_count
FROM Posts p
JOIN Users u ON p.user_id = u.user_id
LEFT JOIN FishingSpots fs ON p.spot_id = fs.spot_id;

CREATE OR REPLACE VIEW V_FishingSpotSummary AS
SELECT
    fs.spot_id,
    fs.name,
    fs.description,
    u.username as created_by,
    COUNT(DISTINCT p.post_id) AS posts_count,
    COUNT(DISTINCT c.catch_id) AS catches_count,
    (
        SELECT wc.temperature_c 
        FROM WaterConditions wc 
        WHERE wc.spot_id = fs.spot_id 
        ORDER BY wc.recorded_at DESC 
        FETCH FIRST 1 ROWS ONLY
    ) AS latest_water_temp_c
FROM FishingSpots fs
JOIN Users u ON fs.created_by_user_id = u.user_id
LEFT JOIN Posts p ON fs.spot_id = p.spot_id
LEFT JOIN Catches c ON fs.spot_id = c.spot_id
GROUP BY fs.spot_id, fs.name, fs.description, u.username;

CREATE OR REPLACE VIEW V_CatchDetails AS
SELECT
    c.catch_id,
    c.weight_kg,
    c.length_cm,
    c.date_caught,
    c.photo_url,
    u.user_id,
    u.username,
    fs.spot_id,
    fs.name AS spot_name,
    ft.fish_type_id,
    ft.name AS fish_name
FROM Catches c
JOIN Users u ON c.user_id = u.user_id
JOIN FishingSpots fs ON c.spot_id = fs.spot_id
JOIN FishTypes ft ON c.fish_type_id = ft.fish_type_id;