"""
Utility script to update all agent creation functions to use centralized model config
"""

import re
from pathlib import Path

AGENT_FILES = [
    "weather_agent.py",
    "logistics_agent.py",
    "accommodation_agent.py",
    "itinerary_agent.py",
    "budget_agent.py",
    "souvenir_agent.py",
    "advisory_agent.py",
]


def update_agent_file(filepath: Path, agent_name: str):
    """Update a single agent file to use model_settings"""

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    original_content = content

    # Step 1: Add import for model_settings if not present
    if "from config import model_settings" not in content:
        # Find the config import line
        config_import = re.search(r"from config import settings", content)
        if config_import:
            content = content.replace(
                "from config import settings",
                "from config import settings, model_settings",
            )

    # Step 2: Update function signature
    # OLD: def create_xxx_agent(model: str = "gpt-4o-mini") -> Agent:
    # NEW: def create_xxx_agent(agent_name: str = "xxx") -> Agent:

    func_pattern = rf'def create_{agent_name}_agent\(model: str = "[^"]+"\) -> Agent:'
    func_replacement = (
        f'def create_{agent_name}_agent(agent_name: str = "{agent_name}") -> Agent:'
    )

    content = re.sub(func_pattern, func_replacement, content)

    # Step 3: Update model creation in Agent initialization
    # Look for OpenAIChat(id=model, ...) or OpenAIChat(id="...", ...)
    # Replace with model_settings.create_model_for_agno(agent_name)

    # Pattern 1: model=OpenAIChat(id=model, api_key=settings.openai_api_key, ...)
    pattern1 = r"model=OpenAIChat\(id=model,\s*api_key=settings\.openai_api_key(?:,\s*http_client=[^)]+)?\)"
    replacement1 = "model=model_settings.create_model_for_agno(agent_name)"
    content = re.sub(pattern1, replacement1, content)

    # Pattern 2: model=OpenAIChat(id="...", api_key=settings.openai_api_key, ...)
    pattern2 = r'model=OpenAIChat\(id="[^"]+",\s*api_key=settings\.openai_api_key(?:,\s*http_client=[^)]+)?\)'
    replacement2 = "model=model_settings.create_model_for_agno(agent_name)"
    content = re.sub(pattern2, replacement2, content)

    # Step 4: Remove OpenAIChat import if model_settings is now used
    # Keep it for now as it might be used elsewhere

    # Only write if changes were made
    if content != original_content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main():
    """Update all agent files"""
    agents_dir = Path(__file__).parent

    print("🔧 Updating agent files to use centralized model config...")
    print("=" * 60)

    updated_count = 0

    for agent_file in AGENT_FILES:
        filepath = agents_dir / agent_file

        if not filepath.exists():
            print(f"⚠️  {agent_file} - Not found, skipping")
            continue

        # Extract agent name from filename (e.g., "weather" from "weather_agent.py")
        agent_name = agent_file.replace("_agent.py", "")

        try:
            was_updated = update_agent_file(filepath, agent_name)
            if was_updated:
                print(f"✅ {agent_file} - Updated successfully")
                updated_count += 1
            else:
                print(f"ℹ️  {agent_file} - No changes needed")
        except Exception as e:
            print(f"❌ {agent_file} - Error: {e}")

    print("=" * 60)
    print(f"✅ Updated {updated_count}/{len(AGENT_FILES)} agent files")

    print("\n📝 Manual steps required:")
    print("1. Review changes in each agent file")
    print("2. Update orchestrator_agent.py to pass agent names to create functions:")
    print(
        "   Example: create_weather_agent('weather') instead of create_weather_agent('gpt-4o-mini')"
    )
    print(
        '3. Test with: cd src/travel_planner && uv run python -c "from config import model_settings; model_settings.print_config_summary()"'
    )


if __name__ == "__main__":
    main()
