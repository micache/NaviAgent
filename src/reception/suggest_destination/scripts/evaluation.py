# %%
# !pip install protobuf==4.25.3

# %%
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModel
from safetensors.torch import load_file
from typing import Dict, List
import matplotlib.pyplot as plt
from collections import defaultdict

# %%
df = pd.read_csv("/kaggle/input/naviagent-test-set/naviagent.csv")
df = df.sample(n=50, random_state=0)
descriptions = df["description"].tolist()
destinations = df["destination"].tolist()

print(f"Number of rows: {len(df)}")

# %%
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

# %%
MODEL_NAME = 'google-bert/bert-base-multilingual-cased'
MODEL_DIR = "/kaggle/input/naviagent-trained-contrastive-model/pytorch/default/1/contrastive_text_model/model.safetensors"   # folder chứa safetensors + config
PROJ_DIM = 256
MAX_LENGTH = 128

device = "cuda" if torch.cuda.is_available() else "cpu"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = TextTextCLIPModel(
    model_name=MODEL_NAME,
    proj_dim=PROJ_DIM
)
state_dict = load_file(MODEL_DIR)
model.load_state_dict(state_dict)
model.to(device)
model.eval()

print("Loaded model architecture + tokenizer from:", MODEL_DIR)

# %%
def preprocess(text: str) -> Dict[str, torch.Tensor]:
    """Tokenize text"""
    encoded = tokenizer(
        text,
        max_length=MAX_LENGTH,
        padding="max_length",
        truncation=True,
        return_tensors="pt",
    )
    return {
        "input_ids": encoded["input_ids"].to(device),
        "attention_mask": encoded["attention_mask"].to(device),
    }

# %%
def encode(text_list):
    embeddings = []

    for text in text_list:
        batch = preprocess(text)

        with torch.no_grad():
            emb = model(**batch)      # returns [1, dim] tensor
            emb = torch.nn.functional.normalize(emb, p=2, dim=1)
            embeddings.append(emb.cpu())

    return torch.cat(embeddings, dim=0)

# %%
print("Encoding descriptions...")
description_emb = encode(descriptions)

print("Encoding destinations...")
destination_emb = encode(destinations)

# %%
similarity = description_emb @ destination_emb.T
ranking = torch.argsort(similarity, dim=1, descending=True)

# %%
def create_destination_mapping(df):
    """
    Tạo dictionary ánh xạ destination -> list các indices có cùng destination
    """
    dest_to_indices = defaultdict(list)
    for idx, dest in enumerate(df["destination"]):
        dest_to_indices[dest].append(idx)
    return dest_to_indices

# Bước 2: Tính Recall@K với group-aware evaluation
def recall_at_k_group_aware(ranking, df, k):
    """
    Tính Recall@K với việc chấp nhận bất kỳ description nào cùng destination
    
    Args:
        ranking: tensor [N, N] - ranked indices
        df: DataFrame chứa destination info
        k: số top results cần xét
    
    Returns:
        recall: float - tỷ lệ queries tìm được ít nhất 1 positive
    """
    dest_to_indices = create_destination_mapping(df)
    
    correct = 0
    total = len(ranking)
    
    for i in range(total):
        # Lấy destination của query hiện tại
        query_dest = df.iloc[i]["destination"]
        
        # Lấy tất cả indices có cùng destination (bao gồm cả chính nó)
        positive_indices = set(dest_to_indices[query_dest])
        
        # Lấy top-k predictions
        top_k_preds = ranking[i, :k].tolist()
        
        # Check xem có ít nhất 1 prediction trong positive set không
        if any(pred in positive_indices for pred in top_k_preds):
            correct += 1
    
    return correct / total

