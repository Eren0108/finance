from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Category:
    id: Optional[int]
    name: str
    type: str
    color: str

    def to_dict(self):
        return asdict(self)


@dataclass
class Transaction:
    id: Optional[int]
    date: str
    description: str
    amount: float
    type: str
    category_id: int
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    source: str = "manual"
    statement_id: Optional[int] = None
    created_at: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Budget:
    id: Optional[int]
    category_id: int
    month: str
    limit_amount: float
    category_name: Optional[str] = None
    category_color: Optional[str] = None
    spent_amount: float = 0.0

    def to_dict(self):
        return asdict(self)


@dataclass
class Statement:
    id: Optional[int]
    filename: str
    uploaded_at: Optional[str] = None
    rows_imported: int = 0

    def to_dict(self):
        return asdict(self)
