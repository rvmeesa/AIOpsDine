from sqlalchemy.sql import text
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
from app.orchestrator import publish_event

logger = logging.getLogger(__name__)

async def compute_kpis(db: Session, date: str, range_type: str) -> dict:
    try:
        start_date = datetime.strptime(date, "%Y-%m-%d")
        end_date = start_date + timedelta(days=1 if range_type == "daily" else 7)
        
        logger.info(f"Querying orders for range: {start_date} to {end_date}")
        orders = db.execute(
            text("""
            SELECT COUNT(*) as total_orders, COALESCE(SUM(oi.quantity * m.price), 0) as total_revenue
            FROM orders o
            LEFT JOIN order_items oi ON o.id = oi.order_id
            LEFT JOIN menu m ON oi.menu_id = m.id
            WHERE o.created_at BETWEEN :start_date AND :end_date
            """),
            {"start_date": start_date, "end_date": end_date}
        ).fetchone()
        logger.info(f"Orders query result: {orders}")
        total_orders = orders[0] if orders else 0
        total_revenue = float(orders[1]) if orders and orders[1] is not None else 0.0

        logger.info(f"Querying top items for range: {start_date} to {end_date}")
        top_items = db.execute(
            text("""
            SELECT m.id, m.name, COALESCE(SUM(oi.quantity), 0) as quantity
            FROM order_items oi
            LEFT JOIN menu m ON oi.menu_id = m.id
            LEFT JOIN orders o ON oi.order_id = o.id
            WHERE o.created_at BETWEEN :start_date AND :end_date
            GROUP BY m.id, m.name
            ORDER BY quantity DESC
            LIMIT 3
            """),
            {"start_date": start_date, "end_date": end_date}
        ).fetchall() or []
        logger.info(f"Top items query result: {top_items}")

        logger.info(f"Querying avg ticket for range: {start_date} to {end_date}")
        avg_ticket_result = db.execute(
            text("""
            SELECT COALESCE(AVG(total), 0) FROM (
                SELECT o.id, COALESCE(SUM(oi.quantity * m.price), 0) as total
                FROM orders o
                LEFT JOIN order_items oi ON o.id = oi.order_id
                LEFT JOIN menu m ON oi.menu_id = m.id
                WHERE o.created_at BETWEEN :start_date AND :end_date
                GROUP BY o.id
            ) as ticket_sizes
            """),
            {"start_date": start_date, "end_date": end_date}
        ).fetchone()
        logger.info(f"Avg ticket query result: {avg_ticket_result}")
        avg_ticket = float(avg_ticket_result[0]) if avg_ticket_result and avg_ticket_result[0] is not None else 0.0

        kpis = {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "top_items": [{"menu_id": row[0], "name": row[1], "quantity": row[2]} for row in top_items],
            "avg_ticket_size": avg_ticket
        }
        
        await publish_event("analytics_generated", kpis)
        logger.info(f"Computed KPIs: {kpis}")
        return kpis
    except ValueError as ve:
        logger.error(f"Invalid date format: {str(ve)}")
        raise
    except Exception as e:
        logger.error(f"Compute KPIs failed: {str(e)}, Traceback: {traceback.format_exc()}")
        raise
import traceback  # Add this at the top