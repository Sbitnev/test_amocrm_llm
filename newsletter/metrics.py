from datetime import datetime
import statistics

from sqlalchemy import func, text, select

from schemas import Digest
from database import get_db
from models import LeadStatusChange, Lead, TgUser


class Metrics:
    @staticmethod
    def get_digest(start_dt: datetime, end_dt: datetime) -> Digest:
        with next(get_db()) as session:
            created_leads: int = (
                session.query(func.count(Lead.id))
                .filter(start_dt <= Lead.created_at, Lead.created_at <= end_dt)
                .scalar()
            )
            closed_lead_ids = (
                session.query(LeadStatusChange.lead_id)
                .filter(
                    start_dt <= LeadStatusChange.created_at,
                    LeadStatusChange.created_at <= end_dt,
                    LeadStatusChange.new_status_id == 142,
                )
                .all()
            )
            closed_lead_ids = [row[0] for row in closed_lead_ids]
            closed_leads = (
                session.query(Lead).filter(Lead.id.in_(closed_lead_ids)).all()
            )
            sells = [lead.price for lead in closed_leads]
            total_price = sum(sells) if sells else 0
            avg_price = statistics.mean(sells) if sells else 0
            conversion = created_leads / len(closed_leads) if len(closed_leads) else 0

            digest = Digest(
                start_dt=start_dt,
                end_dt=end_dt,
                created_leads=created_leads,
                closed_leads=len(closed_leads),
                total_price=total_price,
                avg_price=avg_price,
                conversion=conversion,
            )
            return digest

    @staticmethod
    def get_nl_tg_user_ids():
        with next(get_db()) as session:
            ids = session.query(TgUser.tg_id).filter(TgUser.newsletter == True).all()
            return [i[0] for i in ids]


metrics = Metrics()
