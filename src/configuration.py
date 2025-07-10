from typing import Optional
from pydantic import BaseModel, Field, ValidationError, model_validator
from keboola.component.exceptions import UserException
from datetime import datetime

ALLOWED_DATETIME_FORMATS = [
    "%Y-%m-%d",
    "%Y-%m-%d_%H-%M-%S",
    "%Y%m%d",
    "%Y%m%d_%H%M%S",
    "{epoch}",
]

DATETIME_FORMAT_DISPLAY_NAMES = {
    "%Y-%m-%d": "YYYY-MM-DD",
    "%Y-%m-%d_%H-%M-%S": "YYYY-MM-DD_HH-mm-ss",
    "%Y%m%d": "YYYYMMDD",
    "%Y%m%d_%H%M%S": "YYYYMMDD_HHMMSS",
    "{epoch}": "Timestamp (Epoch)"
}

class Authorization(BaseModel):
    """
    Authorization section for WebDAV.
    """
    webdav_hostname: str = Field(
        ...,
        title="WebDAV Hostname",
        description="URL of your WebDAV server, e.g. https://webdav.example.com."
    )
    username: str = Field(
        ...,
        title="WebDAV Username",
        description="Your WebDAV login username."
    )
    password: str = Field(
        ...,
        alias="#password",
        title="WebDAV Password",
        description="Your WebDAV login password."
    )

    @model_validator(mode="after")
    def validate_hostname(self) -> "Authorization":
        if not self.webdav_hostname.strip():
            raise ValueError("webdav_hostname cannot be empty.")
        return self


class SyncOptions(BaseModel):
    remote_path: str = Field(
        "/",
        title="Remote Path",
        description="Path on the WebDAV server where files will be uploaded, e.g. /backup/files/"
    )
    append_datetime: bool = Field(
        False,
        title="Append Datetime",
        description="If true, a datetime suffix will be appended to the remote path."
    )
    datetime_format: Optional[str] = Field(
        "%Y-%m-%d",
        title="Datetime Format",
        description=(
            "Datetime format string to append to the remote path. "
            f"Allowed values: {', '.join(ALLOWED_DATETIME_FORMATS)}"
        )
    )

    @model_validator(mode="after")
    def check_datetime(self) -> "SyncOptions":
        if self.append_datetime:
            if not self.datetime_format:
                raise ValueError(
                    "datetime_format must be provided if append_datetime is enabled."
                )
            if self.datetime_format not in ALLOWED_DATETIME_FORMATS:
                allowed_str = ", ".join(ALLOWED_DATETIME_FORMATS)
                raise ValueError(
                    f"datetime_format '{self.datetime_format}' is invalid. "
                    f"Allowed values: {allowed_str}"
                )
        return self

    @property
    def datetime_suffix(self) -> str:
        """
        Return the datetime suffix string, or empty string if disabled.
        """
        if not self.append_datetime:
            return ""
        fmt = self.datetime_format
        if fmt == "{epoch}":
            return str(int(datetime.now().timestamp()))
        else:
            return datetime.now().strftime(fmt)


class Parameters(BaseModel):
    """
    Root parameters for WebDAV writer.
    """
    authorization: Authorization
    sync_options: SyncOptions


class Configuration(BaseModel):
    parameters: Parameters
    action: Optional[str] = Field(default="run")

    def __init__(self, **data):
        try:
            super().__init__(**data)
        except ValidationError as e:
            error_messages = [
                f"{'.'.join(str(loc) for loc in err['loc'])}: {err['msg']}"
                for err in e.errors()
            ]
            raise UserException(
                f"Configuration validation error: {', '.join(error_messages)}"
            )

    @property
    def auth(self) -> Authorization:
        return self.parameters.authorization

    @property
    def sync(self) -> SyncOptions:
        return self.parameters.sync_options

    @property
    def datetime_suffix(self) -> str:
        return self.sync.datetime_suffix
