import uuid
from typing import List

from fastapi import Depends, FastAPI, HTTPException

# from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Query, Session

from db import Base, SessionLocal, engin
from models import Application, Base, Department, Employee, Gender, Status
from validators import *

Base.metadata.create_all(bind=engin)

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
    query = db.query(Employee).where(Employee.id == emp_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Employee not found. ")
    return query


# Inserting employee in employees table
@app.post("/employee/", response_model=EmployeeResponse, tags=["Employees"])
async def create_employee(
    employee: EmployeeCreateRequest,
    db: Session = Depends(get_db),
):
    phone = db.query(Employee).filter(Employee.phone_number == employee.phone_number).first()
    if phone:
        raise HTTPException(status_code=403, detail="Phone number already exist. ")

    email = (
        db.query(Employee).filter(Employee.personal_email_id == employee.personal_email_id).first()
    )
    if email:
        raise HTTPException(status_code=403, detail="Email id already exist")

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
    phone = db.query(Employee).filter(Employee.phone_number == user_input.phone_number).first()
    if phone:
        raise HTTPException(status_code=403, detail="Phone number already exist.")
    email = db.query(Employee).filter(Employee.phone_number == user_input.phone_number).first()
    if email:
        raise HTTPException(status_code=403, detail="Email id already exist. ")
    db_id = db.query(Employee).where(Employee.id == emp_id).first()
    try:
        if not db_id:
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
    delete_employee = db.query(Employee).where(Employee.id == emp_id).first()
    if not delete_employee:
        raise HTTPException(status_code=404, detail="Employe not found. ")
    try:
        db.delete(delete_employee)
        db.commit()
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
    duplicate_department = db.query(Department).filter(Department.name == department.name).first()
    if duplicate_department:
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
    dpt_data = db.query(Department).where(Department.id == dpt_id).first()
    if not dpt_data:
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
    db_id = db.query(Department).where(Department.id == dpt_id).first()
    try:
        if not db_id:
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
    DataInDpt = db.query(Department).where(Department.id == dpt_id).first()
    if not DataInDpt:
        raise HTTPException(status_code=404, detail="Department not found. ")
    try:
        db.delete(DataInDpt)
        db.commit()
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
    search: str | None = None,
    application_by_employee_id: uuid.UUID | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Application)
    if status:
        query = query.filter(Application.status == status)
    if application_type:
        query = query.filter(Application.application_type == application_type)
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
    apl_typ = (
        db.query(Application)
        .filter(Application.application_type == emp_application.application_type)
        .first(),
    )
    if apl_typ:
        raise HTTPException(
            status_code=403,
            detail=f"{apl_typ.id} already taken {apl_typ.application_type}",
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
    query = db.query(Application).where(Application.id == application_id).first()
    if not query:
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
    query = db.query(Application).where(Application.id == application_id).first()
    try:
        if not query:
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
    query = db.query(Application).where(Application.id == application_id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Application not found. ")
    try:
        db.delete(query)
        db.commit()
        return {"message": f"Application {query.id} deleted successfully. "}
    except Exception as error:
        return error
