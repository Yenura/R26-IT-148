"""
Component 2: Interview System - Database Models & Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ====================================================================
# ENUMS
# ====================================================================

class QuestionTypeEnum(str, Enum):
    MCQ = "MCQ"
    DESCRIPTIVE = "Descriptive"
    CODING = "Coding"


class DifficultyEnum(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"


class GradeEnum(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"
    BELOW_AVERAGE = "Below Average"
    POOR = "Poor"


# ====================================================================
# QUESTION MODELS
# ====================================================================

class QuestionBase(BaseModel):
    """Base question schema"""
    question_text: str
    question_type: QuestionTypeEnum
    difficulty: DifficultyEnum
    category: str
    topic: str
    keywords: List[str] = []


class MCQOption(BaseModel):
    """MCQ option"""
    index: int
    text: str


class MCQQuestion(QuestionBase):
    """MCQ question"""
    options: List[MCQOption]
    correct_option: int


class DescriptiveQuestion(QuestionBase):
    """Descriptive question"""
    answer_text: str
    expected_length: Optional[str] = "Medium"  # Short, Medium, Long


class TestCase(BaseModel):
    """Test case for coding question"""
    input: Dict[str, Any]
    expected_output: Any
    description: Optional[str] = None


class CodingQuestion(QuestionBase):
    """Coding question"""
    language: str = "Python"
    test_cases: List[TestCase]
    expected_complexity: str = "O(n)"
    time_limit: int = 900  # seconds


# ====================================================================
# ANSWER MODELS
# ====================================================================

class MCQAnswer(BaseModel):
    """MCQ answer submission"""
    question_id: str
    selected_option: int
    time_taken_seconds: int
    skipped: bool = False


class DescriptiveAnswer(BaseModel):
    """Descriptive answer submission"""
    question_id: str
    answer_text: str
    time_taken_seconds: int


class CodeSubmission(BaseModel):
    """Code submission for evaluation"""
    question_id: str
    code_text: str
    language: str = "Python"
    time_taken_seconds: int


class AnswerSubmission(BaseModel):
    """Unified answer submission"""
    candidate_id: str
    session_id: str
    question_id: str
    question_type: QuestionTypeEnum
    mcq_answer: Optional[MCQAnswer] = None
    descriptive_answer: Optional[DescriptiveAnswer] = None
    code_submission: Optional[CodeSubmission] = None
    answer_text: Optional[str] = None
    code_text: Optional[str] = None
    language: Optional[str] = "Python"
    submitted_at: datetime = Field(default_factory=datetime.utcnow)


# ====================================================================
# SCORING MODELS
# ====================================================================

class MCQScoreDetail(BaseModel):
    """MCQ score details"""
    question_id: str
    correct_option: int
    candidate_option: int
    score: float
    is_correct: bool


class DescriptiveScoreDetail(BaseModel):
    """Descriptive score details"""
    question_id: str
    cosine_similarity: float
    keyword_coverage: float
    raw_score: float
    final_score: float
    alpha: float = 0.7
    beta: float = 0.3


class CodeScoreDetail(BaseModel):
    """Coding score details"""
    question_id: str
    test_pass_rate: float
    tests_passed: int
    total_tests: int
    syntax_valid: bool
    complexity_order: int
    quality_score: float
    code_score: float


# ====================================================================
# PROCTORING MODELS
# ====================================================================

class ProctoringFlags(BaseModel):
    """Raw flag counts collected during live proctoring"""
    face_absent_seconds: int = 0
    multiple_faces_count: int = 0
    gaze_off_screen_count: int = 0
    second_voice_count: int = 0
    tab_switch_count: int = 0
    paste_event_count: int = 0
    code_typed_too_fast: bool = False
    right_click_count: int = 0
    devtools_opened: bool = False


class ProctoringTimelineEntry(BaseModel):
    """Single event on the proctoring timeline"""
    t: int = 0                # seconds from interview start
    event: str = ""           # gaze_off_screen, tab_switch, paste_event, etc.
    duration: float = 0       # optional duration in seconds
    question: str = ""        # optional question reference


class ProctoringFeatures(BaseModel):
    """Feature vectors extracted during interview for post-processing analysis"""
    face_landmarks: List[Dict] = []   # [{t, bbox: {x,y,w,h}}, ...]
    gaze_vectors: List[Dict] = []     # [{t, x, y, off_screen}, ...]
    head_pose: List[Dict] = []        # [{t, pitch, yaw, roll}, ...]
    audio_features: List[Dict] = []   # [{t, energy, spectral_centroid, speech_ratio, is_speaking}, ...]


class ProctoringAnalysis(BaseModel):
    """Computed analysis from feature vectors"""
    nonverbal: Dict = {}     # {eye_contact_pct, head_movement_score, total_frames}
    speech: Dict = {}        # {avg_energy, speech_ratio, avg_spectral_centroid}
    confidence: Dict = {}    # {overall_score, gaze_aversion_rate, head_movement_normalized}


class ProctoringData(BaseModel):
    """Complete proctoring payload sent with interview submission"""
    integrity_score: int = 100
    flags: ProctoringFlags = ProctoringFlags()
    timeline: List[Dict] = []
    duration_seconds: int = 0
    features: Optional[ProctoringFeatures] = None
    analysis: Optional[ProctoringAnalysis] = None


class InterviewScoreResult(BaseModel):
    """Interview score result"""
    interview_id: str
    candidate_id: str
    session_id: str
    job_role: str
    
    # Aggregate scores
    mcq_score: float = 0
    descriptive_score: float = 0
    coding_score: float = 0
    interview_score: float = 0
    grade: GradeEnum
    
    # Detailed metrics
    mcq_total: int = 0
    mcq_correct: int = 0
    descriptive_total: int = 0
    coding_total: int = 0
    coding_tests_passed: int = 0
    
    # Detailed breakdowns
    mcq_details: List[MCQScoreDetail] = []
    descriptive_details: List[DescriptiveScoreDetail] = []
    coding_details: List[CodeScoreDetail] = []
    
    # Weights used
    weights_used: Dict[str, float] = {}
    
    # Weak areas
    weak_topics: List[str] = []
    failed_mcq_topics: List[str] = []
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_time_seconds: int = 0

    # Proctoring (job interviews only)
    integrity_score: Optional[int] = None
    proctoring: Optional[ProctoringData] = None


# ====================================================================
# INTERVIEW SESSION MODELS
# ====================================================================

class InterviewQuestion(BaseModel):
    """Question in interview"""
    id: str
    sequence: int
    question_text: str
    question_type: QuestionTypeEnum
    difficulty: DifficultyEnum
    category: str
    topic: str
    options: Optional[List[MCQOption]] = None
    test_cases: Optional[List[TestCase]] = None
    time_limit_seconds: int = 900


class InterviewSession(BaseModel):
    """Interview session"""
    session_id: str
    candidate_id: str
    job_role: str
    required_skills: List[str]
    questions: List[InterviewQuestion]
    
    question_count: Dict[str, int]
    total_questions: int
    
    mcq_time: int = 60
    desc_time: int = 300
    coding_time: int = 600
    total_time: int = 60
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "created"  # created, in_progress, completed


class InterviewRequest(BaseModel):
    """Request to create interview"""
    candidate_id: str
    job_role: str
    required_skills: List[str]
    num_questions: int = 10
    mcq_count: Optional[int] = None
    desc_count: Optional[int] = None
    coding_count: Optional[int] = None
    job_level: Optional[str] = "Mid-Level"
    mcq_time: Optional[int] = 60
    desc_time: Optional[int] = 300
    coding_time: Optional[int] = 600
    total_time: Optional[int] = 60
    job_description: Optional[str] = ""
    job_id: Optional[str] = ""
    is_practice: Optional[bool] = False


# ====================================================================
# RESPONSE MODELS
# ====================================================================

class QuestionResponse(BaseModel):
    """Response containing a question"""
    success: bool
    message: str
    data: Optional[InterviewQuestion] = None


class InterviewSessionResponse(BaseModel):
    """Response containing interview session"""
    success: bool
    message: str
    data: Optional[InterviewSession] = None


class EvaluationResponse(BaseModel):
    """Response containing evaluation results"""
    success: bool
    message: str
    data: Optional[InterviewScoreResult] = None


class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict] = None


# ====================================================================
# STATISTICS & ANALYTICS MODELS
# ====================================================================

class CandidateStats(BaseModel):
    """Candidate statistics"""
    candidate_id: str
    total_interviews: int
    average_score: float
    best_score: float
    weak_areas: List[str]
    last_interview: Optional[datetime] = None


class JobRoleStats(BaseModel):
    """Job role statistics"""
    job_role: str
    total_candidates: int
    average_score: float
    pass_rate: float
    common_weak_areas: List[str]


# ====================================================================
# DATABASE MODELS (SQLAlchemy)
# ====================================================================

class InterviewDB(BaseModel):
    """SQLAlchemy model for interview"""
    id: Optional[str] = None
    session_id: str
    candidate_id: str
    job_role: str
    questions_count: int
    total_time_seconds: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AnswerDB(BaseModel):
    """SQLAlchemy model for answer"""
    id: Optional[str] = None
    interview_id: str
    question_id: str
    question_type: str
    answer_text: Optional[str] = None
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    time_taken_seconds: int = 0
    
    class Config:
        from_attributes = True


class ScoreResultDB(BaseModel):
    """SQLAlchemy model for score result"""
    id: Optional[str] = None
    interview_id: str
    candidate_id: str
    job_role: str
    interview_score: float
    mcq_score: float
    descriptive_score: float
    coding_score: float
    grade: str
    weak_topics: str = ""  # JSON string
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        from_attributes = True
