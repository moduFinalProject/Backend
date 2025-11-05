from sqlalchemy import VARCHAR,Boolean,Column,Date,ForeignKey,Integer,Text,TIMESTAMP
from app.database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone


class User(Base):

    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True)
    unique_id = Column(VARCHAR(22),unique=True,nullable=False)
    email = Column(VARCHAR(100), unique=True, nullable=False)
    name = Column(VARCHAR(50), nullable=False)
    address = Column(VARCHAR(100), nullable=False)
    phone = Column(VARCHAR(20))
    birth_date = Column(Date, nullable=False)
    provider = Column(VARCHAR(50))
    provider_id = Column(VARCHAR(50))
    user_type = Column(VARCHAR(10))
    is_activate = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    last_accessed = Column(TIMESTAMP)
    gender = Column(VARCHAR(10), nullable=False)
    is_sanctions = Column(Boolean, default=False)

    # UserBlacklist relationships (다중 외래키)
    blocked_users = relationship(
        "UserBlacklist",
        foreign_keys="UserBlacklist.blocked_by",
        back_populates="blocker",
        cascade="all, delete-orphan",
    )

    updated_blacklists = relationship(
        "UserBlacklist",
        foreign_keys="UserBlacklist.updated_by",
        back_populates="updater",
    )

    blacklist_records = relationship(
        "UserBlacklist",
        foreign_keys="UserBlacklist.user_id",
        back_populates="blocked_user",
    )

    # 다른 테이블 relationships
    activity_logs = relationship(
        "UserActivityLog", back_populates="user", cascade="all, delete-orphan"
    )

    job_postings = relationship(
        "JobPosting", back_populates="user", cascade="all, delete-orphan"
    )

    resumes = relationship(
        "Resume", back_populates="user", cascade="all, delete-orphan"
    )

    files = relationship("File", back_populates="user", cascade="all, delete-orphan")

    resume_feedbacks = relationship(
        "ResumeFeedback", back_populates="user", cascade="all, delete-orphan"
    )

    interviews = relationship(
        "Interview", back_populates="user", cascade="all, delete-orphan"
    )

    study_guides = relationship(
        "StudyGuide", back_populates="user", cascade="all, delete-orphan"
    )


class UserBlacklist(Base):

    __tablename__ = "userblacklists"

    blacklist_id = Column(Integer, primary_key=True)
    blocked_by = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    updated_by = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    reason = Column(VARCHAR(200))
    blocked_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    block_period = Column(TIMESTAMP)

    blocker = relationship(
        "User", foreign_keys=[blocked_by], back_populates="blocked_users"
    )

    updater = relationship(
        "User", foreign_keys=[updated_by], back_populates="updated_blacklists"
    )

    blocked_user = relationship(
        "User", foreign_keys=[user_id], back_populates="blacklist_records"
    )


class UserActivityLog(Base):

    __tablename__ = "useractiviylogs"

    log_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    action_type = Column(VARCHAR(50))
    description = Column(VARCHAR(200))
    ip_address = Column(VARCHAR(100))
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="activity_logs")


class JobPosting(Base):

    __tablename__ = "jobpostings"

    posting_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    url = Column(VARCHAR(1000))
    title = Column(VARCHAR(30), nullable=False)
    company = Column(VARCHAR(30), nullable=False)
    content = Column(VARCHAR(300))
    qualification = Column(VARCHAR(300), nullable=False)
    prefer = Column(VARCHAR(300), nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="job_postings")

    resumes = relationship("Resume", back_populates="job_posting")

    resume_feedbacks = relationship(
        "ResumeFeedback", back_populates="job_posting", cascade="all, delete-orphan"
    )

    interviews = relationship("Interview", back_populates="job_posting")

    study_guides = relationship("StudyGuide", back_populates="job_posting")


