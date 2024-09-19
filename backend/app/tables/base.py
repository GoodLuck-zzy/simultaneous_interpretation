import pytz
import datetime
import logging
from app.settings import settings
from playhouse.pool import PooledMySQLDatabase
from app.utils.query_wrapper import QueryWrapper
from peewee import Model
from peewee import PrimaryKeyField, UUIDField, DateTimeField, DateField

logger = logging.getLogger(__name__)


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseWrapper(metaclass=SingletonMeta):
    def __init__(self):
        self.database = settings.mysql.database
        self.user = settings.mysql.user
        self.password = settings.mysql.password
        self.host = settings.mysql.host
        self.port = settings.mysql.port
        self.max_coonnection = settings.mysql.max_connections
        self.__db__ = PooledMySQLDatabase(
            self.database,
            max_connections=self.max_coonnection,
            stale_timeout=300,
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
        )

    def db(self):
        return self.__db__


db_wrapper = DatabaseWrapper()
db = db_wrapper.db()


class ModelBase(Model):
    created_at = DateTimeField(null=True, default=datetime.datetime.utcnow, index=True)
    updated_at = DateTimeField(null=True, default=datetime.datetime.utcnow)

    class Meta:
        database = db

    id = PrimaryKeyField()

    def to_json(self):
        item = {}
        for column, column_info in self._meta.fields.items():
            try:
                column_type = type(column_info)
                column_value = getattr(self, column)
                item[column] = self._normalize_model_field(column_value, column_type)
            except Exception as e:
                logger.error(e)
                pass
        return item

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.utcnow()
        return super(ModelBase, self).save(*args, **kwargs)

    @staticmethod
    def _normalize_model_field(value, field_type):
        if value is None:
            return None

        if isinstance(value, str):
            return value

        if field_type == UUIDField:
            return str(value)
        elif field_type == DateTimeField:
            return value.astimezone(pytz.timezone("Asia/Shanghai")).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        elif field_type == DateField:
            return value.strftime("%Y-%m-%d")
        else:
            return value

    @classmethod
    def bulk_create(cls, list):
        with cls._meta.database:
            return cls.insert_many(list).execute()

    def create_instance_with_connection(self, **kwargs):
        with self._meta.database:
            return self.create(**kwargs)

    def delete_instance_with_connection(self):
        with self._meta.database:
            return self.delete_instance()

    @classmethod
    def create_instance(cls, **kwargs):
        with cls._meta.database:
            record = cls.create(**kwargs)
            return record

    @classmethod
    def update_instance(cls, id, **kwargs):
        with cls._meta.database:
            query = cls.update(**kwargs).where(cls.id == id)
            return query.execute()

    @classmethod
    def get_by_id(cls, _id):
        with cls._meta.database:
            try:
                instance = cls.get(cls.id == _id)
                return instance
            except cls.DoesNotExist:
                return None

    @classmethod
    def delete_by_id(cls, _id):
        with cls._meta.database:
            instance = cls.get_by_id(_id)
            if instance:
                instance.delete_instance()
                return True
        return False

    @classmethod
    def list(cls, params, order=None, limit=None, offset=None):
        if order is None:
            order = []
        return QueryWrapper(cls).list(
            params=params, order=order, limit=limit, offset=offset
        )

    @classmethod
    def delete_by_query(cls, **params):
        return QueryWrapper(cls).delete(**params)
