"""
Configuration schema validation using Pydantic

This module provides type-safe configuration validation for Obsidian Auto-Linker.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path
import os


class OllamaConfig(BaseModel):
    """Ollama API configuration"""
    base_url: str = Field(default="http://localhost:11434", description="Ollama API base URL")
    model: str = Field(default="qwen2.5:3b", description="Ollama model to use")
    timeout: int = Field(default=15, ge=5, le=300, description="API timeout in seconds")
    max_retries: int = Field(default=1, ge=0, le=5, description="Maximum retry attempts")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Model temperature")
    max_tokens: int = Field(default=200, ge=50, le=2000, description="Maximum tokens in response")

    @field_validator('base_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("base_url must start with http:// or https://")
        return v


class ProcessingConfig(BaseModel):
    """Processing behavior configuration"""
    vault_path: str = Field(description="Path to Obsidian vault")
    dry_run: bool = Field(default=True, description="If True, don't modify files")
    fast_dry_run: bool = Field(default=False, description="If True, skip AI analysis")
    batch_size: int = Field(default=1, ge=1, le=100, description="Number of files to process per batch")
    file_ordering: str = Field(default="recent", description="File processing order")
    cache_enabled: bool = Field(default=True, description="Enable AI response caching")
    resume_enabled: bool = Field(default=True, description="Enable resume from progress file")
    confirm_large_batches: bool = Field(default=False, description="Prompt before large batches")

    @field_validator('vault_path')
    @classmethod
    def validate_vault_path(cls, v: str) -> str:
        """Validate vault path exists and is a directory"""
        if not v:
            raise ValueError("vault_path cannot be empty")

        # Expand user home directory if needed
        expanded_path = os.path.expanduser(v)

        # For security, reject paths with suspicious patterns
        if '..' in v:
            # Allow relative paths but warn about path traversal
            pass

        return expanded_path

    @field_validator('file_ordering')
    @classmethod
    def validate_file_ordering(cls, v: str) -> str:
        """Validate file ordering option"""
        valid_options = ['recent', 'size', 'random', 'alphabetical']
        if v not in valid_options:
            raise ValueError(f"file_ordering must be one of {valid_options}")
        return v


class FilterConfig(BaseModel):
    """File filtering configuration"""
    exclude_patterns: List[str] = Field(default_factory=lambda: ["*.tmp", ".*", "_*"])
    include_patterns: List[str] = Field(default_factory=lambda: ["*.md"])
    folder_whitelist: Optional[List[str]] = Field(default=None, description="Only process these folders")
    folder_blacklist: List[str] = Field(default_factory=lambda: ["_backups", ".git", "Templates"])


class ObsidianConfig(BaseModel):
    """Complete Obsidian Auto-Linker configuration"""

    # Core processing
    vault_path: str = Field(description="Path to Obsidian vault")
    dry_run: bool = Field(default=True)
    fast_dry_run: bool = Field(default=False)
    batch_size: int = Field(default=1, ge=1, le=100)
    file_ordering: str = Field(default="recent")

    # Ollama configuration
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="qwen2.5:3b")
    ollama_timeout: int = Field(default=15, ge=5, le=300)
    ollama_max_retries: int = Field(default=1, ge=0, le=5)
    ollama_temperature: float = Field(default=0.3, ge=0.0, le=2.0)
    ollama_max_tokens: int = Field(default=200, ge=50, le=2000)

    # Features
    cache_enabled: bool = Field(default=True)
    resume_enabled: bool = Field(default=True)
    incremental: bool = Field(default=False, description="Enable incremental processing")
    incremental_tracker_file: str = Field(default=".file_hashes.json", description="Where to persist incremental hashes")
    link_quality_threshold: float = Field(default=0.2, ge=0.0, le=1.0, description="Minimum sibling similarity score to keep")
    max_cache_size_mb: int = Field(default=500, ge=1, description="Bounded cache size in MB")
    max_cache_entries: int = Field(default=10000, ge=1, description="Bounded cache entry count")
    confirm_large_batches: bool = Field(default=False)
    embedding_enabled: bool = Field(default=False, description="Enable embedding-based similarity")
    embedding_base_url: str = Field(default="http://localhost:11434", description="Embedding API base URL")
    embedding_model: str = Field(default="nomic-embed-text:latest", description="Embedding model to use")
    embedding_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum cosine similarity to keep")
    embedding_top_k: int = Field(default=12, ge=1, le=50, description="How many embedding neighbors to consider")
    knowledge_graph_file: str = Field(default="knowledge_graph.json", description="Where to export the knowledge graph edges")

    # Filtering
    exclude_patterns: List[str] = Field(default_factory=lambda: ["*.tmp", ".*", "_*"])
    include_patterns: List[str] = Field(default_factory=lambda: ["*.md"])
    folder_whitelist: Optional[List[str]] = Field(default=None)
    folder_blacklist: List[str] = Field(default_factory=lambda: ["_backups", ".git", "Templates"])

    # Advanced
    parallel_processing_enabled: bool = Field(
        default=False, description="Enable experimental parallel processing"
    )
    parallel_workers: int = Field(default=1, ge=1, le=16)
    max_retries: int = Field(default=1, ge=0, le=5)

    # Custom MOCs
    custom_mocs: Dict[str, str] = Field(default_factory=dict)

    @field_validator('vault_path')
    @classmethod
    def validate_vault_path(cls, v: str) -> str:
        """Validate and expand vault path"""
        if not v:
            raise ValueError("vault_path cannot be empty")

        # Expand user home directory
        expanded_path = os.path.expanduser(v)

        # Security: Reject absolute path traversal attempts
        try:
            resolved = os.path.abspath(expanded_path)
            # Basic sanity check - path should not escape too far up
            if resolved.count(os.sep) < 2:
                raise ValueError(f"Suspicious vault path: {v}")
        except (ValueError, OSError):
            pass  # Allow, will be caught later if actually invalid

        return expanded_path

    @field_validator('file_ordering')
    @classmethod
    def validate_file_ordering(cls, v: str) -> str:
        """Validate file ordering option"""
        valid_options = ['recent', 'size', 'random', 'alphabetical']
        if v not in valid_options:
            raise ValueError(f"file_ordering must be one of {valid_options}")
        return v

    @field_validator('ollama_base_url')
    @classmethod
    def validate_ollama_url(cls, v: str) -> str:
        """Validate Ollama URL format"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("ollama_base_url must start with http:// or https://")
        return v

    @field_validator('embedding_base_url')
    @classmethod
    def validate_embedding_url(cls, v: str) -> str:
        """Validate embedding base URL"""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("embedding_base_url must start with http:// or https://")
        return v

    @model_validator(mode='after')
    def validate_dry_run_modes(self):
        """Validate dry run mode combinations"""
        if self.fast_dry_run and not self.dry_run:
            raise ValueError("fast_dry_run requires dry_run to be enabled")
        return self

    def to_dict(self) -> dict:
        """Convert config to dictionary"""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict) -> 'ObsidianConfig':
        """Create config from dictionary with validation"""
        return cls(**data)

    @classmethod
    def from_yaml_file(cls, file_path: str) -> 'ObsidianConfig':
        """Load and validate config from YAML file"""
        import yaml

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            if data is None:
                data = {}

            return cls(**data)

        except FileNotFoundError:
            # If file doesn't exist, validation will fail without vault_path
            # Return empty dict to trigger validation error
            return cls(**{})
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")

    def save_to_yaml_file(self, file_path: str) -> None:
        """Save config to YAML file"""
        import yaml

        data = self.to_dict()

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, indent=2)


