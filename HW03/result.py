from copy import copy
from multiprocessing.sharedctypes import Value
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
        jsonb_build_object('ability_name', abi.name, 'count',COUNT(abi.name),'upgrade_level', MAX(au.level))AS ability_name\
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