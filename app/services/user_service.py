from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.user import User


def list_users(db: Session, keyword: str | None = None, is_active: bool | None = None):
    stmt = select(User)
    if keyword:
        stmt = stmt.where(
            or_(User.email.ilike(f"%{keyword}%"), User.full_name.ilike(f"%{keyword}%"))
        )
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    users = db.scalars(stmt)
    return users
