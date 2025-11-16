"""
报告生成端到端集成测试
需要真实的 Celery Worker 运行
"""
import uuid
import pytest

from app.models import (
    Report, 
    CurrentProfile, 
    FutureProfile, 
    Letter, 
    LetterReply, 
    ChatMessage
)
from tests.integration.conftest import wait_for_task_completion


@pytest.fixture()
def setup_complete_chat_history(integration_db_session, integration_test_user):
    """
    准备完整的聊天历史数据
    Worker需要这些数据来生成报告
    """
    # 创建当前档案
    current_profile = CurrentProfile(
        id=uuid.uuid4(),
        user_id=integration_test_user.id,
        demo_data={"age": 26, "name": "测试用户"},
        vals_data={"value1": 4.0},
        bfi_data={"trait1": 3.5},
    )
    
    # 创建未来档案
    future_profile = FutureProfile(
        id=uuid.uuid4(),
        user_id=integration_test_user.id,
        profile_name="集成测试未来人设",
        profile_description="用于报告生成集成测试的未来人设描述，需要足够详细以便生成有意义的报告。",
    )
    
    # 创建信件和回信
    letter = Letter(
        id=uuid.uuid4(),
        user_id=integration_test_user.id,
        content="集成测试信件内容",
        status="REPLIES_READY",
    )
    
    reply = LetterReply(
        id=uuid.uuid4(),
        letter_id=letter.id,
        future_profile_id=future_profile.id,
        content="集成测试回信内容",
        chat_status="COMPLETED",
    )
    
    # 创建5条聊天记录
    chat_messages = []
    for i in range(5):
        # 用户消息
        user_msg = ChatMessage(
            id=uuid.uuid4(),
            user_id=integration_test_user.id,
            future_profile_id=future_profile.id,
            sender="USER",
            content=f"这是第 {i+1} 条用户消息，用于集成测试报告生成。",
        )
        chat_messages.append(user_msg)
        
        # AI回复
        agent_msg = ChatMessage(
            id=uuid.uuid4(),
            user_id=integration_test_user.id,
            future_profile_id=future_profile.id,
            sender="AGENT",
            content=f"这是第 {i+1} 条AI回复，用于集成测试报告生成。",
        )
        chat_messages.append(agent_msg)
    
    integration_db_session.add_all([
        current_profile, 
        future_profile, 
        letter, 
        reply
    ] + chat_messages)
    integration_db_session.commit()
    
    return future_profile


@pytest.mark.integration
@pytest.mark.celery
def test_report_generation_full_workflow(
    integration_client,
    integration_db_session,
    integration_test_user,
    setup_complete_chat_history
):
    """
    场景：完整的报告生成流程
    1. 触发报告生成 -> 202 Accepted
    2. Worker 处理报告生成
    3. 状态更新为 READY
    4. 获取报告内容
    
    ⚠️ 注意：此测试需要真实的 Celery Worker 运行
    """
    # 1. 触发报告生成
    response = integration_client.post("/api/v1/report/generate")
    
    assert response.status_code == 202
    data = response.json()
    report_id = uuid.UUID(data["report_id"])
    assert data["status"] == "GENERATING"
    
    # 2. 验证报告已创建且状态为 GENERATING
    report = integration_db_session.query(Report).filter(Report.id == report_id).first()
    assert report is not None
    assert report.status == "GENERATING"
    
    # 3. 等待 Worker 处理完成（最多等待90秒，报告生成可能比信件慢）
    print("\n⏳ 等待 Celery Worker 生成报告...")
    completed_report = wait_for_task_completion(
        db_session=integration_db_session,
        model=Report,
        record_id=report_id,
        status_field="status",
        expected_status="READY",
        timeout=90,
        poll_interval=3
    )
    
    # 4. 验证处理结果
    assert completed_report is not None, "❌ 超时：Worker 未在90秒内完成任务"
    assert completed_report.status == "READY", f"❌ 状态错误：{completed_report.status}"
    assert completed_report.content is not None, "❌ 报告内容为空"
    
    # 5. 验证报告内容格式
    import json
    try:
        content = json.loads(completed_report.content) if isinstance(completed_report.content, str) else completed_report.content
        
        # WOOP框架必须包含的字段
        required_fields = ["wish", "outcome", "obstacle", "plan"]
        for field in required_fields:
            assert field in content, f"❌ 缺少必填字段：{field}"
            assert content[field] is not None, f"❌ 字段为空：{field}"
        
        print(f"✅ 测试通过：报告生成成功")
        print(f"   Wish: {content['wish'][:50]}...")
        print(f"   Outcome: {content['outcome'][:50]}...")
        
    except json.JSONDecodeError:
        pytest.fail("❌ 报告内容不是有效的JSON格式")


@pytest.mark.integration
@pytest.mark.celery
def test_report_status_polling(
    integration_client,
    integration_db_session,
    integration_test_user,
    setup_complete_chat_history
):
    """
    场景：模拟前端轮询报告状态
    1. 触发报告生成
    2. 多次轮询状态接口
    3. 验证状态从 GENERATING -> READY
    4. 获取报告内容
    
    ⚠️ 注意：此测试需要真实的 Celery Worker 运行
    """
    # 1. 触发报告生成
    response = integration_client.post("/api/v1/report/generate")
    assert response.status_code == 202
    report_id = uuid.UUID(response.json()["report_id"])
    
    # 2. 模拟前端轮询（最多30次，每3秒一次）
    print("\n⏳ 模拟前端轮询报告状态...")
    max_polls = 30
    poll_count = 0
    final_status = None
    
    import time
    for i in range(max_polls):
        poll_count += 1
        
        response = integration_client.get("/api/v1/report/status")
        assert response.status_code == 200
        
        data = response.json()
        status = data["status"]
        
        print(f"   第 {poll_count} 次轮询: {status}")
        
        if status == "READY":
            final_status = "READY"
            print(f"✅ 报告生成完成，共轮询 {poll_count} 次")
            break
        elif status == "FAILED":
            final_status = "FAILED"
            pytest.fail("❌ 报告生成失败")
        elif status == "GENERATING":
            time.sleep(3)  # 等待3秒后继续轮询
    
    assert final_status == "READY", f"❌ 超时或状态错误: {final_status}"
    
    # 3. 获取报告内容
    latest_response = integration_client.get("/api/v1/report/latest")
    assert latest_response.status_code == 200
    
    latest_data = latest_response.json()
    assert latest_data["report_id"] == str(report_id)
    assert latest_data["status"] == "READY"
    assert "content" in latest_data
    
    # 验证WOOP框架字段
    content = latest_data["content"]
    assert "wish" in content
    assert "outcome" in content
    assert "obstacle" in content
    assert "plan" in content


@pytest.mark.integration
@pytest.mark.celery
def test_report_idempotency(
    integration_client,
    integration_db_session,
    integration_test_user,
    setup_complete_chat_history
):
    """
    场景：测试报告生成的幂等性
    1. 第一次生成报告
    2. 等待完成
    3. 再次尝试生成应返回错误
    
    ⚠️ 注意：此测试需要真实的 Celery Worker 运行
    """
    # 1. 第一次生成报告
    response = integration_client.post("/api/v1/report/generate")
    assert response.status_code == 202
    report_id = uuid.UUID(response.json()["report_id"])
    
    # 2. 等待完成
    print("\n⏳ 等待报告生成完成...")
    completed_report = wait_for_task_completion(
        db_session=integration_db_session,
        model=Report,
        record_id=report_id,
        status_field="status",
        expected_status="READY",
        timeout=90,
        poll_interval=3
    )
    
    assert completed_report is not None, "❌ 第一次生成超时"
    assert completed_report.status == "READY"
    
    # 3. 再次尝试生成应返回错误
    retry_response = integration_client.post("/api/v1/report/generate")
    assert retry_response.status_code == 400
    assert retry_response.json()["detail"] == "REPORT_ALREADY_GENERATED"
    
    print("✅ 幂等性验证通过：已生成的报告无法重复生成")