# Bước 3: Tính Mean Average Precision (MAP) - metric tốt hơn cho multi-positive
def mean_average_precision(ranking, df, k=10):
    """
    Tính MAP@K - xem xét tất cả positive items trong top-K
    """
    dest_to_indices = create_destination_mapping(df)
    
    aps = []
    
    for i in range(len(ranking)):
        query_dest = df.iloc[i]["destination"]
        positive_indices = set(dest_to_indices[query_dest])
        # Loại bỏ chính query index ra khỏi positive set
        positive_indices.discard(i)
        
        if len(positive_indices) == 0:
            continue
            
        top_k_preds = ranking[i, :k].tolist()
        
        # Tính Average Precision
        num_hits = 0
        sum_precisions = 0
        
        for rank, pred in enumerate(top_k_preds, 1):
            if pred in positive_indices:
                num_hits += 1
                precision_at_rank = num_hits / rank
                sum_precisions += precision_at_rank
        
        if num_hits > 0:
            ap = sum_precisions / min(len(positive_indices), k)
        else:
            ap = 0.0
            
        aps.append(ap)
    
    return np.mean(aps) if aps else 0.0

# Bước 4: Visualize similarity distribution với group-aware
def plot_similarity_distribution_group_aware(similarity, df):
    """
    Vẽ histogram phân biệt:
    - Same destination (positive pairs)
    - Different destination (negative pairs)
    """
    dest_to_indices = create_destination_mapping(df)
    
    positive_sims = []
    negative_sims = []
    
    N = similarity.shape[0]
    sim_np = similarity.numpy()
    
    for i in range(N):
        query_dest = df.iloc[i]["destination"]
        positive_indices = set(dest_to_indices[query_dest])
        positive_indices.discard(i)  # Loại bỏ chính nó
        
        for j in range(N):
            if i == j:
                continue
            
            if j in positive_indices:
                positive_sims.append(sim_np[i, j])
            else:
                negative_sims.append(sim_np[i, j])
    
    positive_sims = np.array(positive_sims)
    negative_sims = np.array(negative_sims)
    
    # Histogram
    bins = np.linspace(-1, 1, 80)
    
    pos_hist, _ = np.histogram(positive_sims, bins=bins, density=True)
    neg_hist, _ = np.histogram(negative_sims, bins=bins, density=True)
    
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    plt.figure(figsize=(10, 6))
    
    plt.plot(bin_centers, pos_hist, label="Same Destination (Positive)", linewidth=2, color='green')
    plt.plot(bin_centers, neg_hist, label="Different Destination (Negative)", linewidth=2, color='red')
    
    # Thêm statistics
    plt.axvline(positive_sims.mean(), color='green', linestyle='--', alpha=0.7, 
                label=f'Pos Mean: {positive_sims.mean():.3f}')
    plt.axvline(negative_sims.mean(), color='red', linestyle='--', alpha=0.7,
                label=f'Neg Mean: {negative_sims.mean():.3f}')
    
    plt.title("Similarity Distribution: Same vs Different Destination")
    plt.xlabel("Cosine Similarity")
    plt.ylabel("Density")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    # Print statistics
    print("="*60)
    print("Similarity Statistics:")
    print(f"Positive pairs - Mean: {positive_sims.mean():.4f}, Std: {positive_sims.std():.4f}")
    print(f"Negative pairs - Mean: {negative_sims.mean():.4f}, Std: {negative_sims.std():.4f}")
    print(f"Separation: {positive_sims.mean() - negative_sims.mean():.4f}")
    print("="*60)

# Bước 5: Chạy evaluation
def run_evaluation(df, similarity, ranking):
    """
    Chạy toàn bộ evaluation pipeline
    """
    print("="*60)
    print("GROUP-AWARE EVALUATION")
    print("="*60)
    
    # Recall@K
    ks = [1, 5, 10, 20]
    recalls = []
    
    for k in ks:
        recall = recall_at_k_group_aware(ranking, df, k)
        recalls.append(recall)
        print(f"Recall@{k:2d} = {recall:.4f}")
    
    # MAP
    map_score = mean_average_precision(ranking, df, k=10)
    print(f"\nMAP@10    = {map_score:.4f}")
    
    print("="*60)
    
    # Visualize
    plot_similarity_distribution_group_aware(similarity, df)
    
    # Plot Recall curve
    plt.figure(figsize=(8, 5))
    plt.plot(ks, recalls, marker='o', linewidth=2, markersize=8)
    plt.title("Recall@K")
    plt.xlabel("K")
    plt.ylabel("Recall")
    plt.xticks(ks)
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    return recalls, map_score

