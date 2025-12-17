# %%
# !pip install transformers datasets accelerate sentencepiece protobuf==4.25.3
# !pip install torch torchvision torchaudio

# %% [markdown]
# # Hyperparameters configuration

# %%
# Model Configuration
MODEL_NAME = "bert-base-multilingual-cased"
PROJECTION_DIM = 256  # Dimension of projection head output

# Tokenizer & Data Configuration
MAX_LENGTH = 128  # Maximum sequence length (increase for longer texts)

# Training Configuration
BATCH_SIZE = 64  # Larger batch = more negative pairs = better contrastive learning
LEARNING_RATE = 5e-5  # Learning rate (try 3e-5, 5e-5, 1e-4)
NUM_EPOCHS = 10  # Number of training epochs
WARMUP_RATIO = 0.1  # Warmup steps ratio

# Contrastive Loss Configuration
TEMPERATURE = 0.2  # Temperature for contrastive loss (0.1-0.5 for text-text)
                   # Lower = harder negatives, Higher = softer negatives

# Evaluation Configuration
EVAL_BATCH_SIZE = 64  # Batch size for evaluation
EVAL_STRATEGY = "epoch"  # When to evaluate: "steps" or "epoch"
LOGGING_STEPS = 50  # Log every N steps

# Save Configuration
SAVE_STRATEGY = "epoch"  # When to save: "steps" or "epoch"
SAVE_TOTAL_LIMIT = 3  # Keep only best 3 checkpoints

# W&B Configuration
WANDB_PROJECT = "contrastive-travel-search"
WANDB_RUN_NAME = f"clip_bs{BATCH_SIZE}_lr{LEARNING_RATE}_temp{TEMPERATURE}"

# Random Seed
RANDOM_SEED = 42

# Device
DEVICE = "cuda"  # Will be set automatically in code

print("=" * 70)
print("HYPERPARAMETERS SUMMARY")
print("=" * 70)
print(f"Model: {MODEL_NAME}")
print(f"Max Length: {MAX_LENGTH}")
print(f"Batch Size: {BATCH_SIZE}")
print(f"Learning Rate: {LEARNING_RATE}")
print(f"Temperature: {TEMPERATURE}")
print(f"Epochs: {NUM_EPOCHS}")
print(f"Projection Dim: {PROJECTION_DIM}")
print("=" * 70)

# %%
import wandb
# !wandb login 
wandb.init(
    project=WANDB_PROJECT,   
    name=WANDB_RUN_NAME,              
    config={
        "epochs": NUM_EPOCHS,
        "batch_size": BATCH_SIZE,
        "lr": LEARNING_RATE,
        "temperature": TEMPERATURE,
        "model": MODEL_NAME,
        "max_length": MAX_LENGTH,
        "projection_dim": PROJECTION_DIM
    }
)

# %% [markdown]
# # Read data

# %%
import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("/kaggle/input/naviagent-description-destination-pairs/travel_dataset_10k.csv")

df = df.dropna(subset=["description", "destination"])

# Ép kiểu string để an toàn
df["description"] = df["description"].astype(str).str.strip()
df["destination"] = df["destination"].astype(str).str.strip()


train_df, val_df = train_test_split(
    df, test_size=0.2, random_state=RANDOM_SEED, shuffle=True
)

train_df = train_df.reset_index(drop=True)
val_df = val_df.reset_index(drop=True)

len(train_df), len(val_df)

# %% [markdown]
# # Tokenize

# %%
from torch.utils.data import Dataset
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

class ContrastiveDataset(Dataset):
    def __init__(self, df, tokenizer, max_len=MAX_LENGTH):
        self.df = df
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        row = self.df.iloc[idx]

        anc = row["description"]
        pos = row["destination"]

        enc_anc = self.tokenizer(
            anc, truncation=True, padding="max_length",
            max_length=self.max_len, return_tensors="pt"
        )
        enc_pos = self.tokenizer(
            pos, truncation=True, padding="max_length",
            max_length=self.max_len, return_tensors="pt"
        )

        return {
            "anchor_input_ids": enc_anc["input_ids"].squeeze(),
            "anchor_attention": enc_anc["attention_mask"].squeeze(),
            "pos_input_ids":     enc_pos["input_ids"].squeeze(),
            "pos_attention":     enc_pos["attention_mask"].squeeze(),
        }

train_dataset = ContrastiveDataset(train_df, tokenizer)
val_dataset   = ContrastiveDataset(val_df, tokenizer)

