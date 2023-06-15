# osu!Goldfish API Wrapper

from typing import Optional
import requests
from datetime import datetime
from ossapi import Mod

from utils.emojis import (
    RANKING_SSH,
    RANKING_SS,
    RANKING_SH,
    RANKING_S,
    RANKING_A,
    RANKING_B,
    RANKING_C,
    RANKING_D,
    RANKING_F
)


API_URL = 'https://api.victoryu.dev/v1/'


class UserStats:
    def __init__(self, gamemode, data):
        self.gamemode = gamemode
        self.total_score = data['tscore']
        self.ranked_score = data['rscore']
        self.pp = data['pp']
        self.playcount = data['plays']
        self.playtime = data['playtime']
        self.acc = data['acc']
        self.max_combo = data['max_combo']
        self.total_hits = data['total_hits']
        self.replay_views = data['replay_views']
        self.xh_count = data['xh_count']
        self.x_count = data['x_count']
        self.sh_count = data['sh_count']
        self.s_count = data['s_count']
        self.a_count = data['a_count']
        self.rank = data['rank']
        self.country_rank = data['country_rank']


class User:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.country = data['country']
        self.creation_time = datetime.fromtimestamp(data['creation_time'])
        self.latest_activity = datetime.fromtimestamp(data['latest_activity'])
        self.stats = None

    def add_stats(self, stats):
        self.stats = stats


class Beatmap:
    def __init__(self, data):
        self.md5 = data['md5']
        self.diff_id = data['id']
        self.set_id = data['set_id']
        self.artist = data['artist']
        self.title = data['title']
        self.difficulty = data['version']
        self.creator = data['creator']
        self.last_update = datetime.fromisoformat(
            data['last_update'] + '+00:00'
        )
        self.length = data['total_length']
        self.max_combo = data['max_combo']
        self.status = data['status']
        self.plays = data['plays']
        self.passes = data['passes']
        self.mode = data['mode']
        self.bpm = data['bpm']
        self.cs = data['cs']
        self.od = data['od']
        self.ar = data['ar']
        self.hp = data['hp']
        self.star_rating = data['diff']


class Score:
    def __init__(self, data):
        self.id = data['id']
        self.score = data['score']
        self.pp = data['pp']
        self.acc = data['acc']
        self.max_combo = data['max_combo']
        self.mods = Mod(data['mods'])
        self.n300 = data['n300']
        self.n100 = data['n100']
        self.n50 = data['n50']
        self.nmiss = data['nmiss']
        self.grade = data['grade']
        self.status = data['status']
        self.mode = data['mode']
        self.play_time = datetime.fromisoformat(data['play_time'] + '+00:00')
        self.perfect = bool(data['perfect'])
        self.beatmap = Beatmap(data['beatmap'])
        self.time_elapsed = data['time_elapsed']


def api_get(endpoint, params=None):
    # Returns the response for the given endpoint and parameters
    r = requests.get(API_URL + endpoint, params=params)
    # does this do anything ?
    r.raise_for_status()
    return r


def get_player_count():
    # Returns number of players online
    res = api_get('get_player_count').json()
    return res['counts']


def get_player_info(uid=None, name=None, mode='0') -> User:
    # Returns player stats for the given gamemode
    json = ''
    if uid:
        json = api_get('get_player_info', {
                       'id': uid, 'scope': 'all'}).json()
    elif name:
        json = api_get('get_player_info', {
                       'name': name, 'scope': 'all'}).json()
    else:
        raise ValueError

    player = User(json['player']['info'])
    stats = UserStats(mode, json['player']['stats'][mode])
    player.add_stats(stats)
    return player


def get_player_scores(uid=None, name=None, scope='recent', mode=0) \
        -> list[Score]:
    # Returns a list of player scores
    # Scope can be 'recent' or 'best'
    json = ''
    if uid:
        json = api_get('get_player_scores', {
                       'id': uid, 'scope': scope, 'mode': mode}).json()
    elif name:
        json = api_get('get_player_scores', {
                       'name': name, 'scope': scope, 'mode': mode}).json()
    else:
        raise ValueError
    scores = []
    for score in json['scores']:
        scores.append(Score(score))
    return scores


def get_grade_emoji(grade: str) -> Optional[str]:
    """Return the corresponding emoji for the given osu! score grade."""
    if grade == 'XH':
        return RANKING_SSH
    elif grade == 'X':
        return RANKING_SS
    elif grade == 'SH':
        return RANKING_SH
    elif grade == 'S':
        return RANKING_S
    elif grade == 'A':
        return RANKING_A
    elif grade == 'B':
        return RANKING_B
    elif grade == 'C':
        return RANKING_C
    elif grade == 'D':
        return RANKING_D
    elif grade == 'F':
        return RANKING_F


def calc_map_completion(score: Score) -> float:
    """Calculate the percentage of map completed as given by <score>."""
    return score.time_elapsed / 1000 / score.beatmap.length * 100


def calc_fc_pp():
    return '1'


def calc_fc_acc():
    return '1'
