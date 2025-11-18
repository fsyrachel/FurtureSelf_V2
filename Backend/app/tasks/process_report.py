import logging
import asyncio
import uuid
import json
from sqlalchemy.orm import Session

from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models import Report, Letter, ChatMessage, CurrentProfile
from app.services.ai_services import report_chain # (P1) 导入 Day 7 AI 链

logger = logging.getLogger(__name__)

# 重试配置
MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 60  # 重试延迟（秒）

def async_to_sync(awaitable):
    return asyncio.run(awaitable)

@celery_app.task(
    name="generate_report",
    bind=True,  # 绑定任务实例，允许访问 self
    max_retries=MAX_RETRIES,  # 最大重试次数
    default_retry_delay=RETRY_DELAY,  # 默认重试延迟
)
<<<<<<< HEAD
def generate_report(self, report_id: str, user_id: str, letter_id: str = None, future_profile_id: str = None, **kwargs):
=======
def generate_report(self, report_id: str, user_id: str, letter_id: str = None, future_profile_id: str = None):
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
    """
    (P1) F4.5 异步总结任务 (Tech Specs v1.5, 4.2节)
    支持可选参数：
    - letter_id: 指定信件ID（可选，默认使用最新）
    - future_profile_id: 指定未来人设ID（可选，默认使用所有聊天记录）
    """
    logger.info(f"F4.5 (Worker): 收到任务! ReportID: {report_id}, UserID: {user_id}")
<<<<<<< HEAD
    if kwargs:
        logger.debug(f"F4.5 (Worker): 收到额外的 kwargs: {kwargs}")
