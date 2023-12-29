from typing import List
from fastapi import APIRouter, Depends, Request, HTTPException, status, Query
from ..core.security import (
    create_access_token,
    check_jwt_auth,
)
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q
from ..db.models import Users, Routes, DataDict
from ..schemas import ResultResponse, system
from ..utils.log_util import log
from ..services import SystemService
from ..core.security import (
    check_jwt_auth,
    get_current_user as current_user,
)

router = APIRouter()





@router.get(
    "/treeselect",
    summary="查询菜单树结构",
)
async def get_treeselect():
    """查询菜单树结构"""
    route_list = await Routes.filter(parent_id__isnull=True).prefetch_related(
            "children__meta", "meta"
        )
    log.debug(route_list)
    return 1