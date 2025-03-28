from typing import List

from fastapi import Depends, HTTPException, Request, status

from src.conf import messages
from src.database.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, request: Request, user: User = Depends(auth_service.get_current_user)
    ):
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=messages.FORBIDDEN,
            )


admin_access = RoleAccess([Role.admin])
admin_moderator_access = RoleAccess([Role.admin, Role.moderator])
all_roles_access = RoleAccess([Role.admin, Role.moderator, Role.user])
