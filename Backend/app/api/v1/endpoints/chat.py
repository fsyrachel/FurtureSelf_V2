# 位于: Backend/app/api/v1/endpoints/chat.py
"""
(P1 关键) Day 5/6 - F3.2.2 (5条限制), F3.2.3 (历史)
(基于 FRD v1.11 和 Tech Specs v1.5)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func
import uuid
import logging
from typing import List

from app.core.database import get_db
from app.models import User, Letter, LetterReply, FutureProfile, ChatMessage, CurrentProfile
from app.schemas import ( # (Day 5/6) 导入新的 schemas
    ChatHistoryResponse, ChatMessageRequest, ChatMessageResponse
)
# (P1 Day 5) 导入 Day 5 的 AI 链
from app.services.ai_services import generate_chat_reply_service
# (P1 Day 5) 导入 Day 2 的 "妥协版" 认证
from .user import get_current_user 

from app.core.config import settings  # 添加 settings 的导入

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{future_profile_id}/history", response_model=List[ChatHistoryResponse])
async def get_chat_history(
    future_profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user), # (P1 妥协)
    db: Session = Depends(get_db)
):
    """
    (P1) F3.2.3 获取聊天历史 (Tech Specs v1.5)
    """
    logger.debug(f"F3.2.3 (API): 用户 {current_user.id} 正在加载人设 {future_profile_id} 的聊天历史...")
    
    history_db = db.query(ChatMessage) \
                   .filter(
                       ChatMessage.user_id == current_user.id,
                       ChatMessage.future_profile_id == future_profile_id
                   ) \
                   .order_by(ChatMessage.created_at.asc()) \
                   .all()
    
    # (P1) 格式化 (我们不希望把 DB 模型 schema 暴露给前端)
    return [
        ChatHistoryResponse(
            message_id=msg.id, # type: ignore
            sender=msg.sender, # type: ignore
            content=msg.content, # type: ignore
            created_at=msg.created_at # type: ignore
        ) for msg in history_db
    ]

@router.post("/{future_profile_id}/send", response_model=ChatMessageResponse)
async def send_chat_message(
    request: ChatMessageRequest,
    future_profile_id: uuid.UUID,
    current_user: User = Depends(get_current_user), # (P1 妥协)
    db: Session = Depends(get_db)
):
    """
    (P1) F3.2.2 聊天响应 (Tech Specs v1.5 - 5条限制)
    """
    logger.info(f"F3.2.2 (API): 用户 {current_user.id} 正在向 {future_profile_id} 发送消息...")
    
    # (P1 v1.11 核心) 1. 5条消息守卫 (F4.4)
    user_message_count = db.query(sql_func.count(ChatMessage.id)) \
                           .filter(
                               ChatMessage.user_id == current_user.id,
                               ChatMessage.future_profile_id == future_profile_id,
                               ChatMessage.sender == 'USER'
                           ) \
                           .scalar()
                           
    logger.debug(f"F3.2.2 (API): 用户已发送 {user_message_count} 条消息。")

    if user_message_count >= settings.MAX_CHAT_MESSAGES: # (P1) 5
        logger.warning(f"F3.2.2 (API): 用户 {current_user.id} 已达 10 条消息上限。")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="MESSAGE_LIMIT_EXCEEDED"
        )
        
    # (P1 v1.11 核心) 2. 状态更新 (F4.4)
    if user_message_count == 0:
        logger.info(f"F3.2.2 (API): 这是第一条消息。更新 chat_status='COMPLETED'。")
        # (P1) 找到这封回信 (它必须存在)
        reply = db.query(LetterReply).filter(LetterReply.future_profile_id == future_profile_id).first()
        if reply:
            reply.chat_status = 'COMPLETED' # type: ignore
            db.add(reply)
        else:
            # (P1) 容错
            logger.error(f"F3.2.2 (API): 找不到 {future_profile_id} 对应的 letter_reply 来更新状态!")

    # 3. 存储用户消息
    user_msg = ChatMessage(
        id=uuid.uuid4(),
        future_profile_id=future_profile_id,
        user_id=current_user.id,
        sender='USER',
        content=request.content
    )
    db.add(user_msg)
    
    # 4. (P1 关键) 同步调用 AI 链 (F4.4)
    # (我们需要加载 F4.4 所需的所有数据)
    # ai_content = f"TODO (Day 6): AI 正在处理您的第 {user_message_count + 1} 条消息。"
    current_profile = db.query(CurrentProfile).filter(CurrentProfile.user_id == current_user.id).first()
    future_profile = db.query(FutureProfile).filter(FutureProfile.id == future_profile_id).first()
    chat_history_db = db.query(ChatMessage) \
                        .filter(
                            ChatMessage.user_id == current_user.id,
                            ChatMessage.future_profile_id == future_profile_id
                        ) \
                        .order_by(ChatMessage.created_at.asc()) \
                        .all()

    if current_profile is None or future_profile is None:
      raise HTTPException(status_code=404, detail="Profile data incomplete.")

        
    ai_content = await generate_chat_reply_service(
        db=db,
        current_profile=current_profile,
        future_profile=future_profile,
        chat_history_db=chat_history_db,
        user_query=request.content
    )
    
    # 5. 存储 AI 回复
    ai_msg = ChatMessage(
        id=uuid.uuid4(),
        future_profile_id=future_profile_id,
        user_id=current_user.id,
        sender='AGENT', # (P1) AI
        content=ai_content
    )
    db.add(ai_msg)
    
    # 6. 提交事务
    db.commit()
    db.refresh(ai_msg)
    
    # 7. 返回 AI 回复 (Tech Specs v1.5)
    return ChatMessageResponse(
        message_id=ai_msg.id, # type: ignore
        sender=ai_msg.sender, # type: ignore
        content=ai_msg.content, # type: ignore
        created_at=ai_msg.created_at # type: ignore
    )