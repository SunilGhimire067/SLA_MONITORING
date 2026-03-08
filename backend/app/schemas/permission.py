from typing import List, Optional
from pydantic import BaseModel


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: List[PermissionResponse] = []


class RolePermissionsUpdate(BaseModel):
    permission_ids: List[int]
