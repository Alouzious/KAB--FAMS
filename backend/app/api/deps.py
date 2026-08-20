from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*allowed_roles: UserRole):
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to perform this action")
        return current_user
    return role_checker


def require_eligible_student(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.STUDENT:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Student access only")
    if not current_user.student_profile or not current_user.student_profile.is_eligible_for_fa:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "You are not yet eligible for field attachment based on your current year of study",
        )
    return current_user


def get_faculty_scope(current_user: User = Depends(require_role(UserRole.FACULTY_ADMIN))) -> str:
    """Returns the faculty_id a faculty_admin is scoped to."""
    return str(current_user.admin_profile.faculty_id)


def get_department_scope(current_user: User = Depends(require_role(UserRole.DEPARTMENT_ADMIN))) -> str:
    """Returns the department_id a department_admin is scoped to."""
    return str(current_user.admin_profile.department_id)