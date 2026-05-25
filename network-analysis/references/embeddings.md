# Graph Embeddings and Graph Neural Networks

When the goal is to use network structure as features for downstream ML (classification, link prediction, recommendation, anomaly detection), you embed nodes (or edges, or subgraphs, or whole graphs) into vector spaces and apply standard ML. This file is the menu of embedding methods and the regime each works well in.

## The basic divide

Two families:

1. **Shallow / unsupervised embeddings**: learn one vector per node by optimizing a structural objective (random walks, matrix factorization). *DeepWalk, node2vec, LINE, HOPE, NetMF.*
2. **Deep / message-passing (GNNs)**: learn node representations by neural aggregation of neighbor features; can be supervised or unsupervised. *GCN, GraphSAGE, GAT, GIN.*

Choose shallow when:
- Node features are absent or weak
- The graph is fixed (no need to embed unseen nodes)
- You want simple, interpretable embeddings

Choose GNNs when:
- Nodes have rich features (text, images, attributes)
- You need inductive ability (embed new nodes without retraining)
- You're doing semi-supervised learning with few labels

## Shallow embedding methods

### DeepWalk (Perozzi, Al-Rfou & Skiena 2014)

1. Sample many random walks from each node
2. Treat each walk as a "sentence" and each node as a "word"
3. Train word2vec (skip-gram with hierarchical softmax) on these walks

Result: nodes appearing in similar contexts (similar neighborhoods) get similar embeddings.

### node2vec (Grover & Leskovec 2016)

Generalizes DeepWalk with biased random walks. Two parameters:
- **p (return)**: low p → walks return to recent nodes (BFS-like, captures local structure / equivalence)
- **q (in-out)**: low q → walks explore farther (DFS-like, captures community structure)

Tuning p and q lets node2vec interpolate between **structural equivalence** (similar local patterns → similar embeddings) and **homophily** (same community → similar embeddings). The default p=q=1 is plain DeepWalk.

```python
from node2vec import Node2Vec
n2v = Node2Vec(G, dimensions=128, walk_length=80, num_walks=10, p=1, q=1)
model = n2v.fit(window=10, min_count=1)
emb = model.wv['node_id']
```

### LINE (Tang et al. 2015)

Two objectives:
- **First-order proximity**: directly connected nodes have similar embeddings
- **Second-order proximity**: nodes with similar neighborhoods have similar embeddings (even if not directly connected)

Trained separately and concatenated. Scales to very large networks (millions of nodes); was Microsoft's production embedding for a while.

### Matrix factorization views

Qiu et al. (2018) showed DeepWalk, LINE, node2vec are implicitly factorizing a specific shifted-PMI matrix related to the network's random-walk matrix. **NetMF** explicitly factorizes this matrix and matches/exceeds the random-walk methods, often faster. Useful theoretical bridge: it explains *why* node2vec and SBM-based community detection often agree (Kojaku et al. 2024 — "node2vec encodes communities into separable clusters down to the detectability limit").

### Spectral embedding (Laplacian eigenmaps)

The leading k eigenvectors of the normalized graph Laplacian. Theoretically founded, fast for moderate graphs, but doesn't scale beyond ~100k nodes (eigendecomposition).

Connection: **node2vec ≈ Laplacian eigenmaps with sampling**, both relate to spectral methods (Qiu et al. 2018; Kojaku et al. 2024).

## Graph Neural Networks

GNNs follow a **message-passing** schema:

`h_v^(k+1) = UPDATE(h_v^(k), AGGREGATE({h_u^(k) : u ∈ N(v)}))`

After K layers, each node's representation contains information from its K-hop neighborhood. Variants differ in AGGREGATE and UPDATE.

### Graph Convolutional Network (GCN; Kipf & Welling 2017)

`H^(k+1) = σ(D̃^(-1/2) Ã D̃^(-1/2) H^(k) W^(k))`

where Ã = A + I (add self-loops), D̃ is degree matrix of Ã, σ is nonlinearity. Each node's new representation is a weighted average of its (and neighbors') previous representations.

Simple, fast, surprisingly effective. Limitations: **transductive** (can't embed new nodes), assumes the graph fits in memory.

### GraphSAGE (Hamilton, Ying & Leskovec 2017)

Generalizes GCN to be inductive:
- Sample a fixed-size neighborhood for each node (handles variable degree)
- Aggregate (mean, LSTM, max, or pool)
- Concatenate with own embedding and project

Scales to billions of nodes (Pinterest's PinSage extension). Inductive: can embed new nodes given their features and neighbors.

### Graph Attention Network (GAT; Veličković et al. 2018)

Weighted aggregation where weights are learned attention coefficients:

`α_uv = softmax_u(LeakyReLU(a^T [W h_u || W h_v]))`

Different neighbors contribute differently based on learned relevance. Multi-head attention for stability.

### Graph Isomorphism Network (GIN; Xu et al. 2019)

Theoretically derived to match the Weisfeiler-Lehman test for graph isomorphism, the most expressive 1-WL message-passing GNN. Useful when you need maximum expressiveness within message-passing.

### Beyond message passing

Message-passing GNNs have known expressiveness ceilings (cannot distinguish certain non-isomorphic graphs). Recent work:
- **Higher-order GNNs**: aggregate over k-tuples instead of edges
- **Graph Transformers**: full attention with positional encoding (Graphormer, GraphGPS)
- **Subgraph GNNs**: learn from subgraph samples

For most applications, message-passing GNNs are sufficient; for hard structural tasks (counting motifs, distinguishing molecules), more expressive variants matter.

## Choosing a GNN library

- **PyTorch Geometric (PyG)**: most popular, big model zoo, fast
- **Deep Graph Library (DGL)**: alternative, similar feature set, both PyTorch and MXNet backends
- **StellarGraph**: TensorFlow-based, more limited
- **CogDL**, **Spektral**, etc.: specialized

PyG is the safe default. Code skeleton:

```python
import torch
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv

class GCN(torch.nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super().__init__()
        self.conv1 = GCNConv(in_dim, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, out_dim)
    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = torch.nn.functional.dropout(x, training=self.training)
        return self.conv2(x, edge_index)

data = Data(x=node_features, edge_index=edge_idx, y=labels)
model = GCN(in_dim=..., hidden_dim=64, out_dim=num_classes)
# Train with standard PyTorch loop
```

## Common tasks and recipes

### Node classification

Standard supervised setup; predict node labels given partial labels (semi-supervised).

- Small-to-medium graphs with attributes: GCN or GAT
- Large graphs, inductive: GraphSAGE with sampling
- Sparse labels: SSL with pseudo-labeling or contrastive learning (GraphCL)

### Link prediction

Predict whether two nodes will be connected. Score = some function of embeddings: dot product, MLP, distance.

For training: positive edges = real edges; negative edges = sampled non-edges. Use **train/val/test splits on edges**, not nodes (PyG's `RandomLinkSplit`). Critically: **use the message-passing graph that excludes test edges** to prevent leakage.

Evaluation: AUROC, average precision, Hits@K (especially for ranking).

### Graph classification

Predict a label for a whole graph (molecules, social-network types). Need a **readout / pooling** to aggregate node embeddings into a graph embedding: mean, sum, attention pooling, or hierarchical pooling (DiffPool, SAGPool, TopKPool).

### Community detection via embeddings

Embed nodes, then cluster (k-means, GMM) in the embedding space. Kojaku et al. (2024) showed node2vec recovers SBM communities optimally; combining is competitive with SBMs while being cheaper.

### Anomaly detection

Train a GNN to predict node attributes from neighborhood; high reconstruction error = anomaly. Or use contrastive: encode the graph and find nodes far from their context. Strong baselines: DOMINANT, AnomalyDAE.

## Common embedding mistakes

- **Train/test leakage in link prediction**: using test-set edges during message-passing inflates AUROC. Use proper splits.
- **Comparing embeddings across runs**: embeddings are invariant to rotation/permutation; raw embedding values are not meaningful across runs. Compare downstream task performance, not embeddings.
- **Using node2vec with default p=q=1 and then complaining it doesn't separate communities** — tune p and q to your task.
- **Using GCN on disconnected graphs**: information can't flow between components; either restrict to LCC, add a global "supernode", or use a model that handles disconnection (GraphSAGE with sampling).
- **Forgetting feature normalization**: GNNs are sensitive to input scale; standardize or row-normalize features.
- **Over-smoothing**: stacking many GNN layers makes all node embeddings collapse together. Stay shallow (2–4 layers), or use residual connections, or use methods like APPNP / GCNII that resist over-smoothing.
- **Class imbalance in semi-supervised settings**: weighted loss or balanced sampling matters.
- **Hyperparameter cherry-picking**: GNN benchmark performance is notoriously hyperparameter-dependent; report a sweep, not a best run (Errica et al. 2020).

## When NOT to use GNNs

Many graph tasks have simpler baselines that often match or beat GNNs:

- **Node classification with strong features**: a logistic regression on node features + neighbor-aggregated features (the "Simple Graph Convolution" baseline; Wu et al. 2019) often matches GCN
- **Sparse graphs with little structure**: label propagation may suffice
- **Tasks with no structural signal**: feature-only MLP

Test these baselines before claiming GNN improvement. Errica et al. (2020) and Shchur et al. (2018) showed many published GNN results don't beat simpler baselines under fair evaluation.

## Canonical references

- Hamilton, W. L. (2020). *Graph Representation Learning*. Morgan & Claypool.
- Perozzi, B., Al-Rfou, R., & Skiena, S. (2014). "DeepWalk: Online learning of social representations." *KDD*.
- Grover, A. & Leskovec, J. (2016). "node2vec: Scalable feature learning for networks." *KDD*.
- Kipf, T. N. & Welling, M. (2017). "Semi-supervised classification with graph convolutional networks." *ICLR*.
- Hamilton, W. L., Ying, R., & Leskovec, J. (2017). "Inductive representation learning on large graphs." *NeurIPS*.
- Veličković, P., et al. (2018). "Graph attention networks." *ICLR*.
- Xu, K., Hu, W., Leskovec, J., & Jegelka, S. (2019). "How powerful are graph neural networks?" *ICLR*.
- Qiu, J. et al. (2018). "Network embedding as matrix factorization." *WSDM*.
- Errica, F., Podda, M., Bacciu, D., & Micheli, A. (2020). "A fair comparison of graph neural networks for graph classification." *ICLR*.
- Kojaku, S., Yoon, J., Constantino, I., & Ahn, Y.-Y. (2024). "Network community detection via neural embeddings." *Nature Communications* 15: 10468.