# %% [markdown]
# # Model

# %%
import torch
import torch.nn as nn
from transformers import AutoModel

class TextTextCLIPModel(nn.Module):
    def __init__(self, model_name=MODEL_NAME, proj_dim=PROJECTION_DIM):
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

# %%
from transformers import Trainer, TrainingArguments

def contrastive_loss(z1, z2, temperature=TEMPERATURE):
    logits = (z1 @ z2.T) / temperature
    labels = torch.arange(len(z1)).to(z1.device)
    return nn.CrossEntropyLoss()(logits, labels)

class CLIPTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        # dùng anchor làm batch trái, pos làm batch phải
        z1 = model(
            input_ids=inputs["anchor_input_ids"],
            attention_mask=inputs["anchor_attention"]
        )
        z2 = model(
            input_ids=inputs["pos_input_ids"],
            attention_mask=inputs["pos_attention"]
        )

        loss = contrastive_loss(z1, z2)

        return (loss, {"z1": z1, "z2": z2}) if return_outputs else loss

    def prediction_step(
        self,
        model,
        inputs,
        prediction_loss_only,
        ignore_keys=None,
    ):
        """
        Override prediction_step để:
        - KHÔNG gọi model(**inputs)
        - tự tính loss như compute_loss
        """

        with torch.no_grad():
            z1 = model(
                input_ids=inputs["anchor_input_ids"],
                attention_mask=inputs["anchor_attention"]
            )
            z2 = model(
                input_ids=inputs["pos_input_ids"],
                attention_mask=inputs["pos_attention"]
            )

            loss = contrastive_loss(z1, z2)

        if prediction_loss_only:
            return (loss, None, None)

        return (loss, z1, z2)

# %%
device = "cuda" if torch.cuda.is_available() else "cpu"

model = TextTextCLIPModel().to(device)

training_args = TrainingArguments(
    output_dir="./clip-text-text",
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=EVAL_BATCH_SIZE,
    eval_strategy=EVAL_STRATEGY,
    save_strategy=SAVE_STRATEGY,
    save_total_limit=SAVE_TOTAL_LIMIT,
    num_train_epochs=NUM_EPOCHS,
    learning_rate=LEARNING_RATE,
    warmup_ratio=WARMUP_RATIO,
    logging_steps=LOGGING_STEPS,
    remove_unused_columns=False,   # bắt buộc cho custom Trainer
    report_to='wandb',
    seed=RANDOM_SEED
)

trainer = CLIPTrainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset
)

# %%
trainer.train()

# %%
import pandas as pd

trainer.state.log_history

# Convert log history to DataFrame
logs = pd.DataFrame(trainer.state.log_history)

# Lọc log chứa loss
df_loss = logs[logs["loss"].notna()][["step", "loss"]]
df_eval = logs[logs["eval_loss"].notna()][["step", "eval_loss"]]

df_loss.head(), df_eval.head()

# %%
import matplotlib.pyplot as plt

plt.figure(figsize=(8,6))

# Train loss
plt.plot(df_loss["step"], df_loss["loss"], label="Train Loss", linewidth=2)

# Eval loss
plt.plot(df_eval["step"], df_eval["eval_loss"], label="Dev Loss", linewidth=2)

plt.xlabel("Training Steps")
plt.ylabel("Loss")
plt.title("Training vs Dev Loss Curve")
plt.legend()
plt.grid(True)
plt.show()

# %% [markdown]
# # Evaluation on dev set

# %%
import torch
import numpy as np
from tqdm import tqdm

def encode_texts_anchor(dataset, model, tokenizer, batch_size=64):
    """Encode anchor texts (descriptions)"""
    model.eval()
    all_vecs = []

    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=False)

    with torch.no_grad():
        for batch in tqdm(loader, desc="Encoding anchors"):
            ids = batch["anchor_input_ids"].to(device)
            att = batch["anchor_attention"].to(device)

            z = model(ids, att)
            all_vecs.append(z.cpu())

    all_vecs = torch.cat(all_vecs, dim=0)
    return all_vecs

def encode_texts_pos(dataset, model, tokenizer, batch_size=64):
    """Encode positive texts (destinations)"""
    model.eval()
    all_vecs = []

    loader = torch.utils.data.DataLoader(dataset, batch_size=batch_size, shuffle=False)

    with torch.no_grad():
        for batch in tqdm(loader, desc="Encoding positives"):
            ids = batch["pos_input_ids"].to(device)
            att = batch["pos_attention"].to(device)

            z = model(ids, att)
            all_vecs.append(z.cpu())

    all_vecs = torch.cat(all_vecs, dim=0)
    return all_vecs

