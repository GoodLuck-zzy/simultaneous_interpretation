from uuid import uuid4
from app.tables.history import History


class HistoryService:
    @staticmethod
    def create_history(role, data, session_id=None, is_deleted=False):
        history_id = str(uuid4())
        history = History.create_instance(
            id=history_id,
            role=role,
            data=data,
            session_id=session_id,
            is_deleted=is_deleted,
        )
        return history

    @staticmethod
    def update_history(history_id, **kwargs):
        History.update_instance(history_id, **kwargs)
        return History.get_by_id(history_id)

    @staticmethod
    def delete_history_soft(history_id):
        query = History.update(is_deleted=True).where(History.id == history_id)
        num_of_rows_modified = query.execute()
        return num_of_rows_modified > 0

    @staticmethod
    def list_histories(session_id=None):
        params = {"is_deleted": False}
        if session_id:
            params["session_id"] = session_id
        query = History.list(
            params=params,
            order={"order": "created_at", "sort": "desc"},
        )
        return list(query)
