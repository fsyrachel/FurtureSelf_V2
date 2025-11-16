import uuid

from app.models import User


def test_user_init_creates_new_user(client, db_session):
    """
    场景：anonymous_user_id 为空时应创建新用户并返回 ONBOARDING 状态。
    """
    response = client.post("/api/v1/user/init", json={"anonymous_user_id": None})

    assert response.status_code == 200
    data = response.json()
    created_id = uuid.UUID(data["user_id"])
    assert data["status"] == "ONBOARDING"

    user = db_session.query(User).filter(User.id == created_id).first()
    assert user is not None
    assert user.status == "ONBOARDING"


def test_user_init_returns_existing_user(client, db_session):
    """
    场景：传入已有用户 ID 时应该直接返回其状态。
    """
    existing_user = User(id=uuid.uuid4(), status="ACTIVE")
    db_session.add(existing_user)
    db_session.commit()

    response = client.post(
        "/api/v1/user/init", json={"anonymous_user_id": str(existing_user.id)}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == str(existing_user.id)
    assert data["status"] == "ACTIVE"



