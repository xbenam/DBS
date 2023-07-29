# V2
## ***/v2/patches/***
```sql 
	SELECT 	p.name AS patch_version,
	    CAST(extract(epoch FROM p.release_date) AS INT) AS patch_start_date,
	    CAST(extract(epoch FROM LEAD(p.release_date) OVER (ORDER BY p.release_date) ) AS INT) AS patch_end_date,
	    json_agg(m.id) AS match_id,
	    json_agg(round((m.duration)/60.00, 2)) as match_duration
	FROM public.patches p
	LEFT JOIN public.matches m
	ON m.start_time BETWEEN CAST(extract(epoch FROM p.release_date) AS INT) and CAST(extract(epoch FROM p.release_date) AS INT) + 86400
	GROUP BY patch_version, patch_start_date,p.release_date
	ORDER BY patch_version
```

## ***/v2/players/{player_id}/game_exp/***
```sql 
	SELECT pl.id,
	    COALESCE(pl.nick,'unknown') AS player_nick,
	    json_agg(ma.id ORDER BY ma.start_time) AS match_id,
	    json_agg(h.localized_name ORDER BY match_id) AS hero_localized_name,
	    json_agg(round((ma.duration )/60.00, 2) ORDER BY match_id ) AS match_duration_minutes,
	    json_agg((COALESCE((mpd.xp_hero ), 0) + 
		    COALESCE(mpd.xp_creep ,0) +
		    COALESCE(mpd.xp_other ,0) + 
		    COALESCE(mpd.xp_roshan ,0) )ORDER BY match_id) AS experience_gained,
	    json_agg(mpd.level ORDER BY match_id) AS level_gained,
	json_agg((ma.radiant_win = (mpd.player_slot < 5)) ORDER BY match_id) AS winner
	FROM public.matches_players_details mpd
	INNER JOIN public.players pl
	    ON mpd.player_id = pl.id
	INNER JOIN public.heroes h
	    ON mpd.hero_id = h.id
	INNER JOIN public.matches ma
	    ON mpd.match_id = ma.id
	WHERE pl.id={player_id}
	GROUP BY pl.id
```

## ***/v2/players/{player_id}/game_objectives/***

```sql 
	SELECT pl.id,
	    COALESCE(pl.nick,'unknown') AS player_nick,
	    ma.id AS match_id,
	    h.localized_name AS hero_localized_name,
	    json_agg( (COALESCE(gm.subtype,'NO_ACTION')) ORDER BY gm.subtype) AS action_made
	FROM public.matches_players_details mpd
	full outer JOIN public.players pl
	    ON mpd.player_id = pl.id
	full outer JOIN public.heroes h
	    ON mpd.hero_id = h.id
	full outer JOIN public.matches ma
	    ON mpd.match_id = ma.id
	full outer JOIN public.game_objectives gm
	    ON gm.match_player_detail_id_1 = mpd.id
	WHERE pl.id={player_id}
	group by pl.id, player_nick, ma.id,h.localized_name
```

## ***/v2/players/{player_id}/abilities/***
```sql 
	SELECT pl.id,
	    COALESCE(pl.nick,'unknown') AS player_nick,
	    h.localized_name AS hero_localized_name,
	    ma.id AS match_id,
	    jsonb_build_object('ability_name', abi.name, 'count',COUNT(abi.name),'upgrade_level', MAX(au.level))AS ability_name
	FROM public.matches_players_details mpd
	FULL OUTER JOIN public.players pl
	    ON mpd.player_id = pl.id
	FULL OUTER JOIN public.heroes h
	    ON mpd.hero_id = h.id
	FULL OUTER JOIN public.matches ma
	    ON mpd.match_id = ma.id
	LEFT JOIN public.ability_upgrades au
	    ON au.match_player_detail_id = mpd.id
	FULL OUTER JOIN public.abilities abi
	    ON au.ability_id = abi.id
	WHERE pl.id={player_id}
	GROUP BY pl.id, player_nick, ma.id,h.localized_name,abi.name
	ORDER BY match_id
```

# V3
## ***/v3/matches/{match_id}/top_purchases/***
```sql 
	SELECT 
            match_with_heroes_and_pruchased.id, 
            json_agg(match_with_heroes_and_pruchased.heroes) 
        FROM (
            SELECT  
                hero_purchased.match_id AS id,
                json_build_object('id', hero_purchased.hero_id, 'name', hero_purchased.hero_name, 'top_purchases', array_to_json((array_agg(hero_purchased.top_purchases))[1:5])) AS heroes 
            FROM (
                SELECT 
                    mpd.match_id AS match_id,
                    he.id AS hero_id,
                    he.localized_name AS hero_name, 
                    json_build_object('id', pl.item_id,'name',i.name,'count',COUNT(pl.item_id)) AS top_purchases
                FROM matches_players_details mpd
                LEFT JOIN purchase_logs pl 	ON mpd.id = match_player_detail_id
                LEFT JOIN heroes he 		ON mpd.hero_id = he.id
                LEFT JOIN items i 			ON i.id = pl.item_id
                LEFT JOIN matches m 		ON m.id = mpd.match_id
                WHERE match_id = {match_id} AND (m.radiant_win AND mpd.player_slot < 5 OR NOT m.radiant_win AND mpd.player_slot > 10)
                GROUP BY he.id, he.localized_name, i.name,pl.item_id, mpd.match_id
                ORDER BY he.id, COUNT(pl.item_id) DESC,i.name, pl.item_id) AS hero_purchased
            GROUP BY hero_purchased.match_id, hero_purchased.hero_id, hero_purchased.hero_name) AS match_with_heroes_and_pruchased
        GROUP BY match_with_heroes_and_pruchased.id
```