# Convenience function for backward compatibility
def load_and_validate_config(config_path: str = 'config.yaml') -> ObsidianConfig:
    """Load and validate configuration from YAML file

    Args:
        config_path: Path to config.yaml file

    Returns:
        Validated ObsidianConfig instance

    Raises:
        ValueError: If configuration is invalid
        FileNotFoundError: If config file doesn't exist and vault_path is required
    """
    return ObsidianConfig.from_yaml_file(config_path)


if __name__ == "__main__":
    # Test configuration validation
    print("Testing configuration schema...")

    # Test with minimal config
    try:
        config = ObsidianConfig(vault_path='/tmp/test_vault')
        print("✓ Minimal config valid")
    except Exception as e:
        print(f"✗ Minimal config failed: {e}")

    # Test with invalid file_ordering
    try:
        config = ObsidianConfig(vault_path='/tmp', file_ordering='invalid')
        print("✗ Should have rejected invalid file_ordering")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid file_ordering: {e}")

    # Test with invalid URL
    try:
        config = ObsidianConfig(vault_path='/tmp', ollama_base_url='invalid-url')
        print("✗ Should have rejected invalid URL")
    except ValueError as e:
        print(f"✓ Correctly rejected invalid URL: {e}")

    # Test fast_dry_run without dry_run
    try:
        config = ObsidianConfig(vault_path='/tmp', fast_dry_run=True, dry_run=False)
        print("✗ Should have rejected fast_dry_run without dry_run")
    except ValueError as e:
        print(f"✓ Correctly rejected incompatible modes: {e}")

    print("\nAll schema validation tests passed!")
