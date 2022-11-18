import logging
import uuid
from logging.config import dictConfig
from typing import List

from fastapi import Depends, FastAPI, HTTPException

# from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Query, Session

from db import Base, SessionLocal, engin
from models import Application, Base, Department, Employee, Gender, Status
from validators import *

Base.metadata.create_all(bind=engin)

formate_time = "%(asctime)s -- %(message)s"
logging.basicConfig(
    filename="logging/employee_leave.log",
    level=logging.DEBUG,
    format=formate_time,
)
log = logging.getLogger(__name__)
log.debug("This is my debug file.")
app = FastAPI(debug=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Getting all employees from employees table
@app.get(
    "/employee/",
    tags=["Employees"],
    response_model=List[EmployeeResponse],
)
async def all_employees(
    gender: Gender | None = None,
    email: str | None = None,
    department_id: uuid.UUID | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    """_Description:_

        This API will fetch employee from employees table,
        according to provided options (Optional).

    Argument:

        Department ID --> Optional, Format --> UUID.
        Gender --> Optional.
        Email --> Optional.
        Search --> Optional, Description --> Search via first name.

    """
    query = db.query(Employee)
    if gender:
        query = query.filter(Employee.gender == gender)
    if email:
        query = query.filter(Employee.personal_email_id == email)
    if search:
        query = query.filter(Employee.first_name.ilike(f"%{search}%"))
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    all_data = query.all()
    return all_data


# Getting Emloyee by employe ID
@app.get(
    "/employee/{emp_id}/",
    response_model=EmployeeResponse,
    tags=["Employees"],
)
async def employee_by_id(
    emp_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Description:

        This API will fetch employee according to provided employee id,

    Argument:

        Employee ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Employee not found.
    """
    query = db.query(Employee).where(Employee.id == emp_id).first()
    if not query:
        log.exception("Employee Not found")
        raise HTTPException(status_code=404, detail="Employee not found. ")
    return query


# Inserting employee in employees table
@app.post("/employee/", response_model=EmployeeResponse, tags=["Employees"])
async def create_employee(
    employee: EmployeeCreateRequest,
    db: Session = Depends(get_db),
):
    """
    Description:

        This API will create new employee, if moblie number or email id
        already exist than admin can't.

    Raises:

        HTTPException: Phone number or email id already exist.
    """
    phone = db.query(Employee).filter(Employee.phone_number == employee.phone_number).first()
    if phone:
        log.exception("Phone number already exist. ")
        raise HTTPException(status_code=403, detail="Phone number already exist. ")

    email = (
        db.query(Employee).filter(Employee.personal_email_id == employee.personal_email_id).first()
    )
    if email:
        log.debug("Email id already exist. ")
        raise HTTPException(status_code=403, detail="Email id already exist. ")

    try:
        emp_data = Employee(**employee.dict())
        db.add(emp_data)
        db.commit()
        db.refresh(emp_data)

        return emp_data
    except Exception as error:
        return error


# Update Employee by employee ID
@app.patch(
    "/employe/{emp_id}/",
    response_model=EmployeeResponse,
    tags=["Employees"],
)
async def update_employe_by_id(
    emp_id: uuid.UUID,
    user_input: EmployeeUpdateRequest,
    db: Session = Depends(get_db),
):
    """_Description:_

        This API will update employee according to provided employee id,
        if employee wants to change moblie number or email id than
        employee can't update this.

    Argument:

        Employee ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Phone number or email id already exist.
    """
    phone = db.query(Employee).filter(Employee.phone_number == user_input.phone_number).first()
    if phone:
        log.debug("Phone number already exist. ")
        raise HTTPException(status_code=403, detail="Phone number already exist.")
    email = db.query(Employee).filter(Employee.phone_number == user_input.phone_number).first()
    if email:
        log.debug("Email id already exist. ")
        raise HTTPException(status_code=403, detail="Email id already exist. ")
    db_id = db.query(Employee).where(Employee.id == emp_id).first()
    try:
        if not db_id:
            log.error("Employe not found. ")
            raise HTTPException(status_code=404, detail="Employee not found. ")
        update_data = user_input.dict(exclude_unset=True)
        for field in db_id.__dict__:
            if field in update_data:
                setattr(db_id, field, update_data[field])
        db.add(db_id)
        db.commit()
        db.refresh(db_id)
        return db_id
    except Exception as error:
        return error


# Delete employee
@app.delete("/employee/{emp_id}/", tags=["Employees"])
async def delete_employee_by_id(
    emp_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """_Description:_

        This API will delete employee according to provided employee id.

    Argument:

        Employee ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Employee not found.
    """
    delete_employee = db.query(Employee).where(Employee.id == emp_id).first()
    if not delete_employee:
        log.error("Employee not found. ")
        raise HTTPException(status_code=404, detail="Employe not found. ")
    try:
        db.delete(delete_employee)
        db.commit()
        log.info("Employee deleted successfully. ")
        return {"Message": f"Employe {delete_employee.id} deleted successfully."}
    except Exception as error:
        return error


# ********************* Working on Department table ****************


@app.get(
    "/department/",
    tags=["Departments"],
    response_model=List[DepartmentResponse],
)
async def all_department(
    db: Session = Depends(get_db),
):
    """
    Description:

        This API will fetch all department from department table.

    """
    department = db.query(Department).all()
    return department


@app.post(
    "/department/",
    response_model=DepartmentResponse,
    tags=["Departments"],
)
async def create_department(
    department: DepartmentCreateRequest,
    db: Session = Depends(get_db),
):
    """
       Description:

           This API will create new department if department is already
           exist then message will arise already exists.

    Raises:

           HTTPException: Department already exist.
    """
    duplicate_department = db.query(Department).filter(Department.name == department.name).first()
    if duplicate_department:
        log.debug(f"{department.name} already exist. ")
        raise HTTPException(status_code=403, detail=f"{department.name} already exist. ")
    add_dprt = Department(**department.dict())
    try:
        db.add(add_dprt)
        db.commit()
        db.refresh(add_dprt)
        return add_dprt
    except Exception as error:
        return error


@app.get(
    "/department/{dpt_id}/",
    response_model=DepartmentResponse,
    tags=["Departments"],
)
async def department_by_id(
    dpt_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """
    Description:

        This API will fetch department according to provided department id.

    Argument:

    Department ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Department not found.
    """
    dpt_data = db.query(Department).where(Department.id == dpt_id).first()
    if not dpt_data:
        log.debug("Department not found. ")
        raise HTTPException(status_code=404, detail="Department not found. ")
    return dpt_data


@app.patch(
    "/department/{dpt_id}",
    response_model=DepartmentResponse,
    tags=["Departments"],
)
async def update_department_by_id(
    dpt_id: uuid.UUID,
    user_input: DepartmentUpdateRequest,
    db: Session = Depends(get_db),
):
    """
    Description:

        This API will update department according to provided department id.

    Argument:

    Department ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Department not found.
    """
    db_id = db.query(Department).where(Department.id == dpt_id).first()
    try:
        if not db_id:
            log.debug("Department not found. ")
            raise HTTPException(status_code=404, detail="Department not found. ")
        update_department = user_input.dict(exclude_unset=True)
        for field in update_department:
            if field in update_department:
                setattr(db_id, field, update_department[field])
        db.add(db_id)
        db.commit()
        db.refresh(db_id)
        return db_id
    except Exception as error:
        return error


@app.delete("/department/{dpt_id}", tags=["Departments"])
async def delete_department(
    dpt_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """_Description:_

        This API will delete department according to provided department id.

    Argument:

    Department ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Department not found.
    """
    DataInDpt = db.query(Department).where(Department.id == dpt_id).first()
    if not DataInDpt:
        log.debug("Department not found. ")
        raise HTTPException(status_code=404, detail="Department not found. ")
    try:
        db.delete(DataInDpt)
        db.commit()
        log.debug("Department deleted successfully. ")
        return {"Message": f"{DataInDpt.name} deleted successfully. "}
    except Exception as error:
        return error


# ******************** Working on Application Table ***********************


@app.get(
    "/application/",
    tags=["Applications"],
    response_model=List[ApplicationResponse],
)
async def all_applications(
    status: Status | None = None,
    application_type: Application_type | None = None,
    from_date: date | None = None,
    to_date: date | None = None,
    search: str | None = None,
    application_by_employee_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):

    """_Description:_

        This API will fetch all data from application table according to user requirements'.

    Arguments:

        Status --> Optional, .
        Application Type --> Optional.
        From Date --> Optional, Format --> yyyy-mm-dd.
        To Date --> Optional, Format --> yyyy-mm-dd.
        Search --> Optional: (Admin can search by reason).
        Application By Employee ID --> Optional, Format --> UUID.


    """
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    if application_type:
        query = query.filter(Application.application_type == application_type)
    if from_date:
        query = query.filter(Application.from_date == from_date)
    if to_date:
        query = query.filter(Application.to_date == to_date)
    if search:
        query = query.filter(Application.reason.ilike(f"%{search}%"))
    if application_by_employee_id:
        query = query.filter(Application.employee_id == application_by_employee_id)

    application_data = query.all()
    return application_data


@app.post(
    "/application/",
    tags=["Applications"],
    response_model=ApplicationResponse,
)
async def create_application(
    emp_application: CreateApplicationRequest,
    db: Session = Depends(get_db),
):
    """_Description:_

        This API will create new application, if someone have already taken Work From home
        then other employee can't take Work from home from the same department in same time period.

    Raises:

        Message: Work From Home already taken from same department

    """
    query = (
        db.query(Application)
        .join(Employee, Department)
        .filter(Application.application_type == emp_application.application_type)
        .filter(Department.id == Employee.department_id)
        .filter(Application.from_date == emp_application.from_date)
        # .filter(Application.to_date == emp_application.to_date)
        .first()
    )
    if query:
        log.info("Work From Home already taken from the same department. ")
        raise HTTPException(
            status_code=403,
            detail="Work From Home already taken from the same department",
        )
    try:
        application_data = Application(**emp_application.dict())
        db.add(application_data)
        db.commit()
        db.refresh(application_data)
        return application_data
    except Exception as error:
        return error


@app.get(
    "/application/{application_id}/",
    response_model=ApplicationResponse,
    tags=["Applications"],
)
async def application_by_id(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """_Description_

        This API will fetch data from application table according to provided application id.

    Argument:

        Application ID --> mandatory, Format --> UUID

    Raises:

        HTTPException: Application not found.
    """
    query = db.query(Application).where(Application.id == application_id).first()
    if not query:
        log.debug("Application not found. ")
        raise HTTPException(status_code=404, detail="Application not found. ")
    return query


@app.patch(
    "/application/{application_id}/",
    response_model=ApplicationResponse,
    tags=["Applications"],
)
async def update_application_by_id(
    application_id: uuid.UUID,
    user_input: UpdateApplicationRequest,
    db: Session = Depends(get_db),
):
    """_Description:_

        This API will update application according to provided application id.

    Argument:

    Application ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Application not found.
    """
    query = db.query(Application).where(Application.id == application_id).first()
    try:
        if not query:
            log.debug("Application not found. ")
            raise HTTPException(status_code=404, detail="Application not found. ")
        update_data = user_input.dict(exclude_unset=True)
        for field in query.__dict__:
            if field in update_data:
                setattr(query, field, update_data[field])
        db.add(query)
        db.commit()
        db.refresh(query)
        return query
    except Exception as error:
        return error


@app.delete("/application/{application_id}/", tags=["Applications"])
async def delete_application_by_id(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
):
    """_Description:_

        This API will delete application according to provided application id.

    Argument:

    Application ID --> Mandaotry, Format --> UUID

    Raises:
        HTTPException: Application not found.
    """
    query = db.query(Application).where(Application.id == application_id).first()
    if not query:
        log.debug("Application not found. ")
        raise HTTPException(status_code=404, detail="Application not found. ")
    try:
        db.delete(query)
        db.commit()
        log.info(f"Application {query.id} deleted successfully. ")
        return {"message": f"Application {query.id} deleted successfully. "}
    except Exception as error:
        return error
