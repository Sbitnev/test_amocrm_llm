from datetime import datetime
import statistics

from sqlalchemy import func, text, select
from sqlalchemy.orm import Session

from schemas import Digest, Seller
from database import get_db
from models import LeadStatusChange, Lead, TgUser, User


class Metrics:
    def _get_sellers_performance(
        self,
        session: Session,
        closed_lead_ids: list[int],
    ) -> tuple[Seller, Seller]:
        """
        Находит лучшего и худшего продавца по закрытым сделкам

        Args:
            session: SQLAlchemy session
            closed_lead_ids: список ID закрытых сделок

        Returns:
            tuple: (best_seller, worst_seller)
        """
        if not closed_lead_ids:
            # Если нет закрытых сделок, возвращаем продавцов с нулевыми значениями
            return Seller(), Seller()

        # Запрос для получения продаж по пользователям
        sales_by_user = (
            session.query(User.name, func.sum(Lead.price).label("total_sales"))
            .join(Lead, Lead.responsible_user_id == User.id)
            .filter(Lead.id.in_(closed_lead_ids))
            .group_by(User.id, User.name)
            .all()
        )

        if not sales_by_user:
            # Если есть сделки, но нет данных о пользователях
            return Seller(), Seller()

        # Находим лучшего продавца (максимальная сумма)
        best_seller_data = max(sales_by_user, key=lambda x: x[1] or 0)
        best_seller = Seller(
            name=best_seller_data[0] or "Неизвестен",
            total_price=best_seller_data[1] or 0,
        )

        # Находим худшего продавца (минимальная сумма среди тех, у кого есть продажи)
        worst_seller_data = min(sales_by_user, key=lambda x: x[1] or 0)
        worst_seller = Seller(
            name=worst_seller_data[0] or "Неизвестен",
            total_price=worst_seller_data[1] or 0,
        )

        return best_seller, worst_seller

    def get_raw_digest(self, start_dt: datetime, end_dt: datetime) -> Digest:
        with next(get_db()) as session:
            created_leads: int = (
                session.query(func.count(Lead.id))
                .filter(start_dt <= Lead.created_at, Lead.created_at < end_dt)
                .scalar()
            )
            closed_lead_ids = (
                session.query(LeadStatusChange.lead_id)
                .filter(
                    start_dt <= LeadStatusChange.created_at,
                    LeadStatusChange.created_at < end_dt,
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
            best_seller, worst_seller = self._get_sellers_performance(
                session, closed_lead_ids
            )

            digest = Digest(
                start_dt=start_dt,
                end_dt=end_dt,
                created_leads=created_leads,
                closed_leads=len(closed_leads),
                total_price=total_price,
                avg_price=avg_price,
                best_seller=best_seller,
                worst_seller=worst_seller,
                conversion=conversion,
            )
            return digest

    def get_digest(self, start_dt: datetime, end_dt: datetime) -> Digest:
        current_digest = self.get_raw_digest(start_dt, end_dt)
        td = end_dt - start_dt
        prev_digest = self.get_raw_digest(start_dt - td, end_dt - td)
        alerts = []
        if current_digest.created_leads < prev_digest.created_leads:
            alerts.append("Падение по количеству новых сделок")
        if current_digest.closed_leads < prev_digest.closed_leads:
            alerts.append("Падение по сумме закрытых сделок")
        if current_digest.conversion < prev_digest.conversion:
            alerts.append("Падение конверсии")
        if current_digest.avg_price < prev_digest.avg_price:
            alerts.append("Падение среднего чека")

        current_digest.alerts = alerts
        return current_digest

    @staticmethod
    def get_nl_tg_user_ids():
        with next(get_db()) as session:
            ids = session.query(TgUser.tg_id).filter(TgUser.newsletter == True).all()
            return [i[0] for i in ids]


metrics = Metrics()
