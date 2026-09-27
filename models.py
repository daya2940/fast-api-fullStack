from datetime import datetime, timezone

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

class User(Base):
	__tablename__ = "users"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	userName: Mapped[str] = mapped_column(String(100))
	description: Mapped[str] = mapped_column(Text)
	email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
	image_file: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
	image_path: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
	posts: Mapped[list["Post"]] = relationship(back_populates="author")
	
@property
def def_image() -> str:
	return "default.jpg"


class Post(Base):
	__tablename__ = "posts"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	title: Mapped[str] = mapped_column(String(100))
	content: Mapped[str] = mapped_column(Text)
	published: Mapped[bool] = mapped_column(Boolean, default=True)
	image: Mapped[str] = mapped_column(String(255), default=def_image)
	date_posted: Mapped[str] = mapped_column(
		String(40), default=lambda: datetime.now(timezone.utc).isoformat()
	)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

	author: Mapped[User] = relationship(back_populates="posts")
