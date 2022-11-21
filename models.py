import enum
import uuid

from sqlalchemy import Column, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import BOOLEAN, INTEGER, TIMESTAMP, UUID, VARCHAR
from sqlalchemy.orm import relationship

from db import Base

# from enum import Enum

# from db import Base


class Gender(enum.Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    OTHER = "OTHER"


class Status(enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Application_type(enum.Enum):
    LEAVE = "LEAVE"
    WFH = "WORK FROM HOME"


class Employee(Base):
    __tablename__ = "employees"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"))
    first_name = Column(VARCHAR)
    last_name = Column(VARCHAR)
    dob = Column(TIMESTAMP)
    gender = Column(Enum(Gender))
    phone_number = Column(VARCHAR)
    personal_email_id = Column(VARCHAR)
    is_department_head = Column(BOOLEAN)
    department = relationship("Department")
    application = relationship("Application")

    # application = relationship("Application")


class Department(Base):
    __tablename__ = "departments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(VARCHAR)
    employee = relationship("Employee")


class Application(Base):
    __tablename__ = "applications"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"))
    application_type = Column(Enum(Application_type))
    from_date = Column(TIMESTAMP)
    to_date = Column(TIMESTAMP)
    subject = Column(VARCHAR)
    reason = Column(VARCHAR)
    status = Column(Enum(Status))
    balance_before_approval = Column(INTEGER)
    balance_after_approval = Column(INTEGER)
    employee = relationship("Employee")


class Language(Base):
    __tablename__ = "languages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(VARCHAR)


class EmployeeLanguage(Base):
    __tablename__ = "employeeslanguages"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.id"),
    )
    language_id = Column(
        UUID(as_uuid=True),
        ForeignKey("languages.id"),
    )