# MAIN EXECUTION
# Giả sử bạn đã có df, similarity, ranking từ code cũ
# Chỉ cần gọi:
recalls, map_score = run_evaluation(df, similarity, ranking)

# Bonus: Analyze per-destination performance
def analyze_per_destination(df, similarity, ranking, top_k=10):
    """
    Phân tích performance cho từng destination
    """
    dest_to_indices = create_destination_mapping(df)
    
    results = []
    
    for dest, indices in dest_to_indices.items():
        if len(indices) <= 1:  # Skip destinations với chỉ 1 description
            continue
        
        correct = 0
        for i in indices:
            positive_indices = set(indices)
            positive_indices.discard(i)
            
            top_k_preds = ranking[i, :top_k].tolist()
            
            if any(pred in positive_indices for pred in top_k_preds):
                correct += 1
        
        recall = correct / len(indices)
        results.append({
            'destination': dest,
            'num_descriptions': len(indices),
            'recall@10': recall
        })
    
    results_df = pd.DataFrame(results).sort_values('recall@10')
    
    print("\n" + "="*60)
    print("PER-DESTINATION ANALYSIS")
    print("="*60)
    print(f"\nWorst 5 destinations:")
    print(results_df.head())
    print(f"\nBest 5 destinations:")
    print(results_df.tail())
    print("="*60)
    
    return results_df

# Chạy phân tích per-destination
dest_analysis = analyze_per_destination(df, similarity, ranking)

# %%
import torch
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict

# Giả sử bạn đã có:
# - df: DataFrame với columns ["description", "destination"]
# - similarity: tensor [N, N] chứa cosine similarity
# - ranking: tensor [N, N] chứa indices được sắp xếp theo similarity

# Bước 1: Tạo mapping destination -> list of indices
def create_destination_mapping(df):
    """
    Tạo dictionary ánh xạ destination -> list các indices có cùng destination
    """
    dest_to_indices = defaultdict(list)
    for idx, dest in enumerate(df["destination"]):
        dest_to_indices[dest].append(idx)
    return dest_to_indices

# Bước 2: Tính Recall@K với group-aware evaluation
def recall_at_k_group_aware(ranking, df, k):
    """
    Tính Recall@K với việc chấp nhận bất kỳ description nào cùng destination
    
    Args:
        ranking: tensor [N, N] - ranked indices
        df: DataFrame chứa destination info
        k: số top results cần xét
    
    Returns:
        recall: float - tỷ lệ queries tìm được ít nhất 1 positive
    """
    dest_to_indices = create_destination_mapping(df)
    
    correct = 0
    total = len(ranking)
    
    for i in range(total):
        # Lấy destination của query hiện tại
        query_dest = df.iloc[i]["destination"]
        
        # Lấy tất cả indices có cùng destination (bao gồm cả chính nó)
        positive_indices = set(dest_to_indices[query_dest])
        
        # Lấy top-k predictions
        top_k_preds = ranking[i, :k].tolist()
        
        # Check xem có ít nhất 1 prediction trong positive set không
        if any(pred in positive_indices for pred in top_k_preds):
            correct += 1
    
    return correct / total

# Bước 3: Tính Mean Average Precision (MAP) - metric tốt hơn cho multi-positive
def mean_average_precision(ranking, df, k=10):
    """
    Tính MAP@K - xem xét tất cả positive items trong top-K
    """
    dest_to_indices = create_destination_mapping(df)
    
    aps = []
    
    for i in range(len(ranking)):
        query_dest = df.iloc[i]["destination"]
        positive_indices = set(dest_to_indices[query_dest])
        # Loại bỏ chính query index ra khỏi positive set
        positive_indices.discard(i)
        
        if len(positive_indices) == 0:
            continue
            
        top_k_preds = ranking[i, :k].tolist()
        
        # Tính Average Precision
        num_hits = 0
        sum_precisions = 0
        
        for rank, pred in enumerate(top_k_preds, 1):
            if pred in positive_indices:
                num_hits += 1
                precision_at_rank = num_hits / rank
                sum_precisions += precision_at_rank
        
        if num_hits > 0:
            ap = sum_precisions / min(len(positive_indices), k)
        else:
            ap = 0.0
            
        aps.append(ap)
    
    return np.mean(aps) if aps else 0.0

