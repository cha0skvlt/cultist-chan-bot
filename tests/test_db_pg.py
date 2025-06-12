import pytest
from testcontainers.postgres import PostgresContainer


@pytest.mark.asyncio
async def test_db_pg():
    from cultist_chan_bot.core import database, db
    from cultist_chan_bot.core.config import Settings

    with PostgresContainer("postgres:16-alpine") as pg:
        settings = Settings(
            POSTGRES_HOST=pg.get_container_host_ip(),
            POSTGRES_USER=pg.POSTGRES_USER,
            POSTGRES_PASS=pg.POSTGRES_PASSWORD,
            POSTGRES_NAME=pg.POSTGRES_DB,
        )

        await database.create_pool(settings)
        await db.migrate_pg(settings)

        await db.log_airdrop({"name": "Drop"}, "joined")
        await db.log_telemetry("ev", {"k": 1}, "r")
        await db.log_nft_purchase({"id": 1}, "ok", 1.0)
        rows = await db.get_airdrop_history()

        assert rows == [("Drop", "joined", pytest.approx(rows[0][2]))]

        await database.close_pool()