## ***/v3/abilities/{ability_id}/usage/***
```sql 
	WITH only_max_rows AS (
	SELECT with_count.a_name AS ability_name, with_count.h_id AS hero_id, with_count.h_name AS hero_name, with_count.buckets AS bucket, COUNT(*) AS count, with_count.winner AS win
	FROM (	SELECT CASE  
				WHEN (without_count.bucket >= 0  AND without_count.bucket < 10) THEN '0-9'
				WHEN (without_count.bucket >= 10 AND without_count.bucket < 20) THEN '10-19'
				WHEN (without_count.bucket >= 20 AND without_count.bucket < 30) THEN '20-29'
				WHEN (without_count.bucket >= 30 AND without_count.bucket < 40) THEN '30-39'
				WHEN (without_count.bucket >= 40 AND without_count.bucket < 50) THEN '40-49'
				WHEN (without_count.bucket >= 50 AND without_count.bucket < 60) THEN '50-59'
				WHEN (without_count.bucket >= 60 AND without_count.bucket < 70) THEN '60-69'
				WHEN (without_count.bucket >= 70 AND without_count.bucket < 80) THEN '70-79'
				WHEN (without_count.bucket >= 80 AND without_count.bucket < 90) THEN '80-89'
				WHEN (without_count.bucket >= 90 AND without_count.bucket < 100) THEN '90-99'
				ELSE '100-109' END AS buckets, 
				without_count.a_name AS a_name,
				without_count.h_id AS h_id,
				without_count.h_name AS h_name,
				without_count.winner AS winner
			FROM (
				SELECT au.ability_id AS a_id, a.name AS a_name, h.localized_name AS h_name ,mpd.hero_id AS h_id,  FLOOR((FLOOR(au.time)/ma.duration * 100)) AS bucket, (ma.radiant_win AND mpd.player_slot < 5 OR NOT ma.radiant_win AND mpd.player_slot > 10) AS winner 
				FROM ability_upgrades au
				LEFT JOIN matches_players_details mpd   ON mpd.id = au.match_player_detail_id
				LEFT JOIN matches ma                    ON ma.id = mpd.match_id
				LEFT JOIN heroes h                      ON h.id = mpd.hero_id
				LEFT JOIN abilities a                   ON a.id = au.ability_id
				WHERE au.ability_id = {ability_id}) without_count
		 ) with_count
	GROUP BY ability_name, hero_id, hero_name, bucket, win
	ORDER BY hero_id, win desc)
	
    SELECT only_max_rows.*
    FROM only_max_rows
    INNER JOIN (SELECT MAX(only_max_rows.count) miximal, only_max_rows.hero_id, only_max_rows.win FROM only_max_rows GROUP BY only_max_rows.hero_id, only_max_rows.win) tot ON tot.miximal = only_max_rows.count 
```

## ***/v3/statistics/tower_kills/***
```sql 
	WITH 
    tower_only AS (
        SELECT 
            h.localized_name AS hero_name,
            h.id AS hero_id,
            mpd.match_id AS match_id, 
            obj.subtype,
            obj.time AS time
        FROM matches_players_details mpd
        INNER JOIN heroes h ON h.id = mpd.hero_id
        INNER JOIN game_objectives obj ON obj.match_player_detail_id_1 = mpd.id
        WHERE subtype = 'CHAT_MESSAGE_TOWER_KILL'),

    tower_with_count AS (
        SELECT 
            match_id,
            hero_name,
            hero_id,
            subtype,
            time,
            ROW_NUMBER() OVER(PARTITION BY match_id, hero_id,islands ORDER BY match_id, time) AS gap_and_islands
        FROM(
            SELECT
                islands_order.*,
                (ROW_NUMBER() OVER(ORDER BY match_id, time) - (ROW_NUMBER() OVER(PARTITION BY hero_id ORDER BY match_id, time))) AS islands
            FROM tower_only islands_order
            ) islands_order
        )

    SELECT
        tower_with_count.hero_id,
        tower_with_count.hero_name,
        MAX(tower_with_count.gap_and_islands) biggest_island
    FROM tower_with_count
    GROUP BY hero_id, hero_name
    ORDER BY biggest_island DESC, hero_name, hero_id
```