class Resume(Base):

    __tablename__ = "resumes"

    resume_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    posting_id = Column(
        Integer, ForeignKey("jobpostings.posting_id", ondelete="SET NULL")
    )
    title = Column(VARCHAR(30), nullable=False)
    resume_type = Column(VARCHAR(10), nullable=False)
    is_active = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    email = Column(VARCHAR(50))
    address = Column(VARCHAR(50))
    phone = Column(VARCHAR(50))
    military_service = Column(VARCHAR(10))
    birth_date = Column(Date)
    self_introduction = Column(Text)

    user = relationship("User", back_populates="resumes")
    job_posting = relationship("JobPosting", back_populates="resumes")

    projects = relationship(
        "Project", back_populates="resume", cascade="all, delete-orphan"
    )

    activities = relationship(
        "Activity", back_populates="resume", cascade="all, delete-orphan"
    )

    experiences = relationship(
        "Experience", back_populates="resume", cascade="all, delete-orphan"
    )

    technology_stacks = relationship(
        "TechnologyStack", back_populates="resume", cascade="all, delete-orphan"
    )

    educations = relationship(
        "Education", back_populates="resume", cascade="all, delete-orphan"
    )

    qualifications = relationship(
        "Qualification", back_populates="resume", cascade="all, delete-orphan"
    )

    files = relationship("File", back_populates="resume")

    resume_feedbacks = relationship(
        "ResumeFeedback", back_populates="resume", cascade="all, delete-orphan"
    )

    interviews = relationship(
        "Interview", back_populates="resume", cascade="all, delete-orphan"
    )


