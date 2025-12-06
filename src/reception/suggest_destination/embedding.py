from typing import Dict, List
from pathlib import Path

import numpy as np
import torch
from safetensors.torch import load_file
from transformers import AutoTokenizer

from reception.suggest_destination.config.config import config
from reception.suggest_destination.models.CLIP_model import TextTextCLIPModel


class EmbeddingGenerator:
    """Generate embeddings from text using trained model"""

    def __init__(self, model_path: str = None, device: str = None):
        print("[INFO] Initializing EmbeddingGenerator...")
        self.device = device or config.index.device
        if self.device == "cuda" and not torch.cuda.is_available():
            print("CUDA not available, using CPU")
            self.device = "cpu"

        self.device = torch.device(self.device)

        # CPU optimization
        if self.device.type == "cpu":
            num_threads = getattr(config.index, "num_threads", 8)
            try:
                torch.set_num_threads(num_threads)
                torch.set_num_interop_threads(max(1, num_threads // 2))
            except RuntimeError:
                # Threads already set, skip
                pass
            print(f"Using device: CPU with {torch.get_num_threads()} threads")
        else:
            print(f"Using device: {self.device}")

        # Load tokenizer from local checkpoint
        checkpoint_dir = str(config.paths.checkpoint_dir)
        print(f"[INFO] Loading tokenizer from local checkpoint: {checkpoint_dir}")
        try:
            # Try loading from local checkpoint first
            self.tokenizer = AutoTokenizer.from_pretrained(checkpoint_dir, local_files_only=True)
            print("[INFO] Tokenizer loaded from local checkpoint")
        except Exception as e:
            print(f"[WARNING] Failed to load from local: {e}")
            print(f"[INFO] Falling back to HuggingFace Hub: {config.model.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(config.model.model_name)
            print("[INFO] Tokenizer loaded from HuggingFace Hub")

        # Load model
        model_path = model_path or str(config.paths.model_path)
        self.model = self._load_model(model_path)
        self.model.eval()
        print("[INFO] EmbeddingGenerator initialization complete")

    def _load_model(self, model_path: str) -> TextTextCLIPModel:
        """Load model from safetensors"""
        print(f"[INFO] Loading model from: {model_path}")
        print(f"[INFO] Model file exists: {Path(model_path).exists()}")
        if Path(model_path).exists():
            import os
            file_size_mb = os.path.getsize(model_path) / (1024 * 1024)
            print(f"[INFO] Model file size: {file_size_mb:.2f} MB")
        
        # Create model with local checkpoint directory
        checkpoint_dir = str(config.paths.checkpoint_dir)
        model = TextTextCLIPModel(
            model_name=config.model.model_name, 
            proj_dim=config.model.proj_dim,
            checkpoint_dir=checkpoint_dir
        )

        print(f"[INFO] Loading safetensors state_dict...")
        state_dict = load_file(model_path)
        print(f"[INFO] Safetensors loaded successfully. Keys count: {len(state_dict)}")
        
        model.load_state_dict(state_dict)
        model.to(self.device)

        print(f"✓ Model loaded successfully from {model_path}")
        return model

    def preprocess(self, text: str) -> Dict[str, torch.Tensor]:
        """Tokenize text"""
        encoded = self.tokenizer(
            text,
            max_length=config.model.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoded["input_ids"].to(self.device),
            "attention_mask": encoded["attention_mask"].to(self.device),
        }

    def preprocess_batch(self, texts: List[str]) -> Dict[str, torch.Tensor]:
        """Tokenize batch of texts - FASTER than one-by-one"""
        encoded = self.tokenizer(
            texts,
            max_length=config.model.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return {
            "input_ids": encoded["input_ids"].to(self.device),
            "attention_mask": encoded["attention_mask"].to(self.device),
        }

    @torch.no_grad()
    def generate(self, text: str) -> np.ndarray:
        """Generate embedding for single text"""
        inputs = self.preprocess(text)
        embedding = self.model(
            input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"]
        )
        return embedding.cpu().numpy().flatten()

    @torch.no_grad()
    def generate_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for batch of texts - MUCH FASTER"""
        inputs = self.preprocess_batch(texts)
        embeddings = self.model(
            input_ids=inputs["input_ids"], attention_mask=inputs["attention_mask"]
        )
        return embeddings.cpu().numpy()
