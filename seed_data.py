import os
import sys
from datetime import UTC, datetime, timedelta

from sqlalchemy import select

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import hash_password
from app.db.database import SessionLocal, engine
from app.models.base import Base
from app.models.project import Project
from app.models.project_member import ProjectMember, ProjectMemberRole
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.user import User, UserRole


def seed():
    print("Khởi tạo database session...")
    print("Xóa và tạo lại các bảng trong database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()

    try:
        print("Đang tạo người dùng (Users)...")
        users_data = [
            User(
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                full_name="Quản trị viên",
                role=UserRole.ADMIN,
                is_active=True,
            ),
            User(
                email="user1@example.com",
                password_hash=hash_password("user123"),
                full_name="Người dùng 1",
                role=UserRole.USER,
                is_active=True,
            ),
            User(
                email="user2@example.com",
                password_hash=hash_password("user123"),
                full_name="Người dùng 2",
                role=UserRole.USER,
                is_active=True,
            ),
            User(
                email="user3@example.com",
                password_hash=hash_password("user123"),
                full_name="Người dùng 3 (Để test add member)",
                role=UserRole.USER,
                is_active=True,
            ),
        ]
        db.add_all(users_data)
        db.commit()

        admin = db.scalar(select(User).where(User.email == "admin@example.com"))
        user1 = db.scalar(select(User).where(User.email == "user1@example.com"))
        user2 = db.scalar(select(User).where(User.email == "user2@example.com"))
        user3 = db.scalar(select(User).where(User.email == "user3@example.com"))

        if not admin or not user1 or not user2 or not user3:
            raise ValueError("Không tìm thấy user vừa tạo trong database")

        print("Đang tạo dự án (Projects)...")
        projects_data = [
            Project(
                name="Dự án Alpha",
                description="Hệ thống quản lý công việc và dự án nội bộ",
                owner_id=admin.id,
            ),
            Project(
                name="Dự án Beta",
                description="Ứng dụng di động cho khách hàng",
                owner_id=user1.id,
            ),
        ]
        db.add_all(projects_data)
        db.commit()

        project_alpha = db.scalar(select(Project).where(Project.name == "Dự án Alpha"))
        project_beta = db.scalar(select(Project).where(Project.name == "Dự án Beta"))

        if not project_alpha or not project_beta:
            raise ValueError("Không tìm thấy project vừa tạo trong database")

        print("Đang thêm thành viên vào dự án (Project Members)...")
        members_data = [
            ProjectMember(
                project_id=project_alpha.id,
                user_id=admin.id,
                role=ProjectMemberRole.OWNER,
            ),
            ProjectMember(
                project_id=project_alpha.id,
                user_id=user1.id,
                role=ProjectMemberRole.MEMBER,
            ),
            ProjectMember(
                project_id=project_alpha.id,
                user_id=user2.id,
                role=ProjectMemberRole.MEMBER,
            ),
            ProjectMember(
                project_id=project_beta.id,
                user_id=user1.id,
                role=ProjectMemberRole.OWNER,
            ),
            ProjectMember(
                project_id=project_beta.id,
                user_id=user2.id,
                role=ProjectMemberRole.MEMBER,
            ),
        ]
        db.add_all(members_data)
        db.commit()

        print("Đang tạo công việc (Tasks)...")
        now = datetime.now(UTC)
        tasks_data = [
            Task(
                project_id=project_alpha.id,
                title="Thiết kế Database",
                description="Thiết kế các bảng và quan hệ cho hệ thống",
                assignee_id=admin.id,
                status=TaskStatus.DONE,
                priority=TaskPriority.HIGH,
                due_date=now - timedelta(days=2),
            ),
            Task(
                project_id=project_alpha.id,
                title="Phát triển API Xác thực",
                description="Code chức năng đăng nhập, đăng ký sử dụng JWT",
                assignee_id=user1.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                due_date=now + timedelta(days=5),
            ),
            Task(
                project_id=project_alpha.id,
                title="Viết Test cho API",
                description="Sử dụng pytest để test các endpoint",
                assignee_id=user2.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                due_date=now + timedelta(days=7),
            ),
            Task(
                project_id=project_beta.id,
                title="Thiết kế UI/UX trên Figma",
                description="Vẽ wireframe và mockup cho ứng dụng di động",
                assignee_id=user1.id,
                status=TaskStatus.IN_PROGRESS,
                priority=TaskPriority.HIGH,
                due_date=now + timedelta(days=3),
            ),
            Task(
                project_id=project_beta.id,
                title="Nghiên cứu công nghệ React Native",
                description="Tìm hiểu xem có phù hợp để làm cross-platform không",
                assignee_id=user2.id,
                status=TaskStatus.TODO,
                priority=TaskPriority.LOW,
                due_date=now + timedelta(days=10),
            ),
        ]
        db.add_all(tasks_data)
        db.commit()

        print("✅ Seed dữ liệu thành công!")

    except Exception as e:  # noqa: BLE001
        db.rollback()
        print(f"❌ Có lỗi xảy ra trong quá trình seed dữ liệu: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
