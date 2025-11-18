from pydantic import BaseModel, Field, confloat
from typing import List, Dict, Optional
import uuid
from datetime import datetime

# --- F1.1 (User Init) ---
class UserInitRequest(BaseModel):
    anonymous_user_id: Optional[uuid.UUID] = None

class UserInitResponse(BaseModel):
    user_id: uuid.UUID
    status: str # 'ONBOARDING' or 'ACTIVE'

# --- F2.1 (Current Profile) ----
# Define type aliases for constrained types at the module level
from typing import NewType

NameStr = NewType('NameStr', str)
ShortStr = NewType('ShortStr', str)
AgeInt = NewType('AgeInt', int)

class DemoDataSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=18, le=100)
    gender: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)
    field: str = Field(..., min_length=1)
    interests: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)
    future_location: str = Field(..., min_length=1)


# Tech Specs v1.5 的验证规则
# (问卷是 1-5 分)
ValsValue = confloat(ge=1.0, le=5.0)
BfiValue = confloat(ge=1.0, le=5.0)

class CurrentProfileRequest(BaseModel):
    demo_data: DemoDataSchema
    # 价值观 (PVQ)
    vals_data: Dict[str, float]
    # 人格特质 (BFI)
    bfi_data: Dict[str, float]

class CurrentProfileResponse(BaseModel):
    status: str = "CURRENT_PROFILE_SAVED"

# --- F2.2 (Future Profile) ----
class FutureProfileItem(BaseModel):
    profile_name: str = Field(..., min_length=1, max_length=100)
    # 3 个空白框
    future_values: str = Field(..., min_length=10, max_length=2000)
    future_vision: str = Field(..., min_length=10, max_length=2000)
    future_obstacles: str = Field(..., min_length=10, max_length=2000)

class FutureProfileRequest(BaseModel):
    # 最多 3 个 (如 "UX研究员", "读博", "自由职业")
    profiles: List[FutureProfileItem] = Field(..., min_length=1, max_length=3) 

class CreatedProfileInfo(BaseModel):
    future_profile_id: uuid.UUID
    profile_name: str

class FutureProfileResponse(BaseModel):
    status: str = "ACTIVE"
    user_id: uuid.UUID
    created_profiles: List[CreatedProfileInfo]

# --- F3.1.2 (Submit Letter) ---
class LetterSubmitRequest(BaseModel):
    content: str = Field(..., min_length=50, max_length=5000)

class LetterSubmitResponse(BaseModel):
    letter_id: uuid.UUID
    status: str = "SUBMITTED" 

# --- F6.6 (Poll Status) ---
class LetterStatusResponse(BaseModel):
    status: str # 'PENDING', 'REPLIES_READY', or 'FAILED'
    content: str | None = None  # 信件内容，仅在状态为 FAILED 时返回，其他状态为 None

# --- F6.5 (Inbox) ---
class ReplyItem(BaseModel):
    reply_id: uuid.UUID
    future_profile_id: uuid.UUID
    from_profile_name: str
    chat_status: str # 'NOT_STARTED' or 'COMPLETED'

class InboxResponse(BaseModel):
    letter_id: uuid.UUID
    letter_content_snippet: str
    replies: List[ReplyItem]

# --- F3.1.3 (View Reply) ---
class LetterReplyResponse(BaseModel):
    reply_id: uuid.UUID
    future_profile_id: uuid.UUID
    from_profile_name: str
    content: str
    chat_status: str #

# --- F3.2.2 (Chat Send) ---
class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

class ChatMessageResponse(BaseModel):
    message_id: uuid.UUID
    sender: str # 'AGENT'
    content: str
    created_at: datetime

# --- F3.2.3 (Chat History) ---
class ChatHistoryResponse(BaseModel):
    message_id: uuid.UUID
    sender: str # 'USER' or 'AGENT'
    content: str
    created_at: datetime

# --- F5.1 (Report Generate) ---
class ReportGenerateRequest(BaseModel):
    letter_id: Optional[uuid.UUID] = None  # 指定信件（可选，默认使用最新）
    future_profile_id: Optional[uuid.UUID] = None  # 指定未来人设（可选，默认使用所有）

class ReportGenerateResponse(BaseModel):
    report_id: uuid.UUID
    status: str = "GENERATING"
    letter_id: Optional[uuid.UUID] = None
    future_profile_id: Optional[uuid.UUID] = None
<<<<<<< HEAD
    
=======

>>>>>>> b218fc476dc540b3f1ff99140de32a837678d817
# --- F5.3 (Report Status) ---
class ReportStatusResponse(BaseModel):
    status: str # 'GENERATING', 'READY', or 'FAILED'

# --- F5.2 (Report View) ---
class WOOPContent(BaseModel):
    wish: str # (v1.13) (Wish)
    outcome: str # (v1.13) (Outcome)
    obstacle: str # (v1.13) (Obstacle)
    plan: str # (v1.13) (Plan)

class ReportResponse(BaseModel):
    report_id: uuid.UUID
    status: str = "READY"
    content: WOOPContent
    created_at: datetime