from datetime import UTC, datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config import settings
from database import Base


class User(Base):
	__tablename__ = "users"

	user_id: Mapped[int] = mapped_column("id", Integer, primary_key=True, index=True)
	userName: Mapped[str] = mapped_column(String(100))
	description: Mapped[str] = mapped_column(Text)
	email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
	password_hash: Mapped[str] = mapped_column(String(255),nullable=False)
	image_file: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
	image_path: Mapped[str | None] = mapped_column(String(255), nullable=True, default=None)
	posts: Mapped[list["Post"]] = relationship(back_populates="author",cascade="all, delete-orphan", passive_deletes=True) # cascade="all, 
	#delete-orphan" ensures that when a User is deleted, all associated Post objects are also deleted. passive_deletes=True allows the database 
	#to handle the deletion of related Post objects without loading them into memory.
	likes: Mapped[int] = mapped_column(Integer, default=0,server_default="0")  # New column to store the number of likes for the user
    # The server_default="0" ensures that if no value is provided during insertion, the default value will be 0 on the server side. 
	# This is useful for ensuring that the likes column always has a valid integer value, even if not explicitly set during user creation.
	
def def_image(self) -> str:
	if self.image_file:
		 return f"https://{settings.s3_bucket_name}.s3.{settings.s3_region_name}.amazonaws.com/{self.image_file}"
 # Return the default image URL if no image is set


class PasswordResetToken(Base):
	__tablename__ = "password_reset_tokens"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
	token: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
	expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Post(Base):
	__tablename__ = "posts"

	post_id: Mapped[int] = mapped_column("id", Integer, primary_key=True, index=True)
	title: Mapped[str] = mapped_column(String(100))
	content: Mapped[str] = mapped_column(Text)
	published: Mapped[bool] = mapped_column(Boolean, default=True)
	image: Mapped[str] = mapped_column(String(255), default=def_image)
	date_posted: Mapped[str] = mapped_column(
		String(40), default=lambda: datetime.now(UTC).isoformat()
	)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

	author: Mapped[User] = relationship(back_populates="posts")
