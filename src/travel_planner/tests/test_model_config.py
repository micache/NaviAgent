"""
Test script for model configuration
Run: uv run python test_model_config.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    ModelProvider,
    create_deepseek_config,
    create_default_config,
    create_gemini_config,
    model_settings,
)


def test_api_keys():
    """Test which API keys are configured"""
    print("\n" + "=" * 60)
    print("🔑 API KEY VALIDATION TEST")
    print("=" * 60)

    keys = model_settings.validate_api_keys()

    for provider, has_key in keys.items():
        status = "✅ Configured" if has_key else "❌ Missing"
        print(f"{provider.upper():12s}: {status}")

    configured_count = sum(keys.values())
    print(f"\nTotal configured: {configured_count}/4 providers")

    if configured_count == 0:
        print("\n⚠️  WARNING: No API keys found!")
        print("Please add at least one API key to your .env file")
        return False

    return True


def test_default_config():
    """Test default configuration"""
    print("\n" + "=" * 60)
    print("📋 DEFAULT CONFIGURATION TEST")
    print("=" * 60)

    config = create_default_config()
    config.print_config_summary()

    # Test creating a model
    try:
        model = config.create_model_for_agno()
        print(f"✅ Successfully created model: {model.id}")
        return True
    except Exception as e:
        print(f"❌ Error creating model: {e}")
        return False


def test_provider_switching():
    """Test switching between providers"""
    print("\n" + "=" * 60)
    print("🔄 PROVIDER SWITCHING TEST")
    print("=" * 60)

    providers_to_test = []
    keys = model_settings.validate_api_keys()

    if keys["openai"]:
        providers_to_test.append(("OpenAI", ModelProvider.OPENAI))
    if keys["google"]:
        providers_to_test.append(("Gemini", ModelProvider.GOOGLE))
    if keys["deepseek"]:
        providers_to_test.append(("DeepSeek", ModelProvider.DEEPSEEK))
    if keys["anthropic"]:
        providers_to_test.append(("Claude", ModelProvider.ANTHROPIC))

    if not providers_to_test:
        print("❌ No configured providers to test")
        return False

    for name, provider in providers_to_test:
        try:
            model_settings.default_provider = provider
            model = model_settings.create_model_for_agno()
            print(f"✅ {name:12s}: {model.id}")
        except Exception as e:
            print(f"❌ {name:12s}: Error - {e}")

    return True


def test_agent_override():
    """Test agent-specific model override"""
    print("\n" + "=" * 60)
    print("⚙️  AGENT OVERRIDE TEST")
    print("=" * 60)

    # Reset to default
    model_settings.default_provider = ModelProvider.OPENAI
    model_settings.agent_overrides.clear()

    # Set override for specific agent
    keys = model_settings.validate_api_keys()

    if keys["openai"] and keys["google"]:
        # Use OpenAI as default
        model_settings.default_provider = ModelProvider.OPENAI

        # Override itinerary agent to use Gemini
        model_settings.set_agent_model(
            agent_name="itinerary",
            provider=ModelProvider.GOOGLE,
            model_name="gemini-2.0-flash-exp",
        )

        # Test default agent
        default_model = model_settings.create_model_for_agno("weather")
        print(f"Default (weather): {default_model.id}")

        # Test overridden agent
        override_model = model_settings.create_model_for_agno("itinerary")
        print(f"Override (itinerary): {override_model.id}")

        if "gpt-" in default_model.id and "gemini" in override_model.id:
            print("✅ Agent override working correctly")
            return True
        else:
            print("❌ Agent override not working as expected")
            return False
    else:
        print("⚠️  Skipped: Need both OpenAI and Google API keys")
        return True


def test_model_configs():
    """Test preset configurations"""
    print("\n" + "=" * 60)
    print("📦 PRESET CONFIGURATIONS TEST")
    print("=" * 60)

    configs = [
        ("Default (OpenAI)", create_default_config()),
        ("Gemini", create_gemini_config()),
        ("DeepSeek", create_deepseek_config()),
    ]

    for name, config in configs:
        print(f"\n{name}:")
        print(f"  Provider: {config.default_provider.value}")
        print(f"  Model: {config.model_mappings[config.default_provider]}")
        print(f"  Temperature: {config.default_temperature}")

    return True


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("🧪 MODEL CONFIGURATION TEST SUITE")
    print("=" * 70)

    tests = [
        ("API Keys", test_api_keys),
        ("Default Config", test_default_config),
        ("Provider Switching", test_provider_switching),
        ("Agent Override", test_agent_override),
        ("Preset Configs", test_model_configs),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20s}: {status}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Configuration is working correctly.")
        print("\n📝 Next steps:")
        print("1. Update your agents to use model_settings")
        print("2. Run: cd src/travel_planner/agents && uv run python update_agents.py")
        print("3. Test with: cd src/travel_planner && uv run python test_api.py")
    else:
        print("\n⚠️  Some tests failed. Please check your configuration.")
        print("Make sure you have at least one API key in your .env file")

    print("=" * 70)


if __name__ == "__main__":
    main()