=======
>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
    if letter_id:
        logger.info(f"F4.5 (Worker): 指定信件ID: {letter_id}")
    if future_profile_id:
        logger.info(f"F4.5 (Worker): 指定未来人设ID: {future_profile_id}")
    
    db = SessionLocal()
    
    try:
        # 1. (DB) 获取数据
        report = db.query(Report).filter(Report.id == uuid.UUID(report_id)).first()
        current_profile = db.query(CurrentProfile).filter(CurrentProfile.user_id == uuid.UUID(user_id)).first()
        
        # 获取信件：如果指定了 letter_id，使用指定的；否则使用最新的
        if letter_id:
            letter = db.query(Letter).filter(Letter.id == uuid.UUID(letter_id)).first()
            if not letter:
                logger.error(f"F4.5 (Worker): 指定的信件不存在: {letter_id}")
                raise ValueError(f"Letter with ID {letter_id} not found")
        else:
            letter = db.query(Letter).filter(Letter.user_id == uuid.UUID(user_id)).order_by(Letter.created_at.desc()).first()
        
        # 获取聊天记录：如果指定了 future_profile_id，只获取该人设的；否则获取所有
        if future_profile_id:
            chat_history_db = db.query(ChatMessage).filter(
                ChatMessage.user_id == uuid.UUID(user_id),
                ChatMessage.future_profile_id == uuid.UUID(future_profile_id)
            ).order_by(ChatMessage.created_at.asc()).all()
            if not chat_history_db:
                logger.error(f"F4.5 (Worker): 指定的未来人设没有聊天记录: {future_profile_id}")
                raise ValueError(f"No chat history found for future_profile_id {future_profile_id}")
        else:
            chat_history_db = db.query(ChatMessage).filter(
                ChatMessage.user_id == uuid.UUID(user_id)
            ).order_by(ChatMessage.created_at.asc()).all()
        
        if not all([report, letter, current_profile, chat_history_db]):
            logger.error(f"F4.5 (Worker): 数据不完整。")
            raise ValueError("Data incomplete for report generation.")

        # 2. (P1) 格式化聊天记录
        chat_history_full = "\n".join(
            [f"{msg.sender}: {msg.content}" for msg in chat_history_db]
        )
        
        profile_data_light = {
            "demo_data": current_profile.demo_data, # type: ignore
            "vals_data": current_profile.vals_data,# type: ignore
            "bfi_data": current_profile.bfi_data# type: ignore
        }

        # 4. (AI) 准备 Prompt 输入
        prompt_input = {
            "current_profile_data": json.dumps(profile_data_light, indent=2),
            "user_letter_content": letter.content,# type: ignore
            "full_chat_history": chat_history_full
        }
        
        # 5. (AI) 调用 F4.5 (总结) AI 链
        ai_response_raw = async_to_sync(
            report_chain.ainvoke(prompt_input)
        )
        
        # 6. (P1) 解析和验证 AI 响应
        try:
            # 尝试提取 JSON（可能包含 markdown 代码块）
            content_str = str(ai_response_raw)
            
            # 查找 JSON 的开始 '{' 和结束 '}'
            start_index = content_str.find('{')
            end_index = content_str.rfind('}')
            
            if start_index == -1 or end_index == -1 or end_index <= start_index:
                raise ValueError("无法在 AI 响应中找到有效的 JSON 结构")
            
            # 提取并解析 JSON
            json_substring = content_str[start_index:end_index + 1]
            ai_response_json = json.loads(json_substring)
            
            # 验证必需字段
            required_fields = ['wish', 'outcome', 'obstacle', 'plan']
            missing_fields = [field for field in required_fields if field not in ai_response_json]
            if missing_fields:
                raise ValueError(f"AI 响应缺少必需字段: {', '.join(missing_fields)}")
            
            # 验证字段类型（都必须是字符串）
            for field in required_fields:
                if not isinstance(ai_response_json[field], str):
                    raise ValueError(f"字段 '{field}' 必须是字符串类型，实际类型: {type(ai_response_json[field]).__name__}")
            
            logger.debug(f"F4.5 (Worker): AI 响应验证通过。")
            
        except (json.JSONDecodeError, ValueError) as e:
            # JSON 解析或验证失败
            logger.error(f"F4.5 (Worker): AI 响应解析/验证失败! ReportID: {report_id}. 错误: {e}")
            logger.debug(f"F4.5 (Worker): 原始响应: {ai_response_raw[:500]}...")  # 记录前500字符用于调试
            raise ValueError(f"AI 响应格式无效: {e}")
        
        # 7. (DB) 更新报告状态为 "READY"
        # 保存原始响应字符串（包含可能的 markdown 标记），前端会再次解析
        report.content = ai_response_raw# type: ignore
        report.status = 'READY'# type: ignore
        db.add(report)
        db.commit()
        
        logger.info(f"F4.5 (Worker): 任务成功完成! ReportID: {report_id} 状态已更新为 READY。")
        
    except ValueError as e:
        # 数据错误（如数据不完整）- 不应该重试，但也要标记为 FAILED 让前端可以重试
        logger.error(f"F4.5 (Worker): 数据错误，不重试! ReportID: {report_id}. 错误: {e}", exc_info=True)
        db.rollback()
        # 更新报告状态为 FAILED，让前端知道可以手动重试
        try:
            report = db.query(Report).filter(Report.id == uuid.UUID(report_id)).first()
            if report:
                report.status = 'FAILED'# type: ignore
                db.commit()
                logger.info(f"F4.5 (Worker): 报告 {report_id} 状态已更新为 FAILED（数据错误）")
        except Exception as update_error:
            logger.error(f"F4.5 (Worker): 更新报告状态失败: {update_error}", exc_info=True)
        raise  # 不重试，直接抛出异常
        
    except Exception as e:
        # 其他错误（如 AI API 超时、网络错误等）- 可以重试
        logger.error(f"F4.5 (Worker): 任务失败! ReportID: {report_id}. 错误: {e}", exc_info=True)
        db.rollback()
        
        # 检查是否还有重试机会
        if self.request.retries < MAX_RETRIES:
            logger.info(f"F4.5 (Worker): 准备重试 ({self.request.retries + 1}/{MAX_RETRIES})...")
            # 指数退避：第1次重试等60秒，第2次等120秒，第3次等240秒
            retry_delay = RETRY_DELAY * (2 ** self.request.retries)
            raise self.retry(exc=e, countdown=retry_delay)
        else:
            # 达到最大重试次数，任务最终失败
            logger.error(f"F4.5 (Worker): 达到最大重试次数 ({MAX_RETRIES})，任务最终失败!")
            # 更新报告状态为 FAILED，让前端知道可以手动重试
            try:
                report = db.query(Report).filter(Report.id == uuid.UUID(report_id)).first()
                if report:
                    report.status = 'FAILED'# type: ignore
                    db.commit()
                    logger.info(f"F4.5 (Worker): 报告 {report_id} 状态已更新为 FAILED")
            except Exception as update_error:
                logger.error(f"F4.5 (Worker): 更新报告状态失败: {update_error}", exc_info=True)
            raise  # 最终失败，抛出异常
    finally:
        db.close() # (P1 关键) 确保会话被关闭