# university/repositories.py
from __future__ import annotations
from typing import Generic, List, TypeVar, Protocol, Callable, Optional

T = TypeVar("T")

class Repository(Protocol, Generic[T]):
    """Storage interface so we can swap implementations (in-memory, JSON, DB)."""
    def add(self, item: T) -> T: ...
    def list_all(self) -> List[T]: ...
    def find(self, predicate: Callable[[T], bool]) -> List[T]: ...


class InMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._items: List[T] = []

    def add(self, item: T) -> T:
        self._items.append(item)
        return item

    def list_all(self) -> List[T]:
        return list(self._items)

    def find(self, predicate):
        return [x for x in self._items if predicate(x)]
