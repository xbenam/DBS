from copy import copy
from multiprocessing.sharedctypes import Value
from unicodedata import name
import psycopg2, os
from dotenv import load_dotenv

# load env file
load_dotenv()
env = os.environ

conn = None
cur = None

def DBconnect():
    global conn, cur

    # creating connection to database
    conn = psycopg2.connect(dbname=os.getenv('DBNAME'), 
                        user=os.getenv('DBUSER'),
                        password=os.getenv('DBPASS'), 
                        host=os.getenv('DBPORT'))
    # create cursor to work with database
    cur = conn.cursor()


def DBdisconnect():
    global conn, cur
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()


def version():
    version_and_size = {}
    version_and_size['pgsql'] = {}

    # get version
    cur.execute("SELECT Version();")

    # store version into dictionary
    version_and_size['pgsql']['version'] = cur.fetchone()[0]

    # get database size
    cur.execute("SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;")

    # store it into dictionary
    version_and_size['pgsql']['dota2_db_size'] = cur.fetchone()[0]
    return version_and_size 


# V2/patch endpoint
def patches():
    cur.execute("SELECT 	p.name AS patch_version,\
		CAST(extract(epoch FROM p.release_date) AS INT) AS patch_start_date,\
		CAST(extract(epoch FROM LEAD(p.release_date) OVER (ORDER BY p.release_date) ) AS INT) AS patch_end_date,\
 		json_agg(m.id) AS match_id,\
		json_agg(round((m.duration)/60.00, 2)) as match_duration\
        FROM public.patches p\
        LEFT JOIN public.matches m\
        ON m.start_time BETWEEN CAST(extract(epoch FROM p.release_date) AS INT) and CAST(extract(epoch FROM p.release_date) AS INT) + 86400\
        GROUP BY patch_version, patch_start_date,p.release_date\
        ORDER BY patch_version")

    fatched = cur.fetchall()
    patch_and_matches = {'patches':[]}
    match = []
    for it in fatched:
        if it[3][0] != None:
            for i in range(len(it[3])):
                match.append({'match_id':it[3][i], 'duration':it[4][i]})
        patch_and_matches['patches'].append({'patch_version':it[0], 
                                        'patch_start_date':it[1],
                                        'patch_end_date':it[2],
                                        'matches':copy(match)}) 
        match.clear()

    return patch_and_matches


# V2/game_experience endpoint
def game_exp(player_id):
    cur.execute("\
        SELECT pl.id,\
            COALESCE(pl.nick,'unknown') AS player_nick,\
            json_agg(ma.id ORDER BY ma.start_time) AS match_id,\
            json_agg(h.localized_name ORDER BY match_id) AS hero_localized_name,\
            json_agg(round((ma.duration )/60.00, 2) ORDER BY match_id ) AS match_duration_minutes,\
            json_agg((COALESCE((mpd.xp_hero ), 0) + \
                    COALESCE(mpd.xp_creep ,0) +\
                    COALESCE(mpd.xp_other ,0) + \
                    COALESCE(mpd.xp_roshan ,0) )ORDER BY match_id) AS experience_gained,\
            json_agg(mpd.level ORDER BY match_id) AS level_gained,\
		    json_agg((ma.radiant_win = (mpd.player_slot < 5)) ORDER BY match_id) AS winner\
        FROM public.matches_players_details mpd\
        INNER JOIN public.players pl\
            ON mpd.player_id = pl.id\
        INNER JOIN public.heroes h\
            ON mpd.hero_id = h.id\
        INNER JOIN public.matches ma\
            ON mpd.match_id = ma.id\
        WHERE pl.id=%s\
        GROUP BY pl.id",(player_id,))

    fatched = cur.fetchall()

    matches = []
    fatched = fatched[0]
    for i in range(len(fatched[2])):
        matches.append({
            'match_id':fatched[2][i],
            'hero_localized_name':fatched[3][i],
            'match_duration_minutes':fatched[4][i],
            'experiences_gained':fatched[5][i],
            'level_gained':fatched[6][i],
            'winner':fatched[7][i]
        })
    game = { 'id':fatched[0],
            'player_nick':fatched[1],
            'matches':matches}

    return game


# V2/game_objective endpoint
def game_obj(player_id):
    cur.execute("\
            SELECT pl.id,\
            COALESCE(pl.nick,'unknown') AS player_nick,\
            ma.id AS match_id,\
            h.localized_name AS hero_localized_name,\
            json_agg( (COALESCE(gm.subtype,'NO_ACTION')) ORDER BY gm.subtype) AS action_made\
        FROM public.matches_players_details mpd\
        full outer JOIN public.players pl\
            ON mpd.player_id = pl.id\
        full outer JOIN public.heroes h\
            ON mpd.hero_id = h.id\
        full outer JOIN public.matches ma\
            ON mpd.match_id = ma.id\
        full outer JOIN public.game_objectives gm\
            ON gm.match_player_detail_id_1 = mpd.id\
        WHERE pl.id=%s\
        group by pl.id, player_nick, ma.id,h.localized_name",(player_id,))

    fatched = cur.fetchall()
    matches = []
    for game in fatched:
        actions = []
        
        action_name_and_count = {}
        for action in game[4]:
            if action in action_name_and_count:
                action_name_and_count[action] += 1
            else:
                action_name_and_count[action] = 1
        for action_name in action_name_and_count.keys():
            actions.append({'hero_action':action_name,'count':action_name_and_count[action_name]})
        matches.append({'match_id':game[2],
                        'hero_localized_name':game[3],
                        'actions':copy(actions)})

    total = {'id':fatched[0][0],
            'player_nick':fatched[0][1],
            'matches':matches}
    return total