# %%
emb_anchor = encode_texts_anchor(val_dataset, model, tokenizer)
emb_pos = encode_texts_pos(val_dataset, model, tokenizer)

# similarity matrix: (N × N)
sim = emb_anchor @ emb_pos.T
sim = sim.numpy()

# %%
def compute_recall(sim, k):
    """Recall@K: Tỉ lệ mẫu có kết quả đúng trong top K"""
    ranks = np.argsort(-sim, axis=1)  # sort desc
    correct = 0
    for i in range(len(sim)):
        if i in ranks[i, :k]:
            correct += 1
    return correct / len(sim)

def compute_precision(sim, k):
    """Precision@K: Tỉ lệ kết quả đúng trong top K (với 1 positive, precision = recall/k hoặc đơn giản hơn)"""
    ranks = np.argsort(-sim, axis=1)
    correct = 0
    for i in range(len(sim)):
        if i in ranks[i, :k]:
            correct += 1
    # Với mỗi query chỉ có 1 positive, precision@k = (số lần tìm thấy trong top k) / (tổng số query * k)
    return correct / (len(sim) * k)

def compute_f1(precision, recall):
    """F1 Score: Trung bình điều hòa của precision và recall"""
    if precision + recall == 0:
        return 0
    return 2 * (precision * recall) / (precision + recall)

def compute_mrr(sim):
    """MRR (Mean Reciprocal Rank): Trung bình nghịch đảo của rank đầu tiên tìm thấy kết quả đúng
    
    Ví dụ: 
    - Nếu kết quả đúng ở vị trí 1 → điểm = 1/1 = 1.0
    - Nếu kết quả đúng ở vị trí 3 → điểm = 1/3 = 0.333
    - Nếu kết quả đúng ở vị trí 10 → điểm = 1/10 = 0.1
    """
    ranks = np.argsort(-sim, axis=1)
    mrr = 0
    for i in range(len(sim)):
        rank = np.where(ranks[i] == i)[0][0]  # index of correct
        mrr += 1 / (rank + 1)
    return mrr / len(sim)

# Calculate metrics
recall1  = compute_recall(sim, 1)
recall5  = compute_recall(sim, 5)
recall10 = compute_recall(sim, 10)

precision1  = compute_precision(sim, 1)
precision5  = compute_precision(sim, 5)
precision10 = compute_precision(sim, 10)

f1_1  = compute_f1(precision1, recall1)
f1_5  = compute_f1(precision5, recall5)
f1_10 = compute_f1(precision10, recall10)

mrr = compute_mrr(sim)

print("=" * 60)
print("EVALUATION METRICS ON VALIDATION SET")
print("=" * 60)
print(f"Recall@1      : {recall1:.4f}")
print(f"Recall@5      : {recall5:.4f}")
print(f"Recall@10     : {recall10:.4f}")
print("-" * 60)
print(f"Precision@1   : {precision1:.4f}")
print(f"Precision@5   : {precision5:.4f}")
print(f"Precision@10  : {precision10:.4f}")
print("-" * 60)
print(f"F1@1          : {f1_1:.4f}")
print(f"F1@5          : {f1_5:.4f}")
print(f"F1@10         : {f1_10:.4f}")
print("-" * 60)
print(f"MRR           : {mrr:.4f}")
print("=" * 60)

# %%
import matplotlib.pyplot as plt

sample = sim[:100, :100]

plt.figure(figsize=(8, 6))
plt.imshow(sample)
plt.colorbar()
plt.title("Similarity Heatmap (first 100 samples)")
plt.show()

# %%
# Positive scores: diagonal (description[i] vs destination[i])
pos_scores = sim.diagonal()

# Negative scores: all off-diagonal elements
neg_mask = ~np.eye(sim.shape[0], dtype=bool)
neg_scores = sim[neg_mask]

print(f"Number of positive pairs: {len(pos_scores)}")
print(f"Number of negative pairs: {len(neg_scores)}")
print(f"Mean positive score: {pos_scores.mean():.4f} ± {pos_scores.std():.4f}")
print(f"Mean negative score: {neg_scores.mean():.4f} ± {neg_scores.std():.4f}")
print(f"Positive score range: [{pos_scores.min():.4f}, {pos_scores.max():.4f}]")
print(f"Negative score range: [{neg_scores.min():.4f}, {neg_scores.max():.4f}]")

