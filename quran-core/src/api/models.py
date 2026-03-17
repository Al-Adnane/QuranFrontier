"""Pydantic schemas for request/response models."""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Enumerations ====================

class DeonticStatus(str, Enum):
    """Islamic legal status."""
    OBLIGATORY = "obligatory"
    RECOMMENDED = "recommended"
    NEUTRAL = "neutral"
    DISLIKED = "disliked"
    FORBIDDEN = "forbidden"
    ABROGATED = "abrogated"


class HadithGrade(str, Enum):
    """Hadith authenticity grade."""
    SAHIH = "Sahih"
    HASAN = "Hasan"
    WEAK = "Weak"
    FABRICATED = "Fabricated"
    MAUQUF = "Mauquf"
    MURSAL = "Mursal"


class UserRole(str, Enum):
    """User roles with permission levels."""
    PUBLIC = "public"
    RESEARCHER = "researcher"
    SCHOLAR = "scholar"
    ADMIN = "admin"


class CorrectionStatus(str, Enum):
    """Status of submitted corrections."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    UNDER_REVIEW = "under_review"
    CONFLICTED = "conflicted"


class Madhab(str, Enum):
    """Islamic schools of jurisprudence."""
    HANAFI = "Hanafi"
    MALIKI = "Maliki"
    SHAFII = "Shafi'i"
    HANBALI = "Hanbali"
    TWELVER_SHIA = "Twelver Shia"
    ISMAILI = "Ismaili"


# ==================== Base Response Models ====================

class Metadata(BaseModel):
    """Response metadata."""
    source_confidence: float = Field(0.95, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    query_latency_ms: int = 0
    audit_trail_id: str = ""


class VerseReference(BaseModel):
    """Reference to a Quranic verse."""
    surah: int = Field(..., ge=1, le=114)
    ayah: int = Field(..., ge=1, le=286)

    @property
    def ref_string(self) -> str:
        return f"{self.surah}:{self.ayah}"


class StandardResponse(BaseModel):
    """Standard API response wrapper."""
    status: str = Field("success", pattern="^(success|error)$")
    data: Dict[str, Any] = {}
    metadata: Metadata = Field(default_factory=Metadata)
    disclaimers: List[str] = [
        "This is not a fatwa (religious ruling)",
        "Consult a qualified Islamic scholar for official guidance",
        "Use for research and educational purposes only"
    ]
    audit_trail_id: str = ""


# ==================== Verse Models ====================

class WordMorphology(BaseModel):
    """Morphological analysis of a word."""
    word: str
    root: Optional[str] = None
    pos: Optional[str] = None  # Part of speech
    pattern: Optional[str] = None
    case: Optional[str] = None
    number: Optional[str] = None
    gender: Optional[str] = None


class VerseResponse(BaseModel):
    """Full verse with metadata."""
    surah: int
    ayah: int
    arabic: str
    transliteration: Optional[str] = None
    english_translation: Optional[str] = None
    has_real_text: bool = True
    morphology: List[WordMorphology] = []
    rhetorical_density: float = 0.0
    word_count: int = 0
    letter_count: int = 0


class VerseWithTafsir(VerseResponse):
    """Verse with associated tafsir."""
    tafsir_ids: List[str] = []
    scholars: List[str] = []
    schools: List[str] = []


class VerseWithSupportingHadith(VerseResponse):
    """Verse with supporting hadiths."""
    supporting_hadith_ids: List[str] = []
    hadith_count: int = 0


class MadhabhRuling(BaseModel):
    """Madhab-specific ruling for a verse."""
    madhab: Madhab
    deontic_status: DeonticStatus
    reasoning: str
    confidence: float = Field(0.95, ge=0.0, le=1.0)


class VerseWithRulings(VerseResponse):
    """Verse with madhab-specific rulings."""
    madhab_rulings: List[MadhabhRuling] = []
    primary_ruling: Optional[DeonticStatus] = None


# ==================== Tafsir Models ====================

class TafsirEntry(BaseModel):
    """A tafsir commentary entry."""
    tafsir_id: str
    verse_reference: VerseReference
    scholar_name: str
    school: str
    text: str
    source: Optional[str] = None
    page_reference: Optional[str] = None
    year_compiled: Optional[int] = None


class TafsirSearchResult(BaseModel):
    """Search result for tafsir content."""
    tafsir_id: str
    scholar_name: str
    school: str
    excerpt: str
    relevance_score: float = Field(0.0, ge=0.0, le=1.0)
    verse_reference: VerseReference


class ScholarProfile(BaseModel):
    """Scholar information."""
    scholar_id: str
    name: str
    school: str
    era: str
    biography: Optional[str] = None
    tafsir_count: int = 0
    famous_works: List[str] = []


# ==================== Hadith Models ====================

class Narrator(BaseModel):
    """Hadith narrator information."""
    narrator_id: str
    name: str
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    reliability_grade: Optional[str] = None  # Thiqa, Saduq, etc.


class Chain(BaseModel):
    """Hadith narrator chain (isnad)."""
    chain_id: str
    narrators: List[Narrator]
    grade: HadithGrade
    chain_text: str


class HadithEntry(BaseModel):
    """Full hadith with all metadata."""
    hadith_id: str
    collection_name: str
    book_number: Optional[int] = None
    hadith_number: int
    text_ar: str
    text_en: Optional[str] = None
    primary_narrator: Narrator
    chains: List[Chain] = []
    grade: HadithGrade
    grade_justification: Optional[str] = None
    supporting_verses: List[VerseReference] = []


class HadithSearchResult(BaseModel):
    """Search result for hadith."""
    hadith_id: str
    collection_name: str
    hadith_number: int
    text_excerpt: str
    relevance_score: float = Field(0.0, ge=0.0, le=1.0)
    grade: HadithGrade


# ==================== Graph Models ====================

class GraphNode(BaseModel):
    """Knowledge graph node."""
    node_id: str
    node_type: str  # "verse", "hadith", "scholar", "concept"
    label: str
    metadata: Dict[str, Any] = {}


class GraphRelationship(BaseModel):
    """Knowledge graph relationship."""
    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: str  # "supports", "contradicts", "extends", etc.
    confidence: float = Field(0.95, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}


class GraphPath(BaseModel):
    """Path between two nodes."""
    source_id: str
    target_id: str
    path_length: int
    nodes: List[GraphNode]
    relationships: List[GraphRelationship]


# ==================== Governance Models ====================

class CorrectionRequest(BaseModel):
    """Submitted correction request."""
    correction_id: str
    verse_reference: VerseReference
    correction_type: str  # "translation", "tafsir", "metadata", etc.
    current_value: str
    proposed_value: str
    justification: str
    submitted_by: str
    submitted_at: datetime
    status: CorrectionStatus
    approvals: List[str] = []
    rejections: List[str] = []


class CorrectionSubmission(BaseModel):
    """Submit a new correction."""
    verse_reference: VerseReference
    correction_type: str
    current_value: str
    proposed_value: str
    justification: str


class ApprovalDecision(BaseModel):
    """Scholar approval/rejection decision."""
    correction_id: str
    decision: str = Field(..., pattern="^(approve|reject)$")
    reasoning: str
    scholar_id: str


class ConflictResolution(BaseModel):
    """Conflict resolution request."""
    conflicted_correction_ids: List[str]
    resolution_type: str  # "voting", "consensus", "escalation"
    proposer_id: str


class AuditLogEntry(BaseModel):
    """Immutable audit log entry."""
    audit_id: str
    action: str
    actor: str
    resource_id: str
    resource_type: str
    timestamp: datetime
    details: Dict[str, Any] = {}
    hash_chain: Optional[str] = None  # For immutability


class ScholarDashboard(BaseModel):
    """Scholar board view."""
    scholar_id: str
    pending_corrections: int
    approved_corrections: int
    rejected_corrections: int
    active_conflicts: int
    recent_actions: List[AuditLogEntry]


class TransparencyReport(BaseModel):
    """Public transparency report."""
    report_date: datetime
    total_corrections_submitted: int
    total_corrections_approved: int
    approval_rate: float = Field(0.0, ge=0.0, le=1.0)
    active_scholars: int
    major_changes: List[Dict[str, Any]]
    conflict_resolution_time_avg_hours: float


class APIUsageStats(BaseModel):
    """API usage analytics."""
    total_requests: int
    requests_today: int
    requests_this_month: int
    average_latency_ms: float
    peak_concurrent_users: int
    endpoint_stats: Dict[str, Dict[str, Any]] = {}


# ==================== Authentication Models ====================

class LoginRequest(BaseModel):
    """Login credentials."""
    username: str = Field(..., min_length=3)
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user_id: str
    role: UserRole


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class UserCreate(BaseModel):
    """Create new user."""
    username: str = Field(..., min_length=3)
    email: str = Field(..., pattern=r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.RESEARCHER


class UserUpdate(BaseModel):
    """Update user."""
    role: Optional[UserRole] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User information."""
    user_id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime
    is_active: bool


