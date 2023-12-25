from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response
from passlib.hash import md5_crypt
from tortoise.transactions import in_transaction
from tortoise.contrib.fastapi import HTTPNotFoundError
from tortoise.exceptions import DoesNotExist
from ..core.security import (
    check_jwt_auth,
    get_current_user as current_user,
)
from ..core.authentication import Authority
from ...src.db.models import Users, Role
from ..schemas import ResultResponse, user_schema
from ..utils.log_util import log
from ..utils.exceptions.user import (
    UserNotExistException,
    RoleNotExistException,
)


router = APIRouter()


@router.get(
    "/list",
    summary="获取所有用户",
    response_model=ResultResponse[user_schema.UsersOut],
    dependencies=[Depends(check_jwt_auth)],
)
async def get_users(
    username: Optional[str] = Query(default=None, description="用户名", alias="userName"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取用户列表"""
    # 查询用户名
    if username:
        result = (
            await Users.filter(username__contains=username)
            .all()
            .offset(limit * (page - 1))
            .limit(limit)
        )
        total = await Users.filter(username__contains=username).all().count()
    # 默认查询
    else:
        result = await Users.all().offset(limit * (page - 1)).limit(limit)
        # total
        total = await Users.all().count()
    return ResultResponse[user_schema.UsersOut](
        result=user_schema.UsersOut(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/role",
    summary="获取当前用户角色",
    response_model=ResultResponse[List[user_schema.RoleTo]],
)
async def query_user_role(
    current_user: Users = Depends(current_user),
):
    """查询当前用户角色"""
    user = await Users.filter(id=current_user.id).prefetch_related("roles").first()
    return ResultResponse[List[user_schema.RoleTo]](result=user.roles)


@router.get(
    "/me",
    summary="获取当前用户信息",
    response_model=ResultResponse[user_schema.UserPy],
)
async def get_current_user(current_user: Users = Depends(current_user)):
    """获取当前用户"""
    return ResultResponse[user_schema.UserPy](result=current_user)


@router.post(
    "/create",
    summary="创建用户",
    response_model=ResultResponse[user_schema.UserOut],
    dependencies=[Depends(check_jwt_auth), Depends(Authority("user","add"))],
)
async def create_user(user: user_schema.UserIn):
    """创建用户."""
    user.password = md5_crypt.hash(user.password)
    user_obj = await Users(**user.dict(exclude_unset=True))
    # 添加用户角色
    role = await Role.filter(name="member").first()
    if not role:
        raise RoleNotExistException
    await user_obj.save()
    await user_obj.roles.add(role)
    log.info(f"成功创建用户：{user.dict(exclude_unset=True)}")
    return ResultResponse[user_schema.UserOut](result=user_obj)


@router.get(
    "/query",
    summary="查询用户",
    response_model=ResultResponse[user_schema.UsersOut],
    dependencies=[Depends(check_jwt_auth)],
)
async def query_user(
    username: Optional[str] = Query(default=None, description="用户名"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """查询用户"""
    result = await Users.filter(username__contains=username).all()
    total = len(result)
    return ResultResponse[user_schema.UsersOut](
        result=user_schema.UsersOut(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/{user_id}",
    response_model=ResultResponse[user_schema.UserOut],
    summary="根据id查询用户",
    dependencies=[Depends(check_jwt_auth)],
)
async def get_user(user_id: int):
    """根据id查询用户."""
    try:
        user = await Users.get(id=user_id)
    except DoesNotExist:
        raise UserNotExistException
    return ResultResponse[user_schema.UserOut](result=user)


@router.put(
    "/{user_id}",
    response_model=ResultResponse[user_schema.UserOut],
    summary="更新用户",
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(check_jwt_auth), Depends(Authority("user","update"))],
)
async def update_user(user_id: int, user: user_schema.UserIn):
    """更新用户信息."""
    # 使用 atomic 事务
    async with in_transaction():
        # 查询用户是否存在
        existing_user = await Users.get_or_none(id=user_id)
        if not existing_user:
            raise UserNotExistException
        # 如果提供了密码，进行密码哈希
        if user.password:
            user.password = md5_crypt.hash(user.password)

        # 使用 filter 更新指定字段
        result = await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
        log.debug(f"update 更新{result}条数据")

        # 获取更新后的用户信息
        updated_user = await Users.get(id=user_id)
        return ResultResponse[user_schema.UserOut](result=updated_user)


@router.delete(
    "/batchDelete",
    summary="批量删除用户",
    response_model=ResultResponse[str],
    dependencies=[Depends(check_jwt_auth), Depends(Authority("user","delete"))],
)
async def batch_delete_user(body: user_schema.BatchDelete):
    """批量删除用户

    Args:
        body (user_schema.BatchDelete): _description_

    Returns:
        _type_: _description_
    """
    async with in_transaction():  # 事务
        # 使用 filter 方法过滤出要删除的记录，然后delete删除
        users_to_delete = await Users.filter(id__in=body.users_id).delete()
    return ResultResponse[str](message=f"successful deleted {users_to_delete} users!")


@router.delete(
    "/{user_id}",
    response_model=ResultResponse[str],
    summary="删除用户",
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(check_jwt_auth), Depends(Authority("user","delete"))],
)
async def delete_user(user_id: int, response: Response):
    """删除用户."""
    if not await Users.filter(id=user_id).exists():
        raise UserNotExistException
    deleted_count = await Users.filter(id=user_id).delete()
    return ResultResponse[str](message="successful deleted user!")
