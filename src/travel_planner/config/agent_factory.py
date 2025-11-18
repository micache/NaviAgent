"""
Production-ready configuration for agents with database support.
"""

from agno.agent import Agent
from config.database import get_db
from config.model_settings import model_settings


def create_production_agent(
    agent_name: str = "production",
    user_id: str = None,
    enable_memory: bool = True,
) -> Agent:
    """
    Create production-ready agent with database support.

    Features:
    - PostgreSQL database for sessions and memories
    - Automatic session history (last 5 runs)
    - User memory management
    - Session summaries for long conversations
    - Optimized for cost (uses cheaper model for memory ops)

    Args:
        agent_name: Agent name for model configuration
        user_id: Optional default user ID
        enable_memory: Enable user memory management

    Returns:
        Configured Agent instance
    """
    db = get_db()

    # Use cheaper model for memory operations to reduce costs
    from agno.memory import MemoryManager

    memory_manager = MemoryManager(
        db=db,
        model=model_settings.create_model_for_agno("memory"),  # Cheap model for memory
    )

    agent = Agent(
        model=model_settings.create_model_for_agno(agent_name),  # Main model
        db=db,
        user_id=user_id,
        # Session configuration
        add_history_to_context=True,  # Add previous messages
        num_history_runs=5,  # Include last 5 runs
        read_chat_history=True,  # Allow reading full history
        # Memory configuration
        enable_user_memories=enable_memory,  # Automatic memory management
        memory_manager=memory_manager,  # Use optimized memory manager
        # Session summaries
        enable_session_summaries=True,  # Auto-create summaries
        # Storage optimization
        store_media=False,  # Don't store images/videos (save space)
        store_tool_messages=True,  # Keep tool calls for debugging
        store_history_messages=True,  # Keep history for context
        # Safety
        tool_call_limit=10,  # Prevent runaway tool calls
        markdown=True,
    )

    return agent


# Example usage in production
if __name__ == "__main__":
    # Create agent for a specific user
    agent = create_production_agent(
        agent_name="travel_assistant",
        user_id="user_12345",
        enable_memory=True,
    )

    # Use in API endpoints
    session_id = "booking_session_001"

    response = agent.run(
        "I want to book a trip to Japan for 7 days",
        user_id="user_12345",
        session_id=session_id,
    )

    print(response.content)
