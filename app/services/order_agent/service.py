from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from datetime import datetime
import logging
from app.orchestrator import publish_event

logger = logging.getLogger(__name__)

async def create_order(db: Session, table_id: int, items: list[dict]) -> dict:
    try:
        logger.info(f"Checking table with id {table_id}")
        table = db.execute(
            text("SELECT status FROM tables WHERE id = :table_id"),  # Changed to id
            {"table_id": table_id}
        ).fetchone()
        logger.info(f"Table query result: {table}")
        if not table:
            logger.error(f"Table with id {table_id} not found")
            raise ValueError(f"Table with id {table_id} not found")
        if table[0] != "available":
            logger.error(f"Table with id {table_id} status is {table[0]}, not available")
            raise ValueError(f"Table with id {table_id} is not available (status: {table[0]})")

        logger.info(f"Validating items: {items}")
        for item in items:
            if not all(k in item for k in ["menu_id", "quantity"]):
                logger.error(f"Invalid item format: {item}")
                raise ValueError(f"Invalid item format: {item}")
            menu_item = db.execute(
                text("SELECT id FROM menu WHERE id = :menu_id"),
                {"menu_id": item["menu_id"]}
            ).fetchone()
            if not menu_item:
                logger.error(f"Menu item {item['menu_id']} not found")
                raise ValueError(f"Menu item {item['menu_id']} not found")
            if not isinstance(item["quantity"], int) or item["quantity"] <= 0:
                logger.error(f"Invalid quantity for item {item['menu_id']}: {item['quantity']}")
                raise ValueError(f"Invalid quantity for item {item['menu_id']}: {item['quantity']}")

        order_result = db.execute(
            text("""
                INSERT INTO orders (table_id, status, created_at)
                VALUES (:table_id, 'pending', :now)
                RETURNING id
            """),
            {"table_id": table_id, "now": datetime.utcnow()}
        )
        order_id = order_result.fetchone()[0]

        for item in items:
            db.execute(
                text("""
                    INSERT INTO order_items (order_id, menu_id, quantity)
                    VALUES (:order_id, :menu_id, :quantity)
                """),
                {"order_id": order_id, "menu_id": item["menu_id"], "quantity": item["quantity"]}
            )

        db.execute(
            text("UPDATE tables SET status = 'occupied' WHERE id = :table_id"),  # Changed to id
            {"table_id": table_id}
        )
        db.commit()

        await publish_event("order_created", {"order_id": order_id, "table_id": table_id})

        logger.info(f"Created order {order_id} for table with id {table_id}")
        return {
            "order_id": order_id,
            "table_id": table_id,
            "status": "pending",
            "items": [{"menu_id": item["menu_id"], "quantity": item["quantity"]} for item in items]
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Order creation failed: {str(e)}", exc_info=True)
        raise

async def update_order_status(db: Session, order_id: int, status: str) -> dict:
    try:
        valid_statuses = ["pending", "preparing", "served", "paid"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Use {valid_statuses}")

        order = db.execute(
            text("SELECT id, table_id, status FROM orders WHERE id = :order_id"),
            {"order_id": order_id}
        ).fetchone()
        if not order:
            raise ValueError(f"Order {order_id} not found")

        db.execute(
            text("UPDATE orders SET status = :status WHERE id = :order_id"),
            {"status": status, "order_id": order_id}
        )
        db.commit()

        await publish_event("order_updated", {"order_id": order_id, "status": status})
        logger.info(f"Updated order {order_id} to status {status} (previous: {order[2]})")
        return {"order_id": order_id, "table_id": order[1], "status": status}
    except Exception as e:
        db.rollback()
        logger.error(f"Order update failed: {str(e)}", exc_info=True)
        raise