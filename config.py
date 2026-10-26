from pydantic import AliasChoices, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    database_url: str
    secret_key: SecretStr
    algorithm: str='HS256'
    access_token_expire_minutes: int = 30
    reset_token_expire_minutes: int = 60  # 1 day
    #email settings
    email_host: str = Field(
        default="localhost",
        validation_alias=AliasChoices("email_host", "mail_server"),
    )
    email_port: int = Field(
        default=587,
        validation_alias=AliasChoices("email_port", "mail_port"),
    )
    email_username: str = Field(
        default="",
        validation_alias=AliasChoices("email_username", "mail_username"),
    )
    email_password: SecretStr = Field(
        default=SecretStr(""),
        validation_alias=AliasChoices("email_password", "mail_password"),
    )
    mail_use_tls: bool=True
    mail_from: str=""
    frontend_url: str="http://localhost:3000"

    max_upload_size: int = 5 * 1024 * 1024  # 5 MB

settings = Settings() #Loaded settings from .env file and environment variables