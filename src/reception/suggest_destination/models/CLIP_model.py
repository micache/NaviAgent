import torch.nn as nn
from transformers import AutoModel


class TextTextCLIPModel(nn.Module):
    """Text-Text Contrastive Learning Model"""

    def __init__(self, model_name: str = "bert-base-multilingual-cased", proj_dim: int = 256):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden = self.encoder.config.hidden_size
        self.proj = nn.Linear(hidden, proj_dim)

    def forward(self, input_ids, attention_mask):
        out = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls = out.last_hidden_state[:, 0]
        z = self.proj(cls)
        z = z / z.norm(dim=-1, keepdim=True)
        return z
