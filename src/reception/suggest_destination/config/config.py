from dataclasses import dataclass
from pathlib import Path


@dataclass
class ModelConfig:
    """Model Configuration parameters"""

    model_name: str = "bert-base-multilingual-cased"
    proj_dim: int = 256
    max_length: int = 128


@dataclass
class PathConfig:
    """Paths configuration"""

    project_root: Path = Path(__file__).parent.parent
    checkpoint_dir: Path = project_root / "checkpoints"
    model_path: Path = checkpoint_dir / "model.safetensors"
    data_path: Path = project_root / "data" / "description_destination_10k.csv"
    chromadb_path: Path = project_root / "chromadb"

    def __post_init__(self):
        # Convert to Path objects
        self.checkpoint_dir = Path(self.checkpoint_dir)
        self.model_path = Path(self.model_path)
        self.data_path = Path(self.data_path)
        self.chromadb_path = Path(self.chromadb_path)


@dataclass
class IndexConfig:
    """Indexing configuration"""

    collection_name: str = "destinations"
    batch_size: int = 64
    device: str = "cuda"  
    num_threads: int = 8


@dataclass
class SearchConfig:
    """Search configuration"""

    top_k: int = 5
    collection_name: str = "destinations"
    group_by_destination: bool = True
    aggregate_results: bool = False


class Config:
    """Main config class"""

    model = ModelConfig()
    paths = PathConfig()
    index = IndexConfig()
    search = SearchConfig()


# Global config instance
config = Config()
