from sqlalchemy import (
    Column, Integer, String, Text, Enum, ForeignKey,
    TIMESTAMP, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Device(Base):
    __tablename__ = "Devices"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    device_name = Column(String(100), nullable=False)
    created_at  = Column(TIMESTAMP, server_default=func.now())

    errors = relationship("Error", back_populates="device")
    os_list = relationship("OperatingSystem", back_populates="device")


class OperatingSystem(Base):
    __tablename__ = "OperatingSystems"
    id        = Column(Integer, primary_key=True, autoincrement=True)
    os_name   = Column(String(100), nullable=False)
    device_id = Column(Integer, ForeignKey("Devices.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP, server_default=func.now())

    device = relationship("Device", back_populates="os_list")
    errors = relationship("Error", back_populates="os")


class ErrorCategory(Base):
    __tablename__ = "ErrorCategories"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(100), nullable=False)
    description   = Column(Text)
    created_at    = Column(TIMESTAMP, server_default=func.now())

    errors = relationship("Error", back_populates="category")


class Error(Base):
    __tablename__ = "Errors"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    error_code  = Column(String(50))
    error_name  = Column(String(200), nullable=False)
    description = Column(Text)
    solution    = Column(Text)
    video_link  = Column(String(500))
    device_id   = Column(Integer, ForeignKey("Devices.id", ondelete="SET NULL"))
    os_id       = Column(Integer, ForeignKey("OperatingSystems.id", ondelete="SET NULL"))
    category_id = Column(Integer, ForeignKey("ErrorCategories.id", ondelete="SET NULL"))
    severity    = Column(Enum("low", "medium", "high", "critical"), default="medium")
    created_at  = Column(TIMESTAMP, server_default=func.now())

    device   = relationship("Device",         back_populates="errors")
    os       = relationship("OperatingSystem", back_populates="errors")
    category = relationship("ErrorCategory",   back_populates="errors")
    error_scripts = relationship("ErrorScript", back_populates="error")


class Script(Base):
    __tablename__ = "Scripts"
    id             = Column(Integer, primary_key=True, autoincrement=True)
    script_name    = Column(String(200), nullable=False)
    description    = Column(Text)
    file_path      = Column(String(500))
    script_type    = Column(Enum(".bat", ".py", ".sh", ".ps1"), nullable=False)
    compatible_os  = Column(String(200))
    download_count = Column(Integer, default=0)
    created_at     = Column(TIMESTAMP, server_default=func.now())

    error_scripts = relationship("ErrorScript", back_populates="script")


class Guide(Base):
    __tablename__ = "Guides"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    title       = Column(String(300), nullable=False)
    content     = Column(Text)
    device_type = Column(String(100))
    os_type     = Column(String(100))
    category    = Column(String(100))
    thumbnail   = Column(String(500))
    view_count  = Column(Integer, default=0)
    created_at  = Column(TIMESTAMP, server_default=func.now())


class ErrorScript(Base):
    __tablename__ = "Error_Scripts"
    id        = Column(Integer, primary_key=True, autoincrement=True)
    error_id  = Column(Integer, ForeignKey("Errors.id",   ondelete="CASCADE"), nullable=False)
    script_id = Column(Integer, ForeignKey("Scripts.id",  ondelete="CASCADE"), nullable=False)
    note      = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    __table_args__ = (UniqueConstraint("error_id", "script_id"),)

    error  = relationship("Error",  back_populates="error_scripts")
    script = relationship("Script", back_populates="error_scripts")
