from datetime import datetime

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("push_jobs.id"))
    hubspot_id: Mapped[str | None] = mapped_column()
    status: Mapped[str | None] = mapped_column(
        default="pending"
    )  # pending, completed, failed
    first_name: Mapped[str | None] = mapped_column()
    last_name: Mapped[str | None] = mapped_column()
    email: Mapped[str | None] = mapped_column(index=True)
    linkedin_id: Mapped[str | None] = mapped_column(index=True)
    phone: Mapped[str | None] = mapped_column()
    company: Mapped[str | None] = mapped_column()
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"Contact(id={self.id}, hubspot_id={self.hubspot_id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, linkedin_id={self.linkedin_id}, phone={self.phone}, company={self.company})"


class PushJob(Base):
    __tablename__ = "push_jobs"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(
        index=True, default="pending"
    )  # pending, completed, failed
    error: Mapped[str | None] = mapped_column()
    created_count: Mapped[int | None] = mapped_column(default=0)
    updated_count: Mapped[int | None] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"PushJob(id={self.id}, status={self.status}, error={self.error})"
