from app.tables.base import ModelBase
from peewee import CharField


class Audio(ModelBase):
    id = CharField(max_length=64, primary_key=True)
    type = CharField(max_length=32, null=False)
    root_dir_path = CharField(max_length=255, null=False)
    filename = CharField(max_length=255, null=False)

    class Meta:
        table_name = "audio"