plt.figure(figsize=(12,6))

# Vẽ negative trước (ở dưới)
plt.hist(neg_scores, bins=50, alpha=0.4, label=f"Negative (n={len(neg_scores):,})", 
         color='red', edgecolor='darkred', linewidth=0.5)

# Vẽ positive sau (ở trên) với alpha cao hơn và viền đậm
plt.hist(pos_scores, bins=50, alpha=0.9, label=f"Positive (n={len(pos_scores):,})", 
         color='green', edgecolor='darkgreen', linewidth=2)

plt.legend(fontsize=11)
plt.title("Similarity Distribution: Positive vs Negative Pairs", fontsize=14, fontweight='bold')
plt.xlabel("Cosine Similarity", fontsize=12)
plt.ylabel("Count", fontsize=12)
plt.grid(True, alpha=0.3)

# Thêm đường thẳng đứng cho mean
plt.axvline(pos_scores.mean(), color='darkgreen', linestyle='--', linewidth=2, alpha=0.7, label=f'Pos Mean: {pos_scores.mean():.3f}')
plt.axvline(neg_scores.mean(), color='darkred', linestyle='--', linewidth=2, alpha=0.7, label=f'Neg Mean: {neg_scores.mean():.3f}')
plt.legend(fontsize=10)

plt.tight_layout()
plt.show()

# %%
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# Recall@K
axes[0].plot([1, 5, 10], [recall1, recall5, recall10], marker="o", linewidth=2, markersize=8, color='blue')
axes[0].set_title("Recall@K", fontsize=14, fontweight='bold')
axes[0].set_xlabel("K", fontsize=12)
axes[0].set_ylabel("Recall", fontsize=12)
axes[0].grid(True, alpha=0.3)
axes[0].set_ylim([0, 1])

# Precision@K
axes[1].plot([1, 5, 10], [precision1, precision5, precision10], marker="s", linewidth=2, markersize=8, color='green')
axes[1].set_title("Precision@K", fontsize=14, fontweight='bold')
axes[1].set_xlabel("K", fontsize=12)
axes[1].set_ylabel("Precision", fontsize=12)
axes[1].grid(True, alpha=0.3)
axes[1].set_ylim([0, 1])

# F1@K
axes[2].plot([1, 5, 10], [f1_1, f1_5, f1_10], marker="^", linewidth=2, markersize=8, color='orange')
axes[2].set_title("F1@K", fontsize=14, fontweight='bold')
axes[2].set_xlabel("K", fontsize=12)
axes[2].set_ylabel("F1 Score", fontsize=12)
axes[2].grid(True, alpha=0.3)
axes[2].set_ylim([0, 1])

plt.tight_layout()
plt.show()

# %%
trainer.save_model("contrastive_text_model")

# %%
# Precompute embeddings for all descriptions
all_embeddings = []

def get_text_embedding(text, model, tokenizer):
    model.eval()
    enc = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        padding=True,
        max_length=MAX_LENGTH
    )
    with torch.no_grad():
        z = model(
            input_ids=enc["input_ids"].to(device),
            attention_mask=enc["attention_mask"].to(device)
        )
    return z.cpu()

model.eval()
for text in tqdm(df["description"].tolist(), desc="Precomputing embeddings"):
    z = get_text_embedding(text, model, tokenizer)
    all_embeddings.append(z)

emb_matrix = torch.cat(all_embeddings, dim=0)  # (N, dim)
torch.save(emb_matrix, "emb_matrix.pt")

# %%
def search_query(query, model, tokenizer, emb_matrix, df, k=5):
    q = get_text_embedding(query, model, tokenizer)  # (1, dim)
    q = q / q.norm(dim=-1, keepdim=True)

    # similarity (1 × N)
    sims = (q @ emb_matrix.T).numpy()[0]

    # Top-K
    idx = sims.argsort()[::-1][:k]

    results = []
    for rank, i in enumerate(idx, start=1):
        results.append({
            "rank": rank,
            "destination": df.iloc[i]["destination"],
            "description": df.iloc[i]["description"],
            "similarity": float(sims[i])
        })
    return results

query = "beatiful beach with clean and clear water, luxurious service"
results = search_query(query, model, tokenizer, emb_matrix, df)

for r in results:
    print("-" * 50)
    print(f"Rank {r['rank']}")
    print(f"Destination: {r['destination']}")
    print(f"Similarity: {r['similarity']:.4f}")
    print(f"Description: {r['description']}")

# %%
wandb.finish()


