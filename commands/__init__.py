from .general import setup as general_setup
from .matches import setup as matches_setup
from .users import setup as users_setup

def setup(bot):
    general_setup(bot)
    matches_setup(bot)
    users_setup(bot)
