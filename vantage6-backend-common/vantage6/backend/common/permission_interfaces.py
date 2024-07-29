from __future__ import annotations

from enum import Enum as Enumerate
from typing import Any

from sqlalchemy.orm.exc import NoResultFound

from vantage6.backend.common.base import DatabaseSessionManager


class OperationInterface(str, Enumerate):
    """Enumerator of all available operations"""

    pass


class ScopeInterface(str, Enumerate):
    """Enumerator of all available scopes"""

    pass


class RuleInterface:
    name: Any
    operation: Any
    description: Any

    @classmethod
    def get_by_(cls, *args, **kwargs):
        pass

    def __repr__(self) -> str:
        """
        String representation of the rule.

        Returns
        -------
        str
            String representation of the rule
        """
        pass


class RoleInterface:

    @classmethod
    def get_by_name(cls, name: str):
        session = DatabaseSessionManager.get_session()
        try:
            result = session.query(cls).filter_by(name=name).first()
            session.commit()
            return result
        except NoResultFound:
            return None

    def __repr__(self) -> str:
        pass
