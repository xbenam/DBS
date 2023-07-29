def purchase_item(db, match_id):
    queryAsObject = (db.engine.execute("""
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
        """,(match_id,)))
    # extracting result from objectQuery as list of dictioneries
    result = result = [dict(row) for row in queryAsObject]
    return {'id' : result[0]['id'], 'heroes' : result[0]['json_agg']}
