"""
Centralized Model Configuration for All Agents
Supports: OpenAI (ChatGPT), Google (Gemini), DeepSeek, Anthropic (Claude)
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field

# Load environment variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path, override=True)


class ModelProvider(str, Enum):
    """Supported AI model providers"""

    OPENAI = "openai"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    ANTHROPIC = "anthropic"


class ModelConfig(BaseModel):
    """Configuration for a specific model"""

    provider: ModelProvider
    model_name: str
    api_key: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None

    # Additional provider-specific settings
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class AgentModelSettings(BaseModel):
    """Model configuration system for all agents"""

    # API Keys (loaded from environment)
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    google_api_key: str = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", ""))
    deepseek_api_key: str = Field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY", ""))
    anthropic_api_key: str = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", ""))

    # Default provider for all agents
    default_provider: ModelProvider = ModelProvider.OPENAI

    # Model mappings by provider
    model_mappings: Dict[ModelProvider, str] = Field(
        default_factory=lambda: {
            ModelProvider.OPENAI: "gpt-4o-mini",
            ModelProvider.GOOGLE: "gemini-2.0-flash-exp",
            ModelProvider.DEEPSEEK: "deepseek-chat",
            ModelProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        }
    )

    # Cheap model for memory operations (to reduce costs)
    memory_model_mappings: Dict[ModelProvider, str] = Field(
        default_factory=lambda: {
            ModelProvider.OPENAI: "gpt-4o-mini",  # 60x cheaper than gpt-4o
            ModelProvider.GOOGLE: "gemini-2.0-flash-exp",  # Already cheap
            ModelProvider.DEEPSEEK: "deepseek-chat",  # Already cheap
            ModelProvider.ANTHROPIC: "claude-3-5-haiku-20241022",  # Cheaper Claude
        }
    )

    # Temperature settings (can be overridden per agent)
    default_temperature: float = 0.7

    # Agent-specific overrides (optional)
    agent_overrides: Dict[str, ModelConfig] = Field(default_factory=dict)

    def get_model_config(self, agent_name: Optional[str] = None) -> ModelConfig:
        """
        Get model configuration for a specific agent

        Args:
            agent_name: Name of agent (e.g., "weather", "itinerary"). If None, uses default.

        Returns:
            ModelConfig with provider, model name, and API key
        """
        # Check if there's an agent-specific override
        if agent_name and agent_name in self.agent_overrides:
            return self.agent_overrides[agent_name]

        # Use default provider
        provider = self.default_provider
        model_name = self.model_mappings[provider]

        # Get API key for provider
        api_key = self._get_api_key(provider)

        return ModelConfig(
            provider=provider,
            model_name=model_name,
            api_key=api_key,
            temperature=self.default_temperature,
        )

    def _get_api_key(self, provider: ModelProvider) -> str:
        """Get API key for a specific provider"""
        key_map = {
            ModelProvider.OPENAI: self.openai_api_key,
            ModelProvider.GOOGLE: self.google_api_key,
            ModelProvider.DEEPSEEK: self.deepseek_api_key,
            ModelProvider.ANTHROPIC: self.anthropic_api_key,
        }
        return key_map.get(provider, "")

    def set_agent_model(
        self,
        agent_name: str,
        provider: ModelProvider,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ):
        """
        Override model configuration for a specific agent

        Args:
            agent_name: Name of agent (e.g., "weather", "itinerary")
            provider: Model provider to use
            model_name: Specific model name (if None, uses default for provider)
            temperature: Temperature setting (if None, uses default)
        """
        if model_name is None:
            model_name = self.model_mappings[provider]

        if temperature is None:
            temperature = self.default_temperature

        api_key = self._get_api_key(provider)

        self.agent_overrides[agent_name] = ModelConfig(
            provider=provider, model_name=model_name, api_key=api_key, temperature=temperature
        )

    def get_memory_model_config(self) -> ModelConfig:
        """
        Get cheaper model configuration for memory operations.
        Uses cheaper models to reduce costs (memory ops can be 8x more expensive).

        Returns:
            ModelConfig with cheaper model for the current provider
        """
        provider = self.default_provider
        model_name = self.memory_model_mappings[provider]
        api_key = self._get_api_key(provider)

        return ModelConfig(
            provider=provider, model_name=model_name, api_key=api_key, temperature=0.7
        )

    def create_model_for_agno(self, agent_name: Optional[str] = None):
        """
        Create a model instance compatible with Agno framework

        Args:
            agent_name: Name of agent for specific configuration

        Returns:
            Configured model instance for Agno Agent
        """
        # Special handling for memory operations
        if agent_name == "memory":
            config = self.get_memory_model_config()
        else:
            config = self.get_model_config(agent_name)

        if config.provider == ModelProvider.OPENAI:
            from agno.models.openai import OpenAIChat

            return OpenAIChat(
                id=config.model_name,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

        elif config.provider == ModelProvider.GOOGLE:
            from agno.models.google import Gemini

            return Gemini(
                id=config.model_name,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

        elif config.provider == ModelProvider.DEEPSEEK:
            from agno.models.deepseek import DeepSeek

            # DeepSeek has dedicated class in Agno
            return DeepSeek(
                id=config.model_name,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

        elif config.provider == ModelProvider.ANTHROPIC:
            from agno.models.anthropic import Claude

            return Claude(
                id=config.model_name,
                api_key=config.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )

        else:
            raise ValueError(f"Unsupported provider: {config.provider}")

    def validate_api_keys(self) -> Dict[str, bool]:
        """
        Validate which API keys are configured

        Returns:
            Dictionary mapping provider to whether API key is present
        """
        return {
            "openai": bool(self.openai_api_key),
            "google": bool(self.google_api_key),
            "deepseek": bool(self.deepseek_api_key),
            "anthropic": bool(self.anthropic_api_key),
        }

    def print_config_summary(self):
        """Print configuration summary for debugging"""
        print("\n" + "=" * 60)
        print("🤖 AGENT MODEL CONFIGURATION")
        print("=" * 60)

        print(f"\n📋 Default Provider: {self.default_provider.value}")
        print(f"📋 Default Model: {self.model_mappings[self.default_provider]}")
        print(f"🌡️  Default Temperature: {self.default_temperature}")

        print("\n🔑 API Keys Status:")
        for provider, has_key in self.validate_api_keys().items():
            status = "✅ Configured" if has_key else "❌ Missing"
            print(f"   {provider.upper()}: {status}")

        if self.agent_overrides:
            print(f"\n⚙️  Agent-Specific Overrides: {len(self.agent_overrides)}")
            for agent, config in self.agent_overrides.items():
                print(f"   • {agent}: {config.provider.value}/{config.model_name}")

        print("=" * 60 + "\n")


# ============================================================================
# PREDEFINED CONFIGURATIONS
# ============================================================================


def create_default_config() -> AgentModelSettings:
    """Create default configuration (OpenAI GPT-4o-mini for all agents)"""
    return AgentModelSettings(
        default_provider=ModelProvider.OPENAI,
        model_mappings={
            ModelProvider.OPENAI: "gpt-4o-mini",
            ModelProvider.GOOGLE: "gemini-2.0-flash-exp",
            ModelProvider.DEEPSEEK: "deepseek-chat",
            ModelProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        },
        default_temperature=0.7,
    )


def create_gemini_config() -> AgentModelSettings:
    """Create configuration using Gemini for all agents"""
    return AgentModelSettings(
        default_provider=ModelProvider.GOOGLE,
        model_mappings={
            ModelProvider.OPENAI: "gpt-4o-mini",
            ModelProvider.GOOGLE: "gemini-2.0-flash-exp",
            ModelProvider.DEEPSEEK: "deepseek-chat",
            ModelProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        },
        default_temperature=0.7,
    )


def create_deepseek_config() -> AgentModelSettings:
    """Create configuration using DeepSeek for all agents"""
    return AgentModelSettings(
        default_provider=ModelProvider.DEEPSEEK,
        model_mappings={
            ModelProvider.OPENAI: "gpt-4o-mini",
            ModelProvider.GOOGLE: "gemini-2.0-flash-exp",
            ModelProvider.DEEPSEEK: "deepseek-chat",
            ModelProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        },
        default_temperature=0.7,
    )


def create_hybrid_config() -> AgentModelSettings:
    """
    Create hybrid configuration with different models for different agents
    Example: Fast models for simple tasks, powerful models for complex tasks
    """
    config = AgentModelSettings(default_provider=ModelProvider.OPENAI, default_temperature=0.7)

    # Use faster/cheaper models for simple tasks
    config.set_agent_model("weather", ModelProvider.OPENAI, "gpt-4o-mini", 0.5)
    config.set_agent_model("souvenir", ModelProvider.OPENAI, "gpt-4o-mini", 0.7)

    # Use more powerful models for complex planning
    config.set_agent_model("itinerary", ModelProvider.OPENAI, "gpt-4o", 0.7)
    config.set_agent_model("budget", ModelProvider.OPENAI, "gpt-4o", 0.6)

    return config


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

# Create global model settings instance
model_settings = create_default_config()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example 1: Print default configuration
    print("Example 1: Default Configuration (OpenAI)")
    model_settings.print_config_summary()

    # Example 2: Switch to Gemini
    print("\nExample 2: Switching to Gemini")
    gemini_settings = create_gemini_config()
    gemini_settings.print_config_summary()

    # Example 3: Hybrid configuration
    print("\nExample 3: Hybrid Configuration")
    hybrid = create_hybrid_config()
    hybrid.print_config_summary()

    # Example 4: Get model for specific agent
    print("\nExample 4: Get Model Config for Itinerary Agent")
    itinerary_model = hybrid.get_model_config("itinerary")
    print(f"Provider: {itinerary_model.provider}")
    print(f"Model: {itinerary_model.model_name}")
    print(f"Temperature: {itinerary_model.temperature}")
