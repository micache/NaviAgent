import torch.nn as nn
from transformers import AutoModel
from pathlib import Path


class TextTextCLIPModel(nn.Module):
    """Text-Text Contrastive Learning Model"""

    def __init__(self, model_name: str = "bert-base-multilingual-cased", proj_dim: int = 256, checkpoint_dir: str = None):
        super().__init__()
        
        # Try loading from local checkpoint first, fallback to HuggingFace
        if checkpoint_dir and Path(checkpoint_dir).exists():
            try:
                print(f"[INFO] Loading BERT encoder from local checkpoint: {checkpoint_dir}")
                self.encoder = AutoModel.from_pretrained(checkpoint_dir, local_files_only=True)
                print("[INFO] BERT encoder loaded from local checkpoint")
            except Exception as e:
                print(f"[WARNING] Failed to load from local: {e}")
                print(f"[INFO] Falling back to HuggingFace Hub: {model_name}")
                self.encoder = AutoModel.from_pretrained(model_name)
        else:
            print(f"[INFO] Loading BERT encoder from HuggingFace Hub: {model_name}")
            self.encoder = AutoModel.from_pretrained(model_name)
        
        hidden = self.encoder.config.hidden_size
        self.proj = nn.Linear(hidden, proj_dim)

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0]
        z = self.proj(cls)
        z = z / z.norm(dim=-1, keepdim=True)
        return z
