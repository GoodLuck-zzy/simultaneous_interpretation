from peewee import fn


class QueryWrapper:
    def __init__(self, model):
        self.model = model

    def check_field_exist(self, field):
        if "." in field:
            field = field.split(".")[0]
        return field in self.model._meta.fields

    def handle_operator(self, field, op, value):
        if "." in field:
            # Split the field into the main part and the subfield
            main_field, sub_field = field.split(".", 1)

            # Check that the main field exists
            if not self.check_field_exist(main_field):
                raise ValueError(f"Field {main_field} does not exist")

            field_expr = fn.JSON_EXTRACT(
                getattr(self.model, main_field), "$." + sub_field
            )
        else:
            # If there is no '.', then it's a normal field
            field_expr = getattr(self.model, field)

        if op == "eq":
            return field_expr == value
        elif op == "neq":
            return field_expr != value
        elif op == "like":
            return field_expr.contains(value)
        elif op == "in":
            return field_expr.in_(value)
        elif op == "not in":
            return field_expr.not_in(value)
        elif op == "le":
            return field_expr <= value
        elif op == "lt":
            return field_expr < value
        elif op == "between":
            return field_expr.between(value[0], value[1])
        # add more operators as needed

    def handle_order(self, order):
        if order["sort"] == "asc":
            return getattr(self.model, order["order"]).asc()
        else:
            return getattr(self.model, order["order"]).desc()

    def generate_total(self, params):
        query = self.model.select()
        for field, value in params.items():
            if self.check_field_exist(field):
                query = query.where(
                    self.handle_operator(field, value["op"], value["value"])
                )
            else:
                query = query.where(getattr(self.model, field) == value)
        return query.count()

    """
    joins = [
        {'model': Model1, 'type': 'inner', 'on': (Model3.user == Model1.id)},
        {'model': Model2, 'type': 'left_outer', 'on': (Model3.session == Model2.id)}
    ]
    """

    def generate_query(
        self, params, order=[], limit=None, offset=None, joins=[], fields=[]
    ):
        query = self.model.select()
        if fields and len(fields):
            query = self.model.select(*fields)

        for join in joins:
            target_model = join.get("model")
            join_type = join.get("type", "inner")
            on_field = join.get("on")
            if join_type == "inner":
                query = query.join(target_model, on=on_field)
            elif join_type == "left_outer":
                query = query.join(target_model, join_type="LEFT_OUTER", on=on_field)

        for field, value in params.items():
            if self.check_field_exist(field):
                if isinstance(value, dict):
                    query = query.where(
                        self.handle_operator(field, value["op"], value["value"])
                    )
                else:
                    query = query.where(getattr(self.model, field) == value)
        orders = []
        for o in order:
            if self.check_field_exist(o["order"]):
                orders.append(self.handle_order(o))
        query = query.order_by(*orders)

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query

    def list(self, params, order=[], limit=None, offset=None):
        with self.model._meta.database:
            query = self.generate_query(
                params=params, order=order, limit=limit, offset=offset
            )
            return query.execute()

    def generate_delete(self, **params):
        query = self.model.delete()
        for field, value in params.items():
            if isinstance(value, dict):
                query = query.where(
                    self.handle_operator(field, value["op"], value["value"])
                )
            else:
                query = query.where(self.handle_operator(field, "eq", value))
        return query

    def delete(self, **params):
        with self.model._meta.database:
            query = self.generate_delete(**params)
            return query.execute()
