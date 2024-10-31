QUERIES = {
    "games_for_elo": """  # noqa
        WITH team_game AS (
            SELECT
                tg.team_id,
                tg.game_id,
                m.lan,
                m.id as match_id,
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
                LOWER(maps.name) AS played_map,
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
            t.match_id,
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
        ORDER BY t.start_date, t.game_id;
    """,
    "matches_to_predict": """  # noqa
        WITH match_players AS (
        SELECT DISTINCT
            fm.id,
            fm.hltv_link,
            fm.max_maps,
            fl.team_id,
            fm.start_date,
            eht.`rank` as hltv_rank
        FROM future_matches fm
        LEFT JOIN future_lineups fl on fl.future_match_id = fm.id
        LEFT JOIN events_have_teams eht on eht.team_id = fl.team_id and eht.event_id = fm.event_id 
        ),
        matches_to_predict as (
        SELECT
            fm.id,
            fm.hltv_link,
            fm.max_maps,
            fm.team_id,
            fm.start_date,
            t.name as team_name,
            fm.hltv_rank,
            GROUP_CONCAT(
                DISTINCT fl.player_id
                ORDER BY fl.player_id SEPARATOR '-'
            ) roster_hash
        FROM match_players fm
        LEFT JOIN future_lineups fl on fl.future_match_id = fm.id and fl.team_id = fm.team_id
        LEFT JOIN teams t on t.id = fm.team_id
        GROUP BY fm.id, fm.team_id
        )
        SELECT
            t1.id AS match_id,
            t1.max_maps,
            t1.team_id,
            100000*t1.id + (CASE WHEN t1.team_id < t2.team_id THEN t1.team_id ELSE t2.team_id END)*1000 + (CASE WHEN t1.team_id > t2.team_id THEN t1.team_id ELSE t2.team_id END) AS game_id,
            t1.start_date AS match_date,
            t1.team_name,
            t1.roster_hash,
            t1.hltv_rank,
            -- opponent
            t2.team_id AS team_id_op,
            t2.team_name AS team_name_op,
            t2.roster_hash AS roster_hash_op,
            t2.hltv_rank AS hltv_rank_op,
            LOWER(m.name) AS played_map
        FROM matches_to_predict t1
        LEFT JOIN matches_to_predict t2 on t1.id = t2.id and t1.team_id <> t2.team_id
        LEFT JOIN maps m on TRUE
    """,
    "team_games": """  # noqa
        WITH team_game AS (
            SELECT 
                m.id as match_id,
                tg.team_id,
                tg.game_id,
                g.hltv_id AS game_hltv_id,
                m.lan,
                m.start_date match_date,
                t.name AS team_name,
                GROUP_CONCAT(
                    DISTINCT pg.player_id
                    ORDER BY pg.player_id SEPARATOR '-'
                ) roster_hash,
                tg.starting_side,
                tg.score_ct,
                tg.won_pistol_ct,
                tg.score_tr,
                tg.won_pistol_tr,
                tg.clutches,
                tg.first_kills,
                LOWER(maps.name) AS played_map,
                eht.rank hltv_rank,
                score + score_opponent AS total_rounds,
                score,
                SUM(pg.kills) AS kills,
                SUM(pg.deaths) AS deaths,
                SUM(pg.assists) AS assists,
                SUM(pg.flash_assists) AS flash_assists,
                SUM(pg.fk_diff) AS fk_diff,
                SUM(pg.kills_ct) AS kills_ct,
                SUM(pg.deaths_ct) AS deaths_ct,
                SUM(pg.assists_ct) AS assists_ct,
                SUM(pg.flash_assists_ct) AS flash_assists_ct,
                SUM(pg.fk_diff_ct) AS fk_diff_ct,
                SUM(pg.kills_tr) AS kills_tr,
                SUM(pg.deaths_tr) AS deaths_tr,
                SUM(pg.assists_tr) AS assists_tr,
                SUM(pg.flash_assists_tr) AS flash_assists_tr,
                SUM(pg.fk_diff_tr) AS fk_diff_tr,
                MAX(pg.rating) AS max_rating,
                AVG(pg.rating) AS avg_rating,
                MIN(pg.rating) AS min_rating,
                MAX(pg.kast) AS max_kast,
                AVG(pg.kast) AS avg_kast,
                MIN(pg.kast) AS min_kast,
                STD(pg.rating) AS rating_stddev, 
                MAX(pg.rating_ct) AS max_rating_ct,
                AVG(pg.rating_ct) AS avg_rating_ct,
                MIN(pg.rating_ct) AS min_rating_ct,
                MAX(pg.rating_tr) AS max_rating_tr,
                AVG(pg.rating_tr) AS avg_rating_tr,
                MIN(pg.rating_tr) AS min_rating_tr
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
            t.match_id,
            t.match_date,
            t.team_id,
            t.game_id,
            t.game_hltv_id,
            t.roster_hash,
            t.lan,
            t.team_name,
            t.starting_side,
            t.score_ct,
            t.won_pistol_ct,
            t.score_tr,
            t.won_pistol_tr,
            t.clutches,
            t.first_kills,
            t.played_map,
            t.hltv_rank,
            t.total_rounds,
            t.score,
            t.kills,
            t.deaths,
            t.assists,
            t.flash_assists,
            t.fk_diff,
            t.kills_ct,
            t.deaths_ct,
            t.assists_ct,
            t.flash_assists_ct,
            t.fk_diff_ct,
            t.kills_tr,
            t.deaths_tr,
            t.assists_tr,
            t.flash_assists_tr,
            t.fk_diff_tr,
            t.max_rating,
            t.avg_rating,
            t.min_rating,
            t.max_kast,
            t.avg_kast,
            t.min_kast,
            t.max_rating_ct,
            t.avg_rating_ct,
            t.min_rating_ct,
            t.max_rating_tr,
            t.avg_rating_tr,
            t.min_rating_tr,
            -- Opponent columns with _op suffix
            op.roster_hash as roster_hash_op,
            op.team_id AS team_id_op,
            op.team_name AS team_name_op,
            op.starting_side AS starting_side_op,
            op.score_ct AS score_ct_op,
            op.won_pistol_ct AS won_pistol_ct_op,
            op.score_tr AS score_tr_op,
            op.won_pistol_tr AS won_pistol_tr_op,
            op.clutches AS clutches_op,
            op.first_kills AS first_kills_op,
            op.hltv_rank AS hltv_rank_op,
            op.score AS score_op,
            op.kills AS kills_op,
            op.deaths AS deaths_op,
            op.assists AS assists_op,
            op.flash_assists AS flash_assists_op,
            op.fk_diff AS fk_diff_op,
            op.kills_ct AS kills_ct_op,
            op.deaths_ct AS deaths_ct_op,
            op.assists_ct AS assists_ct_op,
            op.flash_assists_ct AS flash_assists_ct_op,
            op.fk_diff_ct AS fk_diff_ct_op,
            op.kills_tr AS kills_tr_op,
            op.deaths_tr AS deaths_tr_op,
            op.assists_tr AS assists_tr_op,
            op.flash_assists_tr AS flash_assists_tr_op,
            op.fk_diff_tr AS fk_diff_tr_op,
            op.max_rating AS max_rating_op,
            op.avg_rating AS avg_rating_op,
            op.min_rating AS min_rating_op,
            op.max_rating_ct AS max_rating_ct_op,
            op.avg_rating_ct AS avg_rating_ct_op,
            op.min_rating_ct AS min_rating_ct_op,
            op.max_rating_tr AS max_rating_tr_op,
            op.avg_rating_tr AS avg_rating_tr_op,
            op.min_rating_tr AS min_rating_tr_op,
            -- feature calculations
            -- pistol
            t.won_pistol_ct + t.won_pistol_tr AS pistols_won,
            -- rank split
            CASE WHEN op.hltv_rank <= 5 THEN 5
                WHEN op.hltv_rank <= 10 THEN 10
                WHEN op.hltv_rank <= 20 THEN 20
                WHEN op.hltv_rank <= 50 THEN 50
                WHEN op.hltv_rank <= 100 THEN 100
                WHEN op.hltv_rank <= 500 THEN 500
                ELSE NULL END AS rank_range_op,
            CASE WHEN t.hltv_rank <= 5 THEN 5
                WHEN t.hltv_rank <= 10 THEN 10
                WHEN t.hltv_rank <= 20 THEN 20
                WHEN t.hltv_rank <= 50 THEN 50
                WHEN t.hltv_rank <= 100 THEN 100
                WHEN t.hltv_rank <= 500 THEN 500
                ELSE NULL END AS rank_range,
            t.hltv_rank - op.hltv_rank AS rank_diff,
            -- performance
            t.min_rating < 0.5 AS player_carried_down,
            t.max_rating > 1.6 AS player_carried,
            -- scouts
            CASE WHEN t.score > op.score THEN op.score_ct + op.score_tr ELSE NULL END rounds_lost_on_win,
            CASE WHEN t.score < op.score THEN t.score_ct + t.score_tr ELSE NULL END rounds_won_on_loss,
            t.kills/t.total_rounds AS kills_per_round,
            t.deaths/t.total_rounds AS deaths_per_round,
            t.first_kills/t.total_rounds AS first_kills_per_round,
            t.flash_assists/t.total_rounds AS flash_assists_per_round,
            t.clutches/t.total_rounds AS clutches_per_round,
            1 as game_played,
            -- target
            t.score > op.score AS won
        FROM team_game t
        LEFT JOIN team_game op ON t.game_id = op.game_id AND t.team_id <> op.team_id
        ORDER BY t.match_date;
    """,
}
