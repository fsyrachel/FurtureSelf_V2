# 位于: Backend/app/api/v1/endpoints/letter.py
"""
(P1 关键) Day 3/4 - F3.1.2, F6.6, F6.5, F3.1.3 API
(v1.2 - P1 冲刺（Sprint）asyncio 修复)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid
import logging
from typing import List, Annotated

from app.core.database import get_db
from app.models import User, Letter, LetterReply, FutureProfile
from app.schemas import (
    LetterSubmitRequest, LetterSubmitResponse,
    LetterStatusResponse, InboxResponse, ReplyItem,
    LetterReplyResponse
)
from app.tasks.process_letter import process_letter
# (P1 v1.11 修复) 导入 *async* RAG 写入服务
from app.services.vector_store import add_letter_to_rag_async
from .user import get_current_user 

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/submit", response_model=LetterSubmitResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_letter(
    request: LetterSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    (P1) F3.1.2 信件提交 (v1.11 asyncio 修复)
    """
    logger.info(f"F3.1.2 (API): 用户 {current_user.id} 正在提交信件...")
    
    existing_letter = db.query(Letter).filter(Letter.user_id == current_user.id).first()
    
    if existing_letter is not None:
        logger.warning(f"F3.1.2 (API): 用户 {current_user.id} 试图提交第 2 封信。")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="LETTER_ALREADY_SUBMITTED"
        )
    
    # (P1 v1.11 修复) 事务 (Transaction)
    try:
        # 1. (DB) 存入数据库
        new_letter = Letter(
            id=uuid.uuid4(),
            user_id=current_user.id,
            content=request.content,
            status='PENDING'
        )
        db.add(new_letter)
        db.flush() # (P1 v1.11) 必须 flush 
        
        # 2. (RAG Write) (v1.11 修复) 必须 `await`
        await add_letter_to_rag_async(db, new_letter)

        db.commit()
        db.refresh(new_letter)
    
    except Exception as e:
        logger.error(f"F3.1.2 (API) 失败 (RAG 或 DB)! 事务回滚。 {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"提交信件失败: {e}"
        )
    
    # 3. (Async) (P1 关键) 推送异步任务到 Redis (Celery)
    try:
        process_letter.delay(letter_id=str(new_letter.id), user_id=str(current_user.id))
        logger.info(f"F3.1.2 (API): 任务 process_letter 已推送到 Redis。")
    except Exception as e:
        logger.error(f"F3.1.2 (API): Celery 任务推送失败! {e}", exc_info=True)
        pass # (P1 妥协: 提交成功，但 Worker 不会运行)

    return {
        "letter_id": new_letter.id,
        "status": "SUBMITTED"
    }


@router.get("/status", response_model=LetterStatusResponse)
async def get_letter_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """(P1) F6.6 等待页轮询"""
    letter = db.query(Letter).filter(Letter.user_id == current_user.id).order_by(Letter.created_at.desc()).first()
    if letter is None:
        raise HTTPException(status_code=404, detail="LETTER_NOT_FOUND")
    return {"status": letter.status}


@router.get("/inbox/latest", response_model=InboxResponse)
async def get_inbox_latest(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    调试版 /inbox/latest
    1. 确认路由是否被调用
    2. 打印 current_user
    3. 打印最新信件信息
    """
    print("Entered /inbox/latest")  # 路由调试
    print(f"current_user: {current_user}")

    # 查询最新信件
    letter = (
        db.query(Letter)
        .filter(Letter.user_id == current_user.id)
        .order_by(Letter.created_at.desc())
        .first()
    )

    if not letter:
        print(f"No letter found for user_id={current_user.id}")
        return {"debug": "No letter found", "user_id": str(current_user.id)}

    print(f"Latest letter: id={letter.id}, status={letter.status}, created_at={letter.created_at}")

    # 状态检查（调试阶段不抛异常）
    if letter.status.strip().upper() != "REPLIES_READY":
        print(f"Letter status not ready: {letter.status}")

    # 查询信件回复
    replies_db = (
        db.query(LetterReply, FutureProfile.profile_name)
        .join(FutureProfile, LetterReply.future_profile_id == FutureProfile.id)
        .filter(LetterReply.letter_id == letter.id)
        .all()
    )

    replies_response: List[ReplyItem] = [
        ReplyItem(
            reply_id=reply.id,
            future_profile_id=reply.future_profile_id,
            from_profile_name=profile_name,
            chat_status=reply.chat_status
        )
        for reply, profile_name in replies_db
    ]

    return {
        "letter_id": letter.id,
        "letter_content_snippet": (letter.content[:100] + "...") if len(letter.content) > 100 else letter.content,
        "replies": replies_response
    }



@router.get("/reply/{reply_id}", response_model=LetterReplyResponse)
async def get_letter_reply(
    reply_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """(P1) F3.1.3 读信页"""
    reply_data = db.query(LetterReply, FutureProfile.profile_name, Letter.user_id) \
                   .join(Letter, LetterReply.letter_id == Letter.id) \
                   .join(FutureProfile, LetterReply.future_profile_id == FutureProfile.id) \
                   .filter(LetterReply.id == reply_id) \
                   .first()

    if reply_data is None:
        raise HTTPException(status_code=404, detail="REPLY_NOT_FOUND")
    
    (reply, profile_name, letter_user_id) = reply_data
    
    if letter_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="FORBIDDEN")

    return {
        "reply_id": reply.id,
        "future_profile_id": reply.future_profile_id,
        "from_profile_name": profile_name,
        "content": reply.content,
        "chat_status": reply.chat_status
    }