# ==================== Admin Models ====================

class BackupRequest(BaseModel):
    """Backup request."""
    include_audit_logs: bool = True
    compression: str = "gzip"  # "gzip", "bzip2", "none"


class BackupResponse(BaseModel):
    """Backup response."""
    backup_id: str
    timestamp: datetime
    size_bytes: int
    status: str


class SystemHealth(BaseModel):
    """System health status."""
    status: str
    database_status: str
    cache_status: str
    api_response_time_ms: float
    uptime_hours: float
    error_rate: float


class ConfigUpdate(BaseModel):
    """System configuration update."""
    config_key: str
    config_value: Any
    requires_restart: bool = False


# ==================== Search Models ====================

class SemanticSearchRequest(BaseModel):
    """Semantic search request."""
    query: str = Field(..., min_length=1)
    limit: int = Field(10, ge=1, le=100)
    min_confidence: float = Field(0.5, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    """Generic search result."""
    result_id: str
    result_type: str  # "verse", "hadith", "tafsir"
    title: str
    excerpt: str
    score: float = Field(0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}


class FullTextSearchRequest(BaseModel):
    """Full-text search request."""
    query: str = Field(..., min_length=1)
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)
    filters: Optional[Dict[str, Any]] = None


# ==================== Endpoint 49: Narrator Biography ====================

class NarratorBiography(BaseModel):
    """Complete biographical information for a hadith narrator."""
    narrator_id: str
    name: str
    aliases: List[str] = []
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    birth_location: Optional[str] = None
    death_location: Optional[str] = None
    profession: Optional[str] = None
    era: Optional[str] = None
    reliability_grade: Optional[str] = None  # Thiqa, Saduq, Weak, etc.
    hadith_count: int = 0
    famous_works: List[str] = []
    teachers: List[Dict[str, str]] = []  # [{name: str, era: str}]
    students: List[Dict[str, str]] = []  # [{name: str, era: str}]
    biography_text: Optional[str] = None
    sources: List[str] = []
    reliability_justification: Optional[str] = None
    scholarly_consensus: Optional[str] = None


# ==================== Endpoint 50: Madhab Timeline ====================

class MadhabhRulingEvolution(BaseModel):
    """How a ruling evolved within a madhab over time."""
    century: str  # "7th Century AH", etc.
    year_range: Optional[str] = None
    deontic_status: DeonticStatus
    scholar_name: str
    justification: str
    evidence_verses: List[VerseReference] = []
    supporting_hadiths: List[str] = []
    consensus_at_time: Optional[str] = None


class MadhabhTimeline(BaseModel):
    """Timeline of ruling evolution for a madhab."""
    madhab_id: str
    madhab: Madhab
    topic: str
    verse_reference: Optional[VerseReference] = None
    current_ruling: Optional[MadhabhRuling] = None
    evolution_history: List[MadhabhRulingEvolution] = []
    timeline_start_century: str
    timeline_end_century: str
    notable_disputes: List[Dict[str, Any]] = []
    scholarly_sources: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.utcnow)
