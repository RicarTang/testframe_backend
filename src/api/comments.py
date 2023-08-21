from fastapi import APIRouter, Depends, Request,HTTPException
from src.db.models import Comments, Users
from ..schemas import schemas
from ..utils.log_util import log
from ..core.security import check_jwt_auth

router = APIRouter()


@router.post("/create", summary="发表评论", response_model=schemas.ResultResponse[schemas.CommentTo])
async def create_comment(
    comment: schemas.CommentIn,
    current_user: schemas.UserPy = Depends(check_jwt_auth),
):
    """创建comment"""
    # com = await Comments.create(**comment.dict(exclude_unset=True))
    com = await Comments.create(user_id=current_user.id, comment=comment.comment)
    # log.debug(f"com返回参数：{await com.first().values()}")
    return schemas.ResultResponse[schemas.CommentTo](result=com)


@router.get(
    "/comments/{user_id}", summary="获取用户评论", response_model=schemas.ResultResponse[schemas.CommentsTo]
)
async def get_user_comment(
    user_id: int,
):
    """获取某个user的comments"""
    try:
        user = await Users.filter(id=user_id).first().prefetch_related("comments")
        coms = await user.comments.all()
        log.debug(f"用户{user}的所有评论：{coms}")
    except AttributeError:
        raise HTTPException(detail="User is not exist!")
    return schemas.ResultResponse[schemas.CommentsTo](result=coms)


@router.get("/me", summary="获取我的评论", response_model=schemas.ResultResponse[schemas.CommentsTo])
async def get_comments_me(current_user: schemas.UserPy = Depends(check_jwt_auth)):
    """当前用户的所有评论"""
    user = (
        await Users.filter(username=current_user.username)
        .first()
        .prefetch_related("comments")
    )
    comments = await user.comments.all()
    log.debug(f"comments:{comments}")
    return schemas.ResultResponse[schemas.CommentsTo](result=comments)
