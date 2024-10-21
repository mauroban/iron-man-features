WITH team_game AS (
    SELECT 
        tg.team_id,
        tg.game_id,
        m.lan,
        m.start_date,
        t.name AS team_name,
        GROUP_CONCAT(
            DISTINCT pg.player_id
            ORDER BY pg.player_id SEPARATOR '-'
        ) roster_hash,
        tg.starting_side,
        tg.score_ct,
        tg.score_tr,
        g.map_id,
        eht.rank as hltv_rank,
        maps.name AS played_map,
        score + score_opponent AS total_rounds,
        score
    FROM team_games tg 
    LEFT JOIN teams t ON t.id = tg.team_id 
    LEFT JOIN games g ON g.id = tg.game_id
    LEFT JOIN maps ON maps.id = g.map_id 
    LEFT JOIN matches m ON m.id = g.match_id
    LEFT JOIN events e ON e.id = m.event_id 
    LEFT JOIN events_have_teams eht ON eht.event_id = e.id AND eht.team_id = tg.team_id
    LEFT JOIN player_games pg ON pg.team_game_id = tg.id
    GROUP BY tg.id
)
SELECT 
    t.team_id,
    t.game_id,
    t.lan,
    t.start_date,
    t.roster_hash,
    t.team_name,
    t.starting_side,
    t.score_ct,
    t.score_tr,
    t.map_id,
    t.played_map,
    t.total_rounds,
    t.score,
    t.hltv_rank,
    -- Opponent columns with _op suffix
    op.team_id AS team_id_op,
    op.roster_hash AS roster_hash_op,
    op.team_name AS team_name_op,
    op.starting_side AS starting_side_op,
    op.score_ct AS score_ct_op,
    op.score_tr AS score_tr_op,
    op.score AS score_op,
    op.hltv_rank AS hltv_rank_op
FROM team_game t
LEFT JOIN team_game op ON t.game_id = op.game_id AND t.team_id <> op.team_id
WHERE t.team_id < op.team_id
ORDER BY t.start_date;
