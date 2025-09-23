from .database import get_db
from .models import Pipeline, Status


def get_pipeline_names() -> list[str]:
    with next(get_db()) as session:
        names = session.query(Pipeline.name.distinct()).all()
        return [name[0] for name in names]


def get_status_names() -> list[str]:
    with next(get_db()) as session:
        statuses = session.query(Status.name.distinct()).all()
        return [status[0] for status in statuses]
