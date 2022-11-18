import uuid
from datetime import date

from pydantic import BaseModel

from models import Application_type, Gender, Status

# birth = date.today().strftime("%d-%b-%Y")


class EmployeeCreateRequest(BaseModel):
    first_name: str
    last_name: str | None
    dob: date
    gender: Gender
    phone_number: str
    personal_email_id: str
    is_department_head: bool

    class Config:
        orm_mode = True


class EmployeeResponse(BaseModel):
    id: uuid.UUID
    department_id: uuid.UUID | None
    first_name: str | None
    last_name: str | None
    dob: date | None
    gender: Gender | None
    phone_number: str | None
    personal_email_id: str | None
    is_department_head: bool | None

    class Config:
        orm_mode = True


class EmployeeUpdateRequest(BaseModel):
    first_name: str | None
    last_name: str | None
    department_id: str | None
    dob: date | None
    gender: Gender | None
    phone_number: str | None
    personal_email_id: str | None
    is_department_head: bool | None

    class Config:
        orm_mode = True


# ********************* Working on Department table *********************


class DepartmentCreateRequest(BaseModel):
    name: str

    class Config:
        orm_mode = True


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    name: str

    class Config:
        orm_mode = True


class DepartmentUpdateRequest(BaseModel):
    name: str | None

    class Config:
        orm_mode = True


# *********************** Working on Application Table  **************


class CreateApplicationRequest(BaseModel):
    application_type: Application_type
    # employee_id: uuid.UUID | None
    from_date: date
    to_date: date
    subject: str
    reason: str
    status: Status
    balance_before_approval: int
    balance_after_approval: int

    class Config:
        orm_mode = True


class UpdateApplicationRequest(BaseModel):
    application_type: Application_type | None
    # employee_id: uuid.UUID | None
    from_date: date | None
    to_date: date | None
    subject: str | None
    reason: str | None
    balance_before_approval: int | None
    balance_after_approval: int | None

    class Config:
        orm_mode = True


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID | None
    from_date: date | None
    to_date: date | None
    subject: str | None
    reason: str | None
    balance_before_approval: int | None
    balance_after_approval: int | None

    class Config:
        orm_mode = True
