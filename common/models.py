from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    func,
    JSON,
    Float,
    ForeignKeyConstraint,
    BigInteger,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True)
    date_write = Column(DateTime, default=datetime.now)
    name = Column(String(255))
    price = Column(Float)
    labor_cost = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    responsible_user_id = Column(Integer)
    pipeline_id = Column(Integer, ForeignKey("pipelines.id"))
    status_id = Column(Integer)
    loss_reason_id = Column(Integer)
    updated_by = Column(Integer)
    custom_fields_values = Column(JSON)

    pipeline = relationship("Pipeline", back_populates="leads")

    LABEL = "leads"

    def __repr__(self):
        return f"<Lead(id={self.id}, name={self.name}, price={self.price})>"

    def fill(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.price = data["price"]
        self.created_at = datetime.fromtimestamp(data["created_at"])
        self.updated_at = datetime.fromtimestamp(data["updated_at"])
        self.responsible_user_id = data["responsible_user_id"]
        self.pipeline_id = data["pipeline_id"]
        self.status_id = data["status_id"]
        self.loss_reason_id = data["loss_reason_id"]
        self.updated_by = data["updated_by"]
        self.labor_cost = data["labor_cost"]
        self.custom_fields_values = data["custom_fields_values"]

    def need_update(self, data, if_force_rewrite=False):
        return if_force_rewrite or self.updated_at != datetime.fromtimestamp(
            data["updated_at"]
        )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))

    LABEL = "users"

    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.name})>"

    def fill(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.email = data["email"]

    def need_update(self, data, if_force_rewrite=False):
        return if_force_rewrite


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    responsible_user_id = Column(Integer)
    group_id = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    is_deleted = Column(Boolean)
    is_unsorted = Column(Boolean)
    account_id = Column(Integer)
    custom_fields_values = Column(JSON)

    LABEL = "contacts"

    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.name})>"

    def fill(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.first_name = data["first_name"]
        self.last_name = data["last_name"]
        self.responsible_user_id = data["responsible_user_id"]
        self.group_id = data["group_id"]
        self.created_at = datetime.fromtimestamp(data["created_at"])
        self.updated_at = datetime.fromtimestamp(data["updated_at"])
        self.is_deleted = data["is_deleted"]
        self.is_unsorted = data["is_unsorted"]
        self.account_id = data["account_id"]
        self.custom_fields_values = data["custom_fields_values"]

    def need_update(self, data, if_force_rewrite=False):
        return if_force_rewrite or self.updated_at != datetime.fromtimestamp(
            data["updated_at"]
        )


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    custom_fields_values = Column(JSON)
    responsible_user_id = Column(Integer)
    group_id = Column(Integer)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    account_id = Column(Integer)
    is_deleted = Column(Boolean)
    closest_task_at = Column(Integer)

    LABEL = "companies"

    def fill(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.responsible_user_id = data["responsible_user_id"]
        self.group_id = data["group_id"]
        self.created_at = datetime.fromtimestamp(data["created_at"])
        self.updated_at = datetime.fromtimestamp(data["updated_at"])
        self.updated_by = data["updated_by"]
        self.created_by = data["created_by"]
        self.is_deleted = data["is_deleted"]
        self.account_id = data["account_id"]
        self.custom_fields_values = data["custom_fields_values"]

    def need_update(self, data, if_force_rewrite=False):
        return if_force_rewrite or self.updated_at != datetime.fromtimestamp(
            data["updated_at"]
        )

    def __repr__(self):
        return f"<Company(id={self.id}, name={self.name})>"


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    is_main = Column(Boolean)
    is_archive = Column(Boolean)
    account_id = Column(Integer)
    sort = Column(Integer)

    leads = relationship("Lead", back_populates="pipeline")
    statuses = relationship("Status", back_populates="pipeline")

    LABEL = "pipelines"

    def fill(self, data):
        self.id = data["id"]
        self.name = data["name"]
        self.is_main = data.get("is_main", 0)
        self.is_archive = data.get("is_archive", 0)
        self.account_id = data["account_id"]
        self.sort = data["sort"]

    def need_update(self, data, if_force_rewrite=False):
        return True

    def __repr__(self):
        return f"<Pipeline(id={self.id}, name={self.name})>"


class Status(Base):
    __tablename__ = "statuses"
    __table_args__ = (
        ForeignKeyConstraint(
            ["pipeline_id"],
            ["pipelines.id"],
            name="fk_status_pipeline",
        ),
    )
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    pipeline_id = Column(Integer, primary_key=True)
    type = Column(Integer)
    account_id = Column(Integer)
    sort = Column(Integer)

    pipeline = relationship("Pipeline", back_populates="statuses")

    LABEL = "statuses"

    def fill(self, data):
        self.id = data["id"]
        self.name = data["name"]
        # self.pipeline_id = data.get("pipeline_id", 0)
        self.pipeline_id = data["pipeline_id"]
        self.type = data.get("type", 0)
        self.account_id = data["account_id"]
        self.sort = data["sort"]

    def need_update(self, data, if_force_rewrite=False):
        return True

    def __repr__(self):
        return f"<Status(id={self.id}, name={self.name})>"


class LeadStatusChange(Base):
    __tablename__ = "lead_status_changes"

    id = Column(String(255), primary_key=True)
    lead_id = Column(Integer)
    created_at = Column(DateTime)
    created_by = Column(Integer)
    account_id = Column(Integer)
    old_status_id = Column(Integer)
    old_pipeline_id = Column(Integer)
    new_status_id = Column(Integer)
    new_pipeline_id = Column(Integer)

    LABEL = "events"

    def __repr__(self):
        return f"<Contact(id={self.id}, name={self.name})>"

    def fill(self, data):
        self.id = data["id"]
        self.lead_id = data["entity_id"]
        self.created_at = datetime.fromtimestamp(data["created_at"])
        self.created_by = data["created_by"]
        self.account_id = data["account_id"]
        self.old_status_id = data["value_before"][0]["lead_status"]["id"]
        self.old_pipeline_id = data["value_before"][0]["lead_status"]["pipeline_id"]
        self.new_status_id = data["value_after"][0]["lead_status"]["id"]
        self.new_pipeline_id = data["value_after"][0]["lead_status"]["pipeline_id"]

    def need_update(self, data, if_force_rewrite=False):
        return False


class DataSyncState(Base):
    __tablename__ = "data_sync_state"

    id = Column(Integer, primary_key=True, autoincrement=True)
    last_updated = Column(DateTime, default=datetime.now, nullable=False)
    data_type = Column(String(255), nullable=False, default="")
    last_updated_timestamp = Column(Integer, nullable=False)
    update_log = Column(String(255), nullable=True)
    execution_duration_seconds = Column(Float, nullable=True)

    def __repr__(self):
        return f"<DataSyncState(id={self.id}, last_updated={self.last_updated}, last_updated_timestamp={self.last_updated_timestamp}, execution_duration_seconds={self.execution_duration_seconds}, update_log={self.update_log})>"


class TgUser(Base):
    __tablename__ = "tg_users"

    tg_id = Column(BigInteger, primary_key=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    username = Column(String(255))


# class TgChat(Base):
#     __tablename__ = "tg_chats"

#     tg_id = Column(BigInteger, primary_key=True)
#     title = Column(String(255), nullable=True)
#     username = Column(String(255), nullable=True)
#     type = Column(String(255), nullable=True)
