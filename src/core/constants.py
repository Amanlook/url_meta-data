from enum import Enum
from typing import Any


class BaseEnum(str, Enum):
    @classmethod
    def list(cls) -> list[Any]:
        return list(map(lambda item: item.value, cls))


class Environment(BaseEnum):
    """
    An enumeration representing the various environments in which the application can run.
    Attributes:
        LOCAL: Represents a local development environment on a developer's machine.
        STAGING: Represents a User Acceptance Testing environment for final testing by users.
        PRODUCTION: Represents the final environment where the application is available to end users.
    """

    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "prod"
