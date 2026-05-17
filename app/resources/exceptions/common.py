from app.resources.strings import ALREADY_EXISTS


class FKNotFoundError(Exception):
    def __init__(self, message: str, fk_name: str, table_name: str) -> None:
        super().__init__(message)
        self.fk_name = fk_name
        self.table_name = table_name


class AlreadyExistsError(Exception):
    def __init__(
        self,
        message: str | None = None,
        constraint_name: str | None = None,
    ) -> None:
        super().__init__(message or ALREADY_EXISTS)
        self.constraint_name = constraint_name


class NotFoundError[FKType](Exception):
    def __init__(self, *args: object, entity_id: FKType | None = None) -> None:
        super().__init__(*args)
        self.entity_id = entity_id


class ValidationError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