class Project(Base):

    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True)
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    title = Column(VARCHAR(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    resume = relationship("Resume", back_populates="projects")


class Activity(Base):

    __tablename__ = "activities"

    activity_id = Column(Integer, primary_key=True)
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    title = Column(VARCHAR(20), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    resume = relationship("Resume", back_populates="activities")


class Experience(Base):

    __tablename__ = "experiences"

    experience_id = Column(Integer, primary_key=True)
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    job_title = Column(VARCHAR(20), nullable=False)
    department = Column(VARCHAR(20), nullable=False)
    position = Column(VARCHAR(20))
    job_description = Column(VARCHAR(1000))
    employment_status = Column(Boolean, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    resume = relationship("Resume", back_populates="experiences")


class TechnologyStack(Base):

    __tablename__ = "technologystacks"

    technology_stack_id = Column(Integer, primary_key=True)
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    title = Column(VARCHAR(20), nullable=False)

    resume = relationship("Resume", back_populates="technology_stacks")


class Education(Base):

    __tablename__ = "educations"

    education_id = Column(Integer, primary_key=True)
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    organ = Column(VARCHAR(20), nullable=False)
    department = Column(VARCHAR(20), nullable=False)
    degree_level = Column(VARCHAR(10))
    score = Column(VARCHAR(10))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)

    resume = relationship("Resume", back_populates="educations")


class Qualification(Base):

    __tablename__ = "qualifications"

    qualification_id = Column(Integer, primary_key=True)
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    title = Column(VARCHAR(20), nullable=False)
    acquisition_date = Column(Date, nullable=False)
    score = Column(VARCHAR(10))
    organ = Column(VARCHAR(20))

    resume = relationship("Resume", back_populates="qualifications")


class File(Base):

    __tablename__ = "files"

    file_id = Column(Integer, primary_key=True)
    fileable_id = Column(Integer, ForeignKey("resumes.resume_id", ondelete="SET NULL"))
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    filetype = Column(VARCHAR(10), nullable=False)
    fileable_table = Column(VARCHAR(30), nullable=False)
    org_file_name = Column(VARCHAR(100), nullable=False)
    mod_file_name = Column(VARCHAR(100), nullable=False)
    file_rul = Column(VARCHAR(100), nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="files")
    resume = relationship("Resume", back_populates="files")


class ResumeFeedback(Base):

    __tablename__ = "resumefeedbacks"

    feedback_id = Column(Integer, primary_key=True)
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    posting_id = Column(
        Integer,
        ForeignKey("jobpostings.posting_id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_content = Column(Text, nullable=False)
    matching_rate = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="resume_feedbacks")
    user = relationship("User", back_populates="resume_feedbacks")
    job_posting = relationship("JobPosting", back_populates="resume_feedbacks")

    feedback_contents = relationship(
        "FeedbackContent",
        back_populates="resume_feedback",
        cascade="all, delete-orphan",
    )


class FeedbackContent(Base):

    __tablename__ = "feedbackcontents"

    feedbackcontent_id = Column(Integer, primary_key=True)
    feedback_id = Column(
        Integer,
        ForeignKey("resumefeedbacks.feedback_id", ondelete="CASCADE"),
        nullable=False,
    )
    feedback_devision = Column(VARCHAR(10), nullable=False)
    feedback_result = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    resume_feedback = relationship("ResumeFeedback", back_populates="feedback_contents")


class Interview(Base):

    __tablename__ = "interviews"

    interview_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    resume_id = Column(
        Integer, ForeignKey("resumes.resume_id", ondelete="CASCADE"), nullable=False
    )
    posting_id = Column(
        Integer, ForeignKey("jobpostings.posting_id", ondelete="SET NULL")
    )
    total_score = Column(Integer)

    user = relationship("User", back_populates="interviews")
    resume = relationship("Resume", back_populates="interviews")
    job_posting = relationship("JobPosting", back_populates="interviews")

    conversations = relationship(
        "Conversation", back_populates="interview", cascade="all, delete-orphan"
    )

    interview_feedbacks = relationship(
        "InterviewFeedback", back_populates="interview", cascade="all, delete-orphan"
    )


class Conversation(Base):

    __tablename__ = "conversations"

    conversation_id = Column(Integer, primary_key=True)
    interview_id = Column(
        Integer,
        ForeignKey("interviews.interview_id", ondelete="CASCADE"),
        nullable=False,
    )
    question = Column(VARCHAR(300), nullable=False)
    answer = Column(VARCHAR(300), nullable=False)
    feedback = Column(VARCHAR(300), nullable=False)

    interview = relationship("Interview", back_populates="conversations")


class InterviewFeedback(Base):

    __tablename__ = "interviewfeedbacks"

    interview_feedback_id = Column(Integer, primary_key=True)
    interview_id = Column(
        Integer,
        ForeignKey("interviews.interview_id", ondelete="CASCADE"),
        nullable=False,
    )
    title = Column(VARCHAR(20), nullable=False)
    status = Column(VARCHAR(5), nullable=False)
    content = Column(VARCHAR(100), nullable=False)

    interview = relationship("Interview", back_populates="interview_feedbacks")


class StudyGuide(Base):

    __tablename__ = "studyguides"

    guide_id = Column(Integer, primary_key=True)
    user_id = Column(
        Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    posting_id = Column(
        Integer, ForeignKey("jobpostings.posting_id", ondelete="SET NULL")
    )
    title = Column(VARCHAR(20), nullable=False)
    description = Column(VARCHAR(200), nullable=False)
    is_activate = Column(Boolean, default=True)
    deleted_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="study_guides")
    job_posting = relationship("JobPosting", back_populates="study_guides")

    study_items = relationship(
        "StudyItem", back_populates="study_guide", cascade="all, delete-orphan"
    )


class StudyItem(Base):

    __tablename__ = "studyitems"

    study_item_id = Column(Integer, primary_key=True)
    guide_id = Column(
        Integer, ForeignKey("studyguides.guide_id", ondelete="CASCADE"), nullable=False
    )
    keyword = Column(VARCHAR(20), nullable=False)
    title = Column(VARCHAR(50), nullable=False)
    content = Column(VARCHAR(200), nullable=False)
    estimated_time = Column(Integer, nullable=False)
    priority = Column(VARCHAR(10), nullable=False)

    study_guide = relationship("StudyGuide", back_populates="study_items")

    study_keywords = relationship(
        "StudyKeyword", back_populates="study_item", cascade="all, delete-orphan"
    )


class StudyKeyword(Base):

    __tablename__ = "studykeywords"

    keyword_id = Column(Integer, primary_key=True)
    study_item_id = Column(
        Integer,
        ForeignKey("studyitems.study_item_id", ondelete="CASCADE"),
        nullable=False,
    )
    keyword = Column(VARCHAR(20))

    study_item = relationship("StudyItem", back_populates="study_keywords")


class Code(Base):

    __tablename__ = "codes"

    code_id = Column(Integer, primary_key=True)
    detail_id = Column(Integer, primary_key=True)
    division = Column(VARCHAR(50), nullable=False)
    title = Column(VARCHAR(20), nullable=False)
