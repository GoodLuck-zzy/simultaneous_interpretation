import configparser
import subprocess
from app.settings import settings

profile = "alembic.ini"
url_title = "alembic"
sqlalchemy_url = "sqlalchemy.url"


# fill db url into sqlalchemy.url
def fill_initial_file():
    sets = settings.mysql
    config = configparser.ConfigParser()
    config.read(profile)
    config[url_title][
        sqlalchemy_url
    ] = f"mysql+pymysql://{sets.user}:{sets.password}@{sets.host}:{sets.port}/{sets.database}"

    with open(profile, "w") as configfile:
        config.write(configfile)


def upgrade_database_version(tag="head"):
    subprocess.run(["alembic", "upgrade", tag])


def downgrade_database_version(tag="base"):
    subprocess.run(["alembic", "downgrade", tag])


def migrate_table():
    fill_initial_file()
    upgrade_database_version("head")


def init_database():
    migrate_table()


if __name__ == "__main__":
    init_database()
