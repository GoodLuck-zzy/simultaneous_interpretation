from app.tables.base import ModelBase
from peewee import CharField, BooleanField
from playhouse.mysql_ext import JSONField


class History(ModelBase):
    id = CharField(max_length=64, primary_key=True)
    role = CharField(max_length=64)
    data = JSONField(null=True)   # {type | audio_id | text}
    is_deleted = BooleanField(default=False)
    session_id = CharField(max_length=64)

    class Meta:
        table_name = "history"
