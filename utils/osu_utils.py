from typing import Optional
from utils.gfg_api import Score
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
