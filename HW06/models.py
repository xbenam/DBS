# coding: utf-8
# generated by flask-sqlacodegen
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()



class Ability(db.Model):
    __tablename__ = 'abilities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)



class AbilityUpgrade(db.Model):
    __tablename__ = 'ability_upgrades'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    ability_id = db.Column(db.ForeignKey('abilities.id'))
    match_player_detail_id = db.Column(db.ForeignKey('matches_players_details.id'))
    level = db.Column(db.Integer)
    time = db.Column(db.Integer)

    ability = db.relationship('Ability', primaryjoin='AbilityUpgrade.ability_id == Ability.id', backref='ability_upgrades')
    match_player_detail = db.relationship('MatchesPlayersDetail', primaryjoin='AbilityUpgrade.match_player_detail_id == MatchesPlayersDetail.id', backref='ability_upgrades')



class AuthGroup(db.Model):
    __tablename__ = 'auth_group'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.String(150), nullable=False, unique=True)



class AuthGroupPermission(db.Model):
    __tablename__ = 'auth_group_permissions'
    __table_args__ = (
        db.UniqueConstraint('group_id', 'permission_id'),
    )

    id = db.Column(db.BigInteger, primary_key=True, server_default=db.FetchedValue())
    group_id = db.Column(db.ForeignKey('auth_group.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    permission_id = db.Column(db.ForeignKey('auth_permission.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    group = db.relationship('AuthGroup', primaryjoin='AuthGroupPermission.group_id == AuthGroup.id', backref='auth_group_permissions')
    permission = db.relationship('AuthPermission', primaryjoin='AuthGroupPermission.permission_id == AuthPermission.id', backref='auth_group_permissions')



class AuthPermission(db.Model):
    __tablename__ = 'auth_permission'
    __table_args__ = (
        db.UniqueConstraint('content_type_id', 'codename'),
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.String(255), nullable=False)
    content_type_id = db.Column(db.ForeignKey('django_content_type.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    codename = db.Column(db.String(100), nullable=False)

    content_type = db.relationship('DjangoContentType', primaryjoin='AuthPermission.content_type_id == DjangoContentType.id', backref='auth_permissions')



class AuthUser(db.Model):
    __tablename__ = 'auth_user'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    password = db.Column(db.String(128), nullable=False)
    last_login = db.Column(db.DateTime(True))
    is_superuser = db.Column(db.Boolean, nullable=False)
    username = db.Column(db.String(150), nullable=False, unique=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(254), nullable=False)
    is_staff = db.Column(db.Boolean, nullable=False)
    is_active = db.Column(db.Boolean, nullable=False)
    date_joined = db.Column(db.DateTime(True), nullable=False)



class AuthUserGroup(db.Model):
    __tablename__ = 'auth_user_groups'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'group_id'),
    )

    id = db.Column(db.BigInteger, primary_key=True, server_default=db.FetchedValue())
    user_id = db.Column(db.ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    group_id = db.Column(db.ForeignKey('auth_group.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    group = db.relationship('AuthGroup', primaryjoin='AuthUserGroup.group_id == AuthGroup.id', backref='auth_user_groups')
    user = db.relationship('AuthUser', primaryjoin='AuthUserGroup.user_id == AuthUser.id', backref='auth_user_groups')



class AuthUserUserPermission(db.Model):
    __tablename__ = 'auth_user_user_permissions'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'permission_id'),
    )

    id = db.Column(db.BigInteger, primary_key=True, server_default=db.FetchedValue())
    user_id = db.Column(db.ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)
    permission_id = db.Column(db.ForeignKey('auth_permission.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    permission = db.relationship('AuthPermission', primaryjoin='AuthUserUserPermission.permission_id == AuthPermission.id', backref='auth_user_user_permissions')
    user = db.relationship('AuthUser', primaryjoin='AuthUserUserPermission.user_id == AuthUser.id', backref='auth_user_user_permissions')



class Chat(db.Model):
    __tablename__ = 'chats'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    match_player_detail_id = db.Column(db.ForeignKey('matches_players_details.id'))
    message = db.Column(db.Text)
    time = db.Column(db.Integer)
    nick = db.Column(db.Text)

    match_player_detail = db.relationship('MatchesPlayersDetail', primaryjoin='Chat.match_player_detail_id == MatchesPlayersDetail.id', backref='chats')



class ClusterRegion(db.Model):
    __tablename__ = 'cluster_regions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)



class DjangoAdminLog(db.Model):
    __tablename__ = 'django_admin_log'
    __table_args__ = (
        db.CheckConstraint('action_flag >= 0'),
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    action_time = db.Column(db.DateTime(True), nullable=False)
    object_id = db.Column(db.Text)
    object_repr = db.Column(db.String(200), nullable=False)
    action_flag = db.Column(db.SmallInteger, nullable=False)
    change_message = db.Column(db.Text, nullable=False)
    content_type_id = db.Column(db.ForeignKey('django_content_type.id', deferrable=True, initially='DEFERRED'), index=True)
    user_id = db.Column(db.ForeignKey('auth_user.id', deferrable=True, initially='DEFERRED'), nullable=False, index=True)

    content_type = db.relationship('DjangoContentType', primaryjoin='DjangoAdminLog.content_type_id == DjangoContentType.id', backref='django_admin_logs')
    user = db.relationship('AuthUser', primaryjoin='DjangoAdminLog.user_id == AuthUser.id', backref='django_admin_logs')



class DjangoContentType(db.Model):
    __tablename__ = 'django_content_type'
    __table_args__ = (
        db.UniqueConstraint('app_label', 'model'),
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    app_label = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)



class DjangoMigration(db.Model):
    __tablename__ = 'django_migrations'

    id = db.Column(db.BigInteger, primary_key=True, server_default=db.FetchedValue())
    app = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    applied = db.Column(db.DateTime(True), nullable=False)



class DjangoSession(db.Model):
    __tablename__ = 'django_session'

    session_key = db.Column(db.String(40), primary_key=True, index=True)
    session_data = db.Column(db.Text, nullable=False)
    expire_date = db.Column(db.DateTime(True), nullable=False, index=True)



class DoctrineMigrationVersion(db.Model):
    __tablename__ = 'doctrine_migration_versions'

    version = db.Column(db.String(191), primary_key=True)
    executed_at = db.Column(db.DateTime, server_default=db.FetchedValue())
    execution_time = db.Column(db.Integer)



class FlywaySchemaHistory(db.Model):
    __tablename__ = 'flyway_schema_history'

    installed_rank = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(50))
    description = db.Column(db.String(200), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    script = db.Column(db.String(1000), nullable=False)
    checksum = db.Column(db.Integer)
    installed_by = db.Column(db.String(100), nullable=False)
    installed_on = db.Column(db.DateTime, nullable=False, server_default=db.FetchedValue())
    execution_time = db.Column(db.Integer, nullable=False)
    success = db.Column(db.Boolean, nullable=False, index=True)



class GameObjective(db.Model):
    __tablename__ = 'game_objectives'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    match_player_detail_id_1 = db.Column(db.ForeignKey('matches_players_details.id'))
    match_player_detail_id_2 = db.Column(db.ForeignKey('matches_players_details.id'))
    key = db.Column(db.Integer)
    subtype = db.Column(db.Text)
    team = db.Column(db.Integer)
    time = db.Column(db.Integer)
    value = db.Column(db.Integer)
    slot = db.Column(db.Integer)

    matches_players_detail = db.relationship('MatchesPlayersDetail', primaryjoin='GameObjective.match_player_detail_id_1 == MatchesPlayersDetail.id', backref='matchesplayersdetail_game_objectives')
    matches_players_detail1 = db.relationship('MatchesPlayersDetail', primaryjoin='GameObjective.match_player_detail_id_2 == MatchesPlayersDetail.id', backref='matchesplayersdetail_game_objectives_0')



class Hero(db.Model):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    localized_name = db.Column(db.Text)



class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)



class Match(db.Model):
    __tablename__ = 'matches'

    id = db.Column(db.Integer, primary_key=True)
    cluster_region_id = db.Column(db.ForeignKey('cluster_regions.id'))
    start_time = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    tower_status_radiant = db.Column(db.Integer)
    tower_status_dire = db.Column(db.Integer)
    barracks_status_radiant = db.Column(db.Integer)
    barracks_status_dire = db.Column(db.Integer)
    first_blood_time = db.Column(db.Integer)
    game_mode = db.Column(db.Integer)
    radiant_win = db.Column(db.Boolean)
    negative_votes = db.Column(db.Integer)
    positive_votes = db.Column(db.Integer)

    cluster_region = db.relationship('ClusterRegion', primaryjoin='Match.cluster_region_id == ClusterRegion.id', backref='matches')



class MatchesPlayersDetail(db.Model):
    __tablename__ = 'matches_players_details'
    __table_args__ = (
        db.Index('idx_match_id_player_id', 'match_id', 'player_slot', 'id'),
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    match_id = db.Column(db.ForeignKey('matches.id'))
    player_id = db.Column(db.ForeignKey('players.id'))
    hero_id = db.Column(db.ForeignKey('heroes.id'))
    player_slot = db.Column(db.Integer)
    gold = db.Column(db.Integer)
    gold_spent = db.Column(db.Integer)
    gold_per_min = db.Column(db.Integer)
    xp_per_min = db.Column(db.Integer)
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    assists = db.Column(db.Integer)
    denies = db.Column(db.Integer)
    last_hits = db.Column(db.Integer)
    stuns = db.Column(db.Integer)
    hero_damage = db.Column(db.Integer)
    hero_healing = db.Column(db.Integer)
    tower_damage = db.Column(db.Integer)
    item_id_1 = db.Column(db.ForeignKey('items.id'))
    item_id_2 = db.Column(db.ForeignKey('items.id'))
    item_id_3 = db.Column(db.ForeignKey('items.id'))
    item_id_4 = db.Column(db.ForeignKey('items.id'))
    item_id_5 = db.Column(db.ForeignKey('items.id'))
    item_id_6 = db.Column(db.ForeignKey('items.id'))
    level = db.Column(db.Integer)
    leaver_status = db.Column(db.Integer)
    xp_hero = db.Column(db.Integer)
    xp_creep = db.Column(db.Integer)
    xp_roshan = db.Column(db.Integer)
    xp_other = db.Column(db.Integer)
    gold_other = db.Column(db.Integer)
    gold_death = db.Column(db.Integer)
    gold_buyback = db.Column(db.Integer)
    gold_abandon = db.Column(db.Integer)
    gold_sell = db.Column(db.Integer)
    gold_destroying_structure = db.Column(db.Integer)
    gold_killing_heroes = db.Column(db.Integer)
    gold_killing_creeps = db.Column(db.Integer)
    gold_killing_roshan = db.Column(db.Integer)
    gold_killing_couriers = db.Column(db.Integer)

    hero = db.relationship('Hero', primaryjoin='MatchesPlayersDetail.hero_id == Hero.id', backref='matches_players_details')
    item = db.relationship('Item', primaryjoin='MatchesPlayersDetail.item_id_1 == Item.id', backref='item_item_item_item_item_matches_players_details')
    item1 = db.relationship('Item', primaryjoin='MatchesPlayersDetail.item_id_2 == Item.id', backref='item_item_item_item_item_matches_players_details_0')
    item2 = db.relationship('Item', primaryjoin='MatchesPlayersDetail.item_id_3 == Item.id', backref='item_item_item_item_item_matches_players_details')
    item3 = db.relationship('Item', primaryjoin='MatchesPlayersDetail.item_id_4 == Item.id', backref='item_item_item_item_item_matches_players_details_0')
    item4 = db.relationship('Item', primaryjoin='MatchesPlayersDetail.item_id_5 == Item.id', backref='item_item_item_item_item_matches_players_details')
    item5 = db.relationship('Item', primaryjoin='MatchesPlayersDetail.item_id_6 == Item.id', backref='item_item_item_item_item_matches_players_details_0')
    match = db.relationship('Match', primaryjoin='MatchesPlayersDetail.match_id == Match.id', backref='matches_players_details')
    player = db.relationship('Player', primaryjoin='MatchesPlayersDetail.player_id == Player.id', backref='matches_players_details')



class Patch(db.Model):
    __tablename__ = 'patches'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    name = db.Column(db.Text, nullable=False)
    release_date = db.Column(db.DateTime, nullable=False)



class PlayerAction(db.Model):
    __tablename__ = 'player_actions'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    unit_order_none = db.Column(db.Integer)
    unit_order_move_to_position = db.Column(db.Integer)
    unit_order_move_to_target = db.Column(db.Integer)
    unit_order_attack_move = db.Column(db.Integer)
    unit_order_attack_target = db.Column(db.Integer)
    unit_order_cast_position = db.Column(db.Integer)
    unit_order_cast_target = db.Column(db.Integer)
    unit_order_cast_target_tree = db.Column(db.Integer)
    unit_order_cast_no_target = db.Column(db.Integer)
    unit_order_cast_toggle = db.Column(db.Integer)
    unit_order_hold_position = db.Column(db.Integer)
    unit_order_train_ability = db.Column(db.Integer)
    unit_order_drop_item = db.Column(db.Integer)
    unit_order_give_item = db.Column(db.Integer)
    unit_order_pickup_item = db.Column(db.Integer)
    unit_order_pickup_rune = db.Column(db.Integer)
    unit_order_purchase_item = db.Column(db.Integer)
    unit_order_sell_item = db.Column(db.Integer)
    unit_order_disassemble_item = db.Column(db.Integer)
    unit_order_move_item = db.Column(db.Integer)
    unit_order_cast_toggle_auto = db.Column(db.Integer)
    unit_order_stop = db.Column(db.Integer)
    unit_order_buyback = db.Column(db.Integer)
    unit_order_glyph = db.Column(db.Integer)
    unit_order_eject_item_from_stash = db.Column(db.Integer)
    unit_order_cast_rune = db.Column(db.Integer)
    unit_order_ping_ability = db.Column(db.Integer)
    unit_order_move_to_direction = db.Column(db.Integer)
    match_player_detail_id = db.Column(db.ForeignKey('matches_players_details.id'))

    match_player_detail = db.relationship('MatchesPlayersDetail', primaryjoin='PlayerAction.match_player_detail_id == MatchesPlayersDetail.id', backref='player_actions')



class PlayerRating(db.Model):
    __tablename__ = 'player_ratings'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    player_id = db.Column(db.ForeignKey('players.id'))
    total_wins = db.Column(db.Integer)
    total_matches = db.Column(db.Integer)
    trueskill_mu = db.Column(db.Numeric)
    trueskill_sigma = db.Column(db.Numeric)

    player = db.relationship('Player', primaryjoin='PlayerRating.player_id == Player.id', backref='player_ratings')



class PlayerTime(db.Model):
    __tablename__ = 'player_times'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    match_player_detail_id = db.Column(db.ForeignKey('matches_players_details.id'))
    time = db.Column(db.Integer)
    gold = db.Column(db.Integer)
    lh = db.Column(db.Integer)
    xp = db.Column(db.Integer)

    match_player_detail = db.relationship('MatchesPlayersDetail', primaryjoin='PlayerTime.match_player_detail_id == MatchesPlayersDetail.id', backref='player_times')



class Player(db.Model):
    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    nick = db.Column(db.Text)



class PurchaseLog(db.Model):
    __tablename__ = 'purchase_logs'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    match_player_detail_id = db.Column(db.ForeignKey('matches_players_details.id'))
    item_id = db.Column(db.ForeignKey('items.id'))
    time = db.Column(db.Integer)

    item = db.relationship('Item', primaryjoin='PurchaseLog.item_id == Item.id', backref='purchase_logs')
    match_player_detail = db.relationship('MatchesPlayersDetail', primaryjoin='PurchaseLog.match_player_detail_id == MatchesPlayersDetail.id', backref='purchase_logs')



class Teamfight(db.Model):
    __tablename__ = 'teamfights'
    __table_args__ = (
        db.Index('teamfights_match_id_start_teamfight_id_idx', 'match_id', 'start_teamfight', 'id'),
    )

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    match_id = db.Column(db.ForeignKey('matches.id'))
    start_teamfight = db.Column(db.Integer)
    end_teamfight = db.Column(db.Integer)
    last_death = db.Column(db.Integer)
    deaths = db.Column(db.Integer)

    match = db.relationship('Match', primaryjoin='Teamfight.match_id == Match.id', backref='teamfights')



class TeamfightsPlayer(db.Model):
    __tablename__ = 'teamfights_players'

    id = db.Column(db.Integer, primary_key=True, server_default=db.FetchedValue())
    teamfight_id = db.Column(db.ForeignKey('teamfights.id'))
    match_player_detail_id = db.Column(db.ForeignKey('matches_players_details.id'))
    buyback = db.Column(db.Integer)
    damage = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    gold_delta = db.Column(db.Integer)
    xp_start = db.Column(db.Integer)
    xp_end = db.Column(db.Integer)

    match_player_detail = db.relationship('MatchesPlayersDetail', primaryjoin='TeamfightsPlayer.match_player_detail_id == MatchesPlayersDetail.id', backref='teamfights_players')
    teamfight = db.relationship('Teamfight', primaryjoin='TeamfightsPlayer.teamfight_id == Teamfight.id', backref='teamfights_players')
