from .general import setup as general_setup
from .matches import setup as matches_setup
from .users import setup as users_setup
from .season1 import setup as seasion1_setup
from .riotApi import setup as riotApi_setup

def setup(bot):
    general_setup(bot)
    matches_setup(bot)
    users_setup(bot)
    seasion1_setup(bot)
    riotApi_setup(bot)