# V2/ability endpoint
def abilities(player_id):
    cur.execute("\
        SELECT pl.id,\
        COALESCE(pl.nick,'unknown') AS player_nick,\
        h.localized_name AS hero_localized_name,\
        ma.id AS match_id,\
        jsonb_build_===('ability_name', abi.name, 'count',COUNT(abi.name),'upgrade_level', MAX(au.level))AS ability_name\
        FROM public.matches_players_details mpd\
        FULL OUTER JOIN public.players pl\
            ON mpd.player_id = pl.id\
        FULL OUTER JOIN public.heroes h\
            ON mpd.hero_id = h.id\
        FULL OUTER JOIN public.matches ma\
            ON mpd.match_id = ma.id\
        LEFT JOIN public.ability_upgrades au\
            ON au.match_player_detail_id = mpd.id\
        FULL OUTER JOIN public.abilities abi\
            ON au.ability_id = abi.id\
        WHERE pl.id=%s\
        GROUP BY pl.id, player_nick, ma.id,h.localized_name,abi.name\
        ORDER BY match_id",(player_id,))

    fatched = cur.fetchall()
    matches = []
    abilities = []
    check = None
    for i in range(len(fatched)):
        if check is None:
            check = fatched[i][3]
            abilities.append(fatched[i][4])
            continue
        elif check == fatched[i][3]:
            abilities.append(fatched[i][4])
            continue
        
        matches.append({'match_id':fatched[i-1][3],
                        'hero_localized_name':fatched[i-1][2],
                        'abilities':copy(abilities)})

        abilities.clear()
        check = fatched[i][3]
        abilities.append(fatched[i][4])

    matches.append({'match_id':fatched[i][3],
                        'hero_localized_name':fatched[i][2],
                        'abilities':copy(abilities)})

    total = {'id':fatched[0][0],
            'player_nick':fatched[0][1],
            'matches':matches}

    return total


# V3/top_purchases endpoint
def purchase_item(match_id):
    cur.execute(
        """
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
                WHERE match_id = %s AND (m.radiant_win AND mpd.player_slot < 5 OR NOT m.radiant_win AND mpd.player_slot > 10)
                GROUP BY he.id, he.localized_name, i.name,pl.item_id, mpd.match_id
                ORDER BY he.id, COUNT(pl.item_id) DESC,i.name, pl.item_id) AS hero_purchased
            GROUP BY hero_purchased.match_id, hero_purchased.hero_id, hero_purchased.hero_name) AS match_with_heroes_and_pruchased
        GROUP BY match_with_heroes_and_pruchased.id
        """,(match_id,))
    fatched = cur.fetchone()
    return {'id' : fatched[0], 'heroes' :fatched[1]}


# V3/usage endpoint
def usage(ability_id):
    cur.execute(
    """
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
				WHERE au.ability_id = %s) without_count
		 ) with_count
	GROUP BY ability_name, hero_id, hero_name, bucket, win
	ORDER BY hero_id, win desc)
	
    SELECT only_max_rows.*
    FROM only_max_rows
    INNER JOIN (SELECT MAX(only_max_rows.count) miximal, only_max_rows.hero_id, only_max_rows.win FROM only_max_rows GROUP BY only_max_rows.hero_id, only_max_rows.win) tot ON tot.miximal = only_max_rows.count 
    """,(ability_id,))

    fatched = cur.fetchall()
    actual_hero = None
    actual_winner = None
    result = {}
    heroes = []
    hero = {}
    if len(fatched) != 0:
        actual_hero = fatched[0][2]
        result["id"] = ability_id
        result["name"] = fatched[0][0]
    for i in fatched:
        if (i[2] != actual_hero):
            heroes.append(copy(hero))
            hero = {}
        hero["id"] = i[1]
        hero["name"] = i[2]
        if(i[5]):
            hero["usage_winners"] = {"bucket":i[3], "count":i[4]}
        else:
            hero["usage_loosers"] = {"bucket":i[3], "count":i[4]}
    heroes.append(hero)
    result["heroes"] = heroes

    return result

def tower_kills_by_hero():
    cur.execute(
    """
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
    """)
    fatched = cur.fetchall()
    heroes = []
    hero = {}
    for h in fatched:
        hero["id"] = h[0]
        hero["name"] = h[1]
        hero["tower_kills"] = h[2]
        heroes.append(hero)
        hero = {}
    return {"heroes":heroes}