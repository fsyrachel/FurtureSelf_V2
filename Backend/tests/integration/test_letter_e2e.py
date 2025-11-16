"""
信件处理端到端集成测试
需要真实的 Celery Worker 运行
"""
import uuid
import pytest

from app.models import Letter, FutureProfile, CurrentProfile, LetterReply
from tests.integration.conftest import wait_for_task_completion


VALID_LETTER_CONTENT = (
    "亲爱的未来的我：这是端到端集成测试的信件内容。"
    "我们将测试从提交信件到 Worker 处理完成的完整流程。"
    "这段内容用于满足最小长度限制，确保能够通过Pydantic验证。"
)


@pytest.fixture()
def setup_profiles_for_letter(integration_db_session, integration_test_user):
    """
    为信件处理准备必要的档案数据
    Worker需要这些数据来生成回信
    """
    # 创建当前档案
    current_profile = CurrentProfile(
        id=uuid.uuid4(),
        user_id=integration_test_user.id,
        demo_data={"age": 25, "name": "测试用户"},
        vals_data={"value1": 3.0},
        bfi_data={"trait1": 4.0},
    )
    
    # 创建未来档案
    future_profile = FutureProfile(
        id=uuid.uuid4(),
        user_id=integration_test_user.id,
        profile_name="测试未来人设",
        profile_description="这是用于集成测试的未来人设描述，需要足够长以满足Worker处理要求。",
    )
    
    integration_db_session.add_all([current_profile, future_profile])
    integration_db_session.commit()
    integration_db_session.refresh(future_profile)
    
    return future_profile


@pytest.mark.integration
@pytest.mark.celery
def test_letter_submission_full_workflow(
    integration_client, 
    integration_db_session, 
    integration_test_user,
    setup_profiles_for_letter
):
    """
    场景：完整的信件处理流程
    1. 提交信件 -> 202 Accepted
    2. Worker 处理信件
    3. 生成回信
    4. 状态更新为 REPLIES_READY
    
    ⚠️ 注意：此测试需要真实的 Celery Worker 运行
    """
    # 1. 提交信件
    response = integration_client.post(
        "/api/v1/letters/submit",
        json={"content": VALID_LETTER_CONTENT}
    )
    
    assert response.status_code == 202
    data = response.json()
    letter_id = uuid.UUID(data["letter_id"])
    assert data["status"] == "SUBMITTED"
    
    # 2. 验证信件已创建且状态为 PENDING
    letter = integration_db_session.query(Letter).filter(Letter.id == letter_id).first()
    assert letter is not None
    assert letter.status == "PENDING"
    assert letter.content == VALID_LETTER_CONTENT
    
    # 3. 等待 Worker 处理完成（最多等待60秒）
    print("\n⏳ 等待 Celery Worker 处理信件...")
    completed_letter = wait_for_task_completion(
        db_session=integration_db_session,
        model=Letter,
        record_id=letter_id,
        status_field="status",
        expected_status="REPLIES_READY",
        timeout=60,
        poll_interval=2
    )
    
    # 4. 验证处理结果
    assert completed_letter is not None, "❌ 超时：Worker 未在60秒内完成任务"
    assert completed_letter.status == "REPLIES_READY", f"❌ 状态错误：{completed_letter.status}"
    
    # 5. 验证回信已生成
    replies = integration_db_session.query(LetterReply).filter(
        LetterReply.letter_id == letter_id
    ).all()
    
    assert len(replies) > 0, "❌ 未生成回信"
    
    for reply in replies:
        assert reply.content is not None
        assert len(reply.content) > 0
        assert reply.chat_status == "NOT_STARTED"
    
    print(f"✅ 测试通过：生成了 {len(replies)} 封回信")


@pytest.mark.integration
@pytest.mark.celery
def test_letter_status_polling(
    integration_client,
    integration_db_session,
    integration_test_user,
    setup_profiles_for_letter
):
    """
    场景：模拟前端轮询信件状态
    1. 提交信件
    2. 多次轮询状态接口
    3. 验证状态从 PENDING -> REPLIES_READY
    
    ⚠️ 注意：此测试需要真实的 Celery Worker 运行
    """
    # 1. 提交信件
    response = integration_client.post(
        "/api/v1/letters/submit",
        json={"content": VALID_LETTER_CONTENT}
    )
    assert response.status_code == 202
    letter_id = uuid.UUID(response.json()["letter_id"])
    
    # 2. 模拟前端轮询（最多30次，每2秒一次）
    print("\n⏳ 模拟前端轮询信件状态...")
    max_polls = 30
    poll_count = 0
    final_status = None
    
    import time
    for i in range(max_polls):
        poll_count += 1
        
        response = integration_client.get("/api/v1/letters/status")
        assert response.status_code == 200
        
        data = response.json()
        status = data["status"]
        
        print(f"   第 {poll_count} 次轮询: {status}")
        
        if status == "REPLIES_READY":
            final_status = "REPLIES_READY"
            print(f"✅ 信件处理完成，共轮询 {poll_count} 次")
            break
        elif status == "FAILED":
            final_status = "FAILED"
            pytest.fail(f"❌ 信件处理失败: {data.get('content', '')}")
        elif status == "PENDING":
            time.sleep(2)  # 等待2秒后继续轮询
        
    assert final_status == "REPLIES_READY", f"❌ 超时或状态错误: {final_status}"
    
    # 3. 验证收信箱接口可以正常访问
    inbox_response = integration_client.get("/api/v1/letters/inbox/latest")
    assert inbox_response.status_code == 200
    
    inbox_data = inbox_response.json()
    assert inbox_data["letter_id"] == str(letter_id)
    assert len(inbox_data["replies"]) > 0


@pytest.mark.integration
@pytest.mark.celery
@pytest.mark.slow
def test_letter_retry_on_failure(
    integration_client,
    integration_db_session,
    integration_test_user
):
    """
    场景：测试失败重试机制（需要模拟失败场景）
    
    注意：此测试可能需要特殊配置来触发失败
    例如：暂时关闭AI服务、使用错误的API密钥等
    
    ⚠️ 此测试默认跳过，需要手动触发
    """
    pytest.skip("需要特殊配置来触发失败场景")



