from enum import StrEnum


class Status(StrEnum):
    ADDED = 'added'
    MODIFIED = 'modified'


class Success(StrEnum):
    SUCCESS = 'success'
    WARNING = 'warning'
    ERROR = 'error'