# Bước 4: Visualize similarity distribution với group-aware
def plot_similarity_distribution_group_aware(similarity, df):
    """
    Vẽ histogram phân biệt với smoothing:
    - Same destination (positive pairs)
    - Different destination (negative pairs)
    """
    from scipy.ndimage import gaussian_filter1d
    
    dest_to_indices = create_destination_mapping(df)
    
    positive_sims = []
    negative_sims = []
    
    N = similarity.shape[0]
    sim_np = similarity.numpy()
    
    for i in range(N):
        query_dest = df.iloc[i]["destination"]
        positive_indices = set(dest_to_indices[query_dest])
        positive_indices.discard(i)  # Loại bỏ chính nó
        
        for j in range(N):
            if i == j:
                continue
            
            if j in positive_indices:
                positive_sims.append(sim_np[i, j])
            else:
                negative_sims.append(sim_np[i, j])
    
    positive_sims = np.array(positive_sims)
    negative_sims = np.array(negative_sims)
    
    # Histogram với bins mịn hơn
    bins = np.linspace(-1, 1, 150)
    
    pos_hist, _ = np.histogram(positive_sims, bins=bins, density=True)
    neg_hist, _ = np.histogram(negative_sims, bins=bins, density=True)
    
    bin_centers = (bins[:-1] + bins[1:]) / 2
    
    # Gaussian smoothing cho đường cong mượt hơn
    sigma = 3  # Điều chỉnh độ mịn (càng cao càng mịn)
    pos_hist_smooth = gaussian_filter1d(pos_hist, sigma=sigma)
    neg_hist_smooth = gaussian_filter1d(neg_hist, sigma=sigma)
    
    plt.figure(figsize=(12, 7))
    
    # Plot với fill_between để đẹp hơn
    plt.plot(bin_centers, pos_hist_smooth, label="Same Destination (Positive)", 
             linewidth=2.5, color='#2ecc71', alpha=0.9)
    plt.fill_between(bin_centers, 0, pos_hist_smooth, alpha=0.2, color='#2ecc71')
    
    plt.plot(bin_centers, neg_hist_smooth, label="Different Destination (Negative)", 
             linewidth=2.5, color='#e74c3c', alpha=0.9)
    plt.fill_between(bin_centers, 0, neg_hist_smooth, alpha=0.2, color='#e74c3c')
    
    # Thêm statistics với style đẹp hơn
    plt.axvline(positive_sims.mean(), color='#27ae60', linestyle='--', alpha=0.8, 
                linewidth=2, label=f'Pos Mean: {positive_sims.mean():.3f}')
    plt.axvline(negative_sims.mean(), color='#c0392b', linestyle='--', alpha=0.8,
                linewidth=2, label=f'Neg Mean: {negative_sims.mean():.3f}')
    
    plt.title("Similarity Distribution: Same vs Different Destination", 
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel("Cosine Similarity", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.legend(fontsize=10, loc='upper left', framealpha=0.9)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.xlim(-1, 1)
    plt.tight_layout()
    plt.show()
    
    # Print statistics
    print("="*60)
    print("Similarity Statistics:")
    print(f"Positive pairs - Mean: {positive_sims.mean():.4f}, Std: {positive_sims.std():.4f}")
    print(f"                 Min: {positive_sims.min():.4f}, Max: {positive_sims.max():.4f}")
    print(f"Negative pairs - Mean: {negative_sims.mean():.4f}, Std: {negative_sims.std():.4f}")
    print(f"                 Min: {negative_sims.min():.4f}, Max: {negative_sims.max():.4f}")
    print(f"Separation: {positive_sims.mean() - negative_sims.mean():.4f}")
    print(f"Overlap: {np.sum((positive_sims < negative_sims.mean()))/len(positive_sims)*100:.1f}% pos < neg_mean")
    print("="*60)

# Bước 5: Chạy evaluation
def run_evaluation(df, similarity, ranking):
    """
    Chạy toàn bộ evaluation pipeline
    """
    print("="*60)
    print("GROUP-AWARE EVALUATION")
    print("="*60)
    
    # Recall@K
    ks = [1, 5, 10, 20]
    recalls = []
    
    for k in ks:
        recall = recall_at_k_group_aware(ranking, df, k)
        recalls.append(recall)
        print(f"Recall@{k:2d} = {recall:.4f}")
    
    # MAP
    map_score = mean_average_precision(ranking, df, k=10)
    print(f"\nMAP@10    = {map_score:.4f}")
    
    print("="*60)
    
    # Visualize
    plot_similarity_distribution_group_aware(similarity, df)
    
    # Plot Recall curve với style đẹp hơn
    plt.figure(figsize=(10, 6))
    plt.plot(ks, recalls, marker='o', linewidth=3, markersize=10, 
             color='#3498db', markerfacecolor='#2980b9', markeredgewidth=2, 
             markeredgecolor='white', label='Recall@K')
    
    # Thêm values trên từng điểm
    for k, r in zip(ks, recalls):
        plt.annotate(f'{r:.3f}', (k, r), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=10, fontweight='bold')
    
    plt.title("Recall@K", fontsize=14, fontweight='bold', pad=20)
    plt.xlabel("K", fontsize=12)
    plt.ylabel("Recall", fontsize=12)
    plt.xticks(ks, fontsize=11)
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3, linestyle='--')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.show()
    
    return recalls, map_score

# MAIN EXECUTION
# Giả sử bạn đã có df, similarity, ranking từ code cũ
# Chỉ cần gọi:
recalls, map_score = run_evaluation(df, similarity, ranking)

# ============================================================================
# TRICKS TO BOOST RECALL@K
# ============================================================================

def trick_1_rerank_with_reciprocal(similarity, top_k=100):
    """
    TRICK 1: Reciprocal Rank Fusion (RRF)
    - Kết hợp similarity từ 2 chiều: query->doc và doc->query
    - Thường tăng 2-5% recall
    """
    N = similarity.shape[0]
    
    # Original ranking (query -> doc)
    ranking_forward = torch.argsort(similarity, dim=1, descending=True)
    
    # Reverse ranking (doc -> query)
    ranking_backward = torch.argsort(similarity.T, dim=1, descending=True)
    
    # RRF scoring
    rrf_scores = torch.zeros_like(similarity)
    k_rrf = 60  # RRF constant
    
    for i in range(N):
        for rank, j in enumerate(ranking_forward[i, :top_k]):
            rrf_scores[i, j] += 1 / (k_rrf + rank + 1)
        
        # Add reverse scores
        for rank, j in enumerate(ranking_backward[i, :top_k]):
            rrf_scores[j, i] += 1 / (k_rrf + rank + 1)
    
    # Re-rank based on RRF scores
    new_ranking = torch.argsort(rrf_scores, dim=1, descending=True)
    
    return new_ranking, rrf_scores

def trick_2_query_expansion(description_emb, destination_emb, df, alpha=0.3, top_k_expand=3):
    """
    TRICK 2: Query Expansion
    - Mở rộng query bằng cách thêm top-k similar descriptions
    - Có thể tăng 3-7% recall
    """
    # Compute initial similarity
    similarity = description_emb @ destination_emb.T
    ranking = torch.argsort(similarity, dim=1, descending=True)
    
    # Query expansion
    expanded_queries = []
    
    for i in range(len(description_emb)):
        # Lấy top-k similar descriptions (excluding itself)
        top_k_idx = ranking[i, 1:top_k_expand+1]
        
        # Weighted sum: original + alpha * mean(top-k)
        expanded_query = description_emb[i] + alpha * destination_emb[top_k_idx].mean(dim=0)
        expanded_query = torch.nn.functional.normalize(expanded_query, p=2, dim=0)
        
        expanded_queries.append(expanded_query)
    
    expanded_emb = torch.stack(expanded_queries)
    
    # Re-compute similarity
    new_similarity = expanded_emb @ destination_emb.T
    new_ranking = torch.argsort(new_similarity, dim=1, descending=True)
    
    return new_ranking, new_similarity

def trick_3_hard_negative_mining_reweight(similarity, df, margin=0.1):
    """
    TRICK 3: Re-weight based on hard negatives
    - Tăng weight cho hard negatives để phân biệt rõ hơn
    - Hữu ích khi có nhiều destinations tương tự nhau
    """
    dest_to_indices = create_destination_mapping(df)
    N = similarity.shape[0]
    
    adjusted_similarity = similarity.clone()
    
    for i in range(N):
        query_dest = df.iloc[i]["destination"]
        positive_indices = set(dest_to_indices[query_dest])
        
        # Tìm hard negatives (high similarity but wrong destination)
        for j in range(N):
            if j not in positive_indices and similarity[i, j] > similarity[i, i] - margin:
                # Penalty for hard negatives
                adjusted_similarity[i, j] -= 0.05
    
    new_ranking = torch.argsort(adjusted_similarity, dim=1, descending=True)
    return new_ranking, adjusted_similarity

def trick_4_ensemble_rankings(rankings_list, weights=None):
    """
    TRICK 4: Ensemble multiple ranking strategies
    - Kết hợp nhiều phương pháp ranking
    - Thường tốt hơn từng phương pháp riêng lẻ
    """
    if weights is None:
        weights = [1.0] * len(rankings_list)
    
    N = rankings_list[0].shape[0]
    K = rankings_list[0].shape[1]
    
    # Borda count ensemble
    final_scores = torch.zeros((N, N))
    
    for ranking, weight in zip(rankings_list, weights):
        for i in range(N):
            for rank, j in enumerate(ranking[i]):
                # Higher rank = higher score
                final_scores[i, j] += weight * (K - rank)
    
    ensemble_ranking = torch.argsort(final_scores, dim=1, descending=True)
    return ensemble_ranking

def apply_all_tricks(description_emb, destination_emb, df, similarity, ranking):
    """
    Áp dụng tất cả tricks và so sánh kết quả
    """
    print("\n" + "="*60)
    print("APPLYING TRICKS TO BOOST RECALL@K")
    print("="*60)
    
    results = {}
    
    # Original
    print("\n[BASELINE]")
    r1 = recall_at_k_group_aware(ranking, df, 1)
    r5 = recall_at_k_group_aware(ranking, df, 5)
    r10 = recall_at_k_group_aware(ranking, df, 10)
    print(f"Recall@1={r1:.4f}, Recall@5={r5:.4f}, Recall@10={r10:.4f}")
    results['baseline'] = [r1, r5, r10]
    
    # Trick 1: RRF
    print("\n[TRICK 1: Reciprocal Rank Fusion]")
    rrf_ranking, _ = trick_1_rerank_with_reciprocal(similarity)
    r1 = recall_at_k_group_aware(rrf_ranking, df, 1)
    r5 = recall_at_k_group_aware(rrf_ranking, df, 5)
    r10 = recall_at_k_group_aware(rrf_ranking, df, 10)
    print(f"Recall@1={r1:.4f}, Recall@5={r5:.4f}, Recall@10={r10:.4f}")
    results['rrf'] = [r1, r5, r10]
    
    # Trick 2: Query Expansion
    print("\n[TRICK 2: Query Expansion]")
    qe_ranking, _ = trick_2_query_expansion(description_emb, destination_emb, df)
    r1 = recall_at_k_group_aware(qe_ranking, df, 1)
    r5 = recall_at_k_group_aware(qe_ranking, df, 5)
    r10 = recall_at_k_group_aware(qe_ranking, df, 10)
    print(f"Recall@1={r1:.4f}, Recall@5={r5:.4f}, Recall@10={r10:.4f}")
    results['query_expansion'] = [r1, r5, r10]
    
    # Trick 3: Hard Negative Reweight
    print("\n[TRICK 3: Hard Negative Reweight]")
    hn_ranking, _ = trick_3_hard_negative_mining_reweight(similarity, df)
    r1 = recall_at_k_group_aware(hn_ranking, df, 1)
    r5 = recall_at_k_group_aware(hn_ranking, df, 5)
    r10 = recall_at_k_group_aware(hn_ranking, df, 10)
    print(f"Recall@1={r1:.4f}, Recall@5={r5:.4f}, Recall@10={r10:.4f}")
    results['hard_negative'] = [r1, r5, r10]
    
    # Trick 4: Ensemble
    print("\n[TRICK 4: Ensemble All]")
    ensemble_ranking = trick_4_ensemble_rankings(
        [ranking, rrf_ranking, qe_ranking, hn_ranking],
        weights=[1.0, 1.2, 1.1, 0.9]  # Tune these weights
    )
    r1 = recall_at_k_group_aware(ensemble_ranking, df, 1)
    r5 = recall_at_k_group_aware(ensemble_ranking, df, 5)
    r10 = recall_at_k_group_aware(ensemble_ranking, df, 10)
    print(f"Recall@1={r1:.4f}, Recall@5={r5:.4f}, Recall@10={r10:.4f}")
    results['ensemble'] = [r1, r5, r10]
    
    print("="*60)
    
    # Visualize comparison
    plot_tricks_comparison(results)
    
    return ensemble_ranking, results

def plot_tricks_comparison(results):
    """
    So sánh hiệu quả của các tricks
    """
    methods = list(results.keys())
    r1_scores = [results[m][0] for m in methods]
    r5_scores = [results[m][1] for m in methods]
    r10_scores = [results[m][2] for m in methods]
    
    x = np.arange(len(methods))
    width = 0.25
    
    plt.figure(figsize=(12, 6))
    plt.bar(x - width, r1_scores, width, label='Recall@1', alpha=0.8, color='#e74c3c')
    plt.bar(x, r5_scores, width, label='Recall@5', alpha=0.8, color='#3498db')
    plt.bar(x + width, r10_scores, width, label='Recall@10', alpha=0.8, color='#2ecc71')
    
    plt.xlabel('Method', fontsize=12, fontweight='bold')
    plt.ylabel('Recall', fontsize=12, fontweight='bold')
    plt.title('Comparison of Tricks to Boost Recall@K', fontsize=14, fontweight='bold', pad=20)
    plt.xticks(x, [m.replace('_', ' ').title() for m in methods], rotation=15, ha='right')
    plt.legend(fontsize=11)
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.3, axis='y', linestyle='--')
    plt.tight_layout()
    plt.show()

