from dataclasses import dataclass, field

@dataclass
class Point:
    diem_id: str | None
    noi_dung: str

@dataclass
class Clause:
    khoan_id: int | None   
    noi_dung: str
    points: list[Point] = field(default_factory=list)         

@dataclass
class Article:
    dieu_id: int | None
    tieu_de: str 
    noi_dung: str                       
    clauses: list[Clause] = field(default_factory=list)  