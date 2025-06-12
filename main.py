from cultist_chan_bot.config import load_config
from cultist_chan_bot.db import init_db


def main() -> None:
    cfg = load_config()
    init_db(cfg.DB_PATH)


if __name__ == "__main__":
    main()
