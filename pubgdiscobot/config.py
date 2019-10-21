import os
from pubg_python import Shard
from dotenv import load_dotenv
load_dotenv()

_delay_ = 600

_version_ = '0.2.0'
_prefix_ = 'pubg '
_discord_token_ = os.getenv("DISCORD_TOKEN")
_pubg_token_ = os.getenv("PUBG_TOKEN")
_pubg_tracker_token_ = os.getenv("PUBG_TRACKER_TOKEN")
_pubg_shard_ = Shard.STEAM

_topgg_token_ = os.getenv("TOPGG_TOKEN")

_mongodb_host_ = os.getenv("MONGODB_HOST", 'localhost')
_mongodb_port_ = os.getenv("MONGODB_PORT", 27017)

_owner_id_ = os.getenv("OWNER_ID", 132402729887727616)
_extensions_ = [
    'register', 'me', 'notify', 'prefix', 'reload', 'vote', 'topgg', 'help']