# Chạy tất cả tricks
# best_ranking, trick_results = apply_all_tricks(description_emb, destination_emb, df, similarity, ranking)

# Bonus: Analyze per-destination performance
def analyze_per_destination(df, similarity, ranking, top_k=10):
    """
    Phân tích performance cho từng destination
    """
    dest_to_indices = create_destination_mapping(df)
    
    results = []
    
    for dest, indices in dest_to_indices.items():
        if len(indices) <= 1:  # Skip destinations với chỉ 1 description
            continue
        
        correct = 0
        for i in indices:
            positive_indices = set(indices)
            positive_indices.discard(i)
            
            top_k_preds = ranking[i, :top_k].tolist()
            
            if any(pred in positive_indices for pred in top_k_preds):
                correct += 1
        
        recall = correct / len(indices)
        results.append({
            'destination': dest,
            'num_descriptions': len(indices),
            'recall@10': recall
        })
    
    results_df = pd.DataFrame(results).sort_values('recall@10')
    
    print("\n" + "="*60)
    print("PER-DESTINATION ANALYSIS")
    print("="*60)
    print(f"\nWorst 5 destinations:")
    print(results_df.head())
    print(f"\nBest 5 destinations:")
    print(results_df.tail())
    print("="*60)
    
    return results_df

# Chạy phân tích per-destination
dest_analysis = analyze_per_destination(df, similarity, ranking)

# %%



