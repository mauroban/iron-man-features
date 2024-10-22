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
	t1.start_date,
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