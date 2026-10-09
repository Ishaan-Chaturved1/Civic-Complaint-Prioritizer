from typing import Optional
from pydantic import BaseModel


class DepartmentBase(BaseModel):
    name: str
    category: str
    sla_hours: int = 48
    officer_id: Optional[int] = None


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sla_hours: Optional[int] = None
    officer_id: Optional[int] = None


class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True
