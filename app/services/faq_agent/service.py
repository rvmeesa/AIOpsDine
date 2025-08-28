import logging
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from sqlalchemy.sql import text
from db.connection import get_db
from functools import lru_cache
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for production readiness
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Mistral LLM
try:
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key:
        raise ValueError("MISTRAL_API_KEY is not set in .env")
    llm = ChatMistralAI(api_key=api_key, model="mistral-small")
    logger.info("Mistral LLM initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Mistral LLM: {str(e)}")
    raise

# Tools for LLM
@tool
def search_menu(query: str) -> list:
    """Search menu for items matching query (e.g., vegan, category)."""
    try:
        with next(get_db()) as db:
            if "vegan" in query.lower():
                result = db.execute(text("SELECT name, description, price FROM menu WHERE is_vegan = 1")).fetchall()
            else:
                result = db.execute(
                    text("SELECT name, description, price FROM menu WHERE name LIKE :q OR category LIKE :q"),
                    {"q": f"%{query}%"}
                ).fetchall()
            logger.info(f"Menu search query: {query}, results: {len(result)}")
            return [{"name": row[0], "description": row[1], "price": row[2]} for row in result]
    except Exception as e:
        logger.error(f"Menu search error: {str(e)}")
        return []

@tool
def check_reservations(customer_name: str) -> list:
    """Check reservations by customer name."""
    try:
        with next(get_db()) as db:
            result = db.execute(
                text("SELECT customer_name, reservation_time, table_id FROM reservations WHERE customer_name LIKE :name"),
                {"name": f"%{customer_name}%"}
            ).fetchall()
            logger.info(f"Reservation search for {customer_name}, results: {len(result)}")
            return [{"customer_name": row[0], "reservation_time": str(row[1]), "table_id": row[2]} for row in result]
    except Exception as e:
        logger.error(f"Reservation check error: {str(e)}")
        return []

# Cache responses for repeated queries
@lru_cache(maxsize=100)
def cached_query(query: str) -> str:
    """Cached FAQ query processing."""
    try:
        # Load static policy
        logger.info("Attempting to load policy file")
        with open("data/policy.txt", "r") as f:
            policy = f.read()
        logger.info("Policy file loaded successfully")
        
        # Prompt template
        logger.info("Creating prompt template")
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a restaurant assistant. Use tools to fetch data. Always call 'search_menu' for menu-related queries and 'check_reservations' for reservation queries. Policy: {policy}"),
            ("user", "{query}")
        ])
        
        # Chain with tools
        logger.info("Binding tools to LLM")
        chain = prompt | llm.bind_tools([search_menu, check_reservations])
        
        # Invoke LLM
        logger.info(f"Invoking LLM with query: {query}")
        response = chain.invoke({"query": query, "policy": policy})
        
        # Parse response
        content = response.content
        logger.info(f"LLM response content: {content}")
        if response.tool_calls:
            logger.info(f"Tool calls: {response.tool_calls}")
            for call in response.tool_calls:
                content += f"\nTool result: {call['name']} returned {call['output']}"
        else:
            # Fallback for vegan queries if tool-calling fails
            if "vegan" in query.lower():
                logger.info("Tool-calling failed; using direct search_menu call")
                results = search_menu(query)
                content = "Vegan dishes: " + "; ".join([f"{r['name']}: {r['description']}, ${r['price']}" for r in results])
        logger.info(f"Processed FAQ query: {query}")
        return content
    except Exception as e:
        logger.error(f"FAQ query error: {str(e)}")
        return "Sorry, I couldn't process your request. Please try again."

# Main query function (publishes event to orchestrator)
async def answer_query(query: str) -> str:
    """Answer a customer query and publish event to orchestrator."""
    from app.orchestrator import publish_event
    response = cached_query(query)
    await publish_event("faq_query_processed", {"query": query, "response": response})
    return response