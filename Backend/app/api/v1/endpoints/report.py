# 位于: Backend/app/api/v1/endpoints/report.py
"""
(P1 关键) Day 7 - F5.1, F5.3, F5.2 API
(基于 FRD v1.11 和 Tech Specs v1.5)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid
import logging
import json

from app.core.database import get_db
from app.models import User, Report
from app.schemas import ( # (Day 7) 导入新的 schemas
    ReportGenerateResponse, ReportStatusResponse, ReportResponse
)
# (P1 Day 7) 导入 Celery 任务
from app.tasks.process_report import generate_report
# (P1 Day 7) 导入 Day 2 的 "妥协版" 认证
from .user import get_current_user 

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/generate", response_model=ReportGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def trigger_report_generation(
    current_user: User = Depends(get_current_user), # (P1 妥协)
    db: Session = Depends(get_db)
):
    """
    (P1) F5.1 触发报告生成 (Tech Specs v1.5)
    (由前端在 F3.2.2 聊完 5 条后自动调用)
    """
    logger.info(f"F5.1 (API): 用户 {current_user.id} 正在触发报告生成...")
    
    # (P1) 检查是否已在生成
    existing_report = db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).first()
    if existing_report is not None and existing_report.status == 'GENERATING':# type: ignore
        logger.warning(f"F5.1 (API): 用户 {current_user.id} 试图重复触发报告。")
        return {
            "report_id": existing_report.id,
            "status": "GENERATING"
        }
        
    # 1. (DB) 存入数据库 (DB v1.3)
    new_report = Report(
        user_id=current_user.id,
        status='GENERATING' # (F5.3 关键)
    )
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    # 2. (Async) (P1 关键) 推送异步任务到 Redis (Celery)
    try:
        generate_report.delay(report_id=str(new_report.id), user_id=str(current_user.id))
        logger.info(f"F5.1 (API): 任务 generate_report 已推送到 Redis。")
    except Exception as e:
        logger.error(f"F5.1 (API): Celery 任务推送失败! {e}", exc_info=True)
        pass # (P1) 失败也不应 500

    return {
        "report_id": new_report.id,
        "status": "GENERATING"
    }


@router.get("/status", response_model=ReportStatusResponse)
async def get_report_status(
    current_user: User = Depends(get_current_user), # (P1 妥协)
    db: Session = Depends(get_db)
):
    """
    (P1) F5.3 等待页轮询 (Tech Specs v1.5)
    """
    logger.debug(f"F5.3 (Poll): 用户 {current_user.id} 正在检查报告状态...")
    report = db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="REPORT_NOT_FOUND")
        
    return {"status": report.status} # 'GENERATING' or 'READY'


@router.get("/latest", response_model=ReportResponse)
async def get_latest_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    (P1) F5.2 获取报告
    (v1.16 - 最终修复：修复 Schema 验证，将 list 转换为 str)
    """
    logger.debug(f"F5.2 (API): 用户 {current_user.id} 正在加载最新报告...")
    report = db.query(Report).filter(
        Report.user_id == current_user.id,
        Report.status == 'READY'
    ).order_by(Report.created_at.desc()).first()
    
    if report is None:
        raise HTTPException(status_code=404, detail="REPORT_NOT_READY")

    # 最终要符合 Pydantic (WOOPContent) 模型的对象
    report_content_json = {} 
    
    try:
        # (P1 v1.14 修复) 
        # 应对 Worker 存储 '```json\n{...}\n```' 的问题
        content_str = str(report.content)
        
        # 1. 查找 JSON 的开始 '{' 和结束 '}'
        start_index = content_str.find('{')
        end_index = content_str.rfind('}')
        
        db_json_content = {} # 从数据库解析出的原始 JSON
        
        # 2. 如果找到了
        if start_index != -1 and end_index != -1 and end_index > start_index:
            json_substring = content_str[start_index : end_index + 1]
            # 3. 解析提取出的子字符串
            db_json_content = json.loads(json_substring)
        else:
            # 4. 如果连 {} 都找不到，就主动抛出异常，进入下面的 fallback
            logger.error(f"F5.2 (API): 无法在 Report.content 中找到有效的 {{}} 结构! ID: {report.id}")
            raise ValueError("在数据库内容中找不到有效的 JSON {} 结构")
        
        # (P1 v1.16 修复) 
        # 键/类型映射：将 DB 结构 映射到 Pydantic (WOOPContent) 结构
        # DB: {'wish': str, 'outcome': str, 'obstacle': list, 'plan': list}
        # Pydantic: {'wish': str, 'outcome': str, 'obstacle': str, 'plan': str}
        
        if "wish" not in db_json_content or "outcome" not in db_json_content:
             logger.error(f"DB JSON 缺少 'wish' 或 'outcome' 键! ID: {report.id}")
             raise ValueError("DB JSON 结构不完整")

        # (v1.16 关键) 将 DB 的 list 转换为 Pydantic 期望的 str
        # 我们使用 json.dumps() 来确保它是一个格式正确的字符串
        report_content_json = {
            "wish": db_json_content.get("wish", "N/A"),
            "outcome": db_json_content.get("outcome", "N/A"),
            "obstacle": json.dumps(db_json_content.get("obstacle", []), ensure_ascii=False),
            "plan": json.dumps(db_json_content.get("plan", []), ensure_ascii=False)
        }

    except Exception as e:
        # (P1 v1.16 修复 Fallback) 
        # "备用方案" (Fallback) JSON，必须 100% 匹配 WOOPContent
        logger.error(f"F5.2 (API): 转换报告内容失败! ID: {report.id}. Error: {e}", exc_info=True)
        report_content_json = {
            "wish": "报告生成失败。请联系管理员。",
            "outcome": "N/A",
            "obstacle": "[]", # 必须是字符串
            "plan": "[]"     # 必须是字符串
        }

    return {
        "report_id": report.id,
        "status": report.status,
        "content": report_content_json, # (P1 v1.16) 100% 匹配 WOOPContent
        "created_at": report.created_at
    }