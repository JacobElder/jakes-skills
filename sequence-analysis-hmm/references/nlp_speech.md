# HMMs in NLP and Speech

The application area where HMMs were *the* method for decades and are now mostly historical. This reference is about when they still matter, how they compare to modern alternatives, and the conceptual lineage that makes them worth understanding even when you don't use them.

## When this is the relevant reference

- Part-of-speech tagging (especially as a baseline or in low-resource languages)
- Named entity recognition with HMMs or CRFs
- Speech recognition history and acoustic modeling concepts
- Handwriting or gesture recognition
- Comparison of HMMs with CRFs, neural sequence models, transformers
- Educational / teaching contexts where HMMs are still on the syllabus
- Cases where calibrated generative probabilities are needed

## State of the art: neural models won, but HMMs still teach you things

For nearly every supervised sequence labeling task today, the SOTA approach is a pretrained transformer (BERT, RoBERTa, or larger) fine-tuned on labeled data. For ASR, end-to-end neural systems (Whisper, Conformer, wav2vec2) have replaced HMM-GMM and HMM-DNN hybrids. Be honest about this.

That said, HMMs and their discriminative cousin CRFs remain useful when:

1. **You're a baseline.** Reviewers expect baselines; HMMs are the cheap, principled one.
2. **You have very little labeled data.** Neural models need lots; HMMs can fit on dozens to hundreds of examples and still do something sensible. POS tagging in extremely low-resource languages often still uses HMMs or hybrids.
3. **You need calibrated probabilities.** Generative models give you P(X, Z) and thus well-defined likelihoods; neural classifiers' softmax outputs are notoriously poorly calibrated without explicit calibration.
4. **You need interpretability.** Stakeholders can read a transition matrix; they can't read a transformer.
5. **You're teaching.** The forward-backward algorithm is one of the most important things in machine learning. Understanding HMMs deeply makes understanding RNNs, transformers, CRFs, and CTC much easier.
6. **You're decoding.** Beam search with an HMM language model on top of a neural acoustic model is *still* how a lot of production ASR works under the hood (CTC + LM, RNN-T + LM, etc.).

## POS tagging — the canonical NLP example

A first-order HMM for POS tagging:
- States: POS tags (NN, VB, JJ, ...)
- Observations: words
- Transition matrix: P(tag_{t} | tag_{t-1})
- Emission distributions: P(word | tag)

Estimated from a tagged corpus (Penn Treebank, etc.) by counting:
- A[i][j] = (# times tag i followed by tag j) / (# times tag i appears, not at end)
- B[i][w] = (# times tag i emitted word w) / (# times tag i appears)
- π[i] = (# sentences starting with tag i) / (# sentences)

Inference: Viterbi over the sentence gives the most likely tag sequence. With Laplace smoothing or a more sophisticated smoothing scheme, this gets you to ~95-96% accuracy on Penn Treebank, vs. ~97-98% for a modern neural tagger. Not bad for a model you can fit in 10 lines of code.

The bigger issue is **out-of-vocabulary words**. The pure HMM has B[i][unknown] = 0, which crashes Viterbi (or rather, makes the result depend entirely on tag transitions). Standard fixes: smoothing, treating rare words as a generic UNK token, or using suffix features (an early form of feature engineering that motivated the move to MEMMs / CRFs / neural taggers).

```python
# Toy NLTK HMM tagger
from nltk.corpus import treebank
from nltk.tag.hmm import HiddenMarkovModelTrainer

train_data = treebank.tagged_sents()[:3000]
test_data = treebank.tagged_sents()[3000:]

trainer = HiddenMarkovModelTrainer()
tagger = trainer.train_supervised(train_data)
print(f"Accuracy: {tagger.accuracy(test_data):.4f}")
```

For anything serious, use spaCy / stanza / a transformer fine-tune, not NLTK's HMM. The HMM is a teaching artifact.

## Why CRFs ate HMMs for sequence labeling

HMMs are generative: they model P(X, Z) and you derive P(Z | X) via Bayes. This wastes capacity modeling the observations (which you're given). They also enforce conditional independence of observations given states, which is a strong assumption — you can't easily incorporate overlapping features like "the previous word is capitalized AND ends in -tion AND the current word is in our gazetteer."

Conditional Random Fields (CRFs), specifically linear-chain CRFs, model P(Z | X) directly using a log-linear model over arbitrary features of (X, Z_t, Z_{t-1}). They keep the Markov structure on the labels but allow rich, overlapping features on the observations. The training objective is conditional likelihood, optimized by L-BFGS or similar.

The practical difference: CRFs typically beat HMMs by 2-5 points on POS tagging and named entity recognition when you have decent training data, because they can use features HMMs can't. The decoding algorithm is the same (Viterbi). The learning algorithm is different (gradient-based, not EM).

`sklearn-crfsuite` is the standard Python implementation. Now itself displaced by neural taggers for high-resource tasks, but still a reasonable baseline.

A useful framing: HMM → MEMM (maximum-entropy Markov model, has the "label bias problem") → CRF → BiLSTM-CRF → Transformer + CRF head → fine-tuned transformer with token classification head. Each step relaxes an assumption or adds capacity.

## Speech recognition lineage (the short version)

The dominance of HMMs in speech is a 30-year story; here's the compressed version:

**1970s-1980s.** Discrete HMMs on quantized speech features. HMMs become the dominant ASR approach, displacing dynamic time warping.

**1990s-2000s.** HMM-GMM systems. Continuous HMMs with Gaussian mixture emissions modeling MFCCs. Standard architecture: one HMM per phone (usually 3 states per phone), then composed into word HMMs via pronunciation dictionaries, then sentences via language model. Kaldi is the modern descendant; HTK was the academic standard.

**2010s.** HMM-DNN hybrids. Replace the GMM emissions with a deep neural network's per-frame phone-posterior outputs (divided by phone priors). Big gains. Still uses HMM topology for temporal modeling.

**Late 2010s onward.** End-to-end neural systems. CTC (Connectionist Temporal Classification) lets you train an RNN/transformer to output character or subword sequences directly without explicit HMM alignment. Attention-based seq2seq (LAS), RNN-T, and transformer-based systems (Whisper, etc.) dominate today.

Interesting observation: CTC's forward-backward training algorithm is mathematically isomorphic to HMM forward-backward. The HMM lineage didn't die; it was absorbed.

If a user asks "should I use an HMM for speech recognition," the answer is almost always no — use Whisper or an existing toolkit (NeMo, ESPnet, SpeechBrain). The exception is research/teaching, or extremely low-resource languages.

## NLP-specific pitfalls

1. **Smoothing matters more than the model.** The fanciest model on un-smoothed counts loses to a vanilla model with good smoothing (Kneser-Ney, Good-Turing, additive). HMM POS taggers without smoothing crash on unseen word-tag pairs.

2. **Trigram vs. bigram tags.** Second-order HMMs (tag depends on previous two tags) outperform first-order, but with K² → K³ transition parameters. Worth it for POS tagging with sufficient data; less so for NER where label-transition counts are sparser.

3. **Word features vs. word identity.** Pure HMM emissions are P(word | tag). Practical taggers add features (suffix, capitalization, presence in a name list). Strictly, this breaks the HMM and you end up with a CRF-like model.

4. **Sentence vs. document scope.** Standard HMM POS tagging treats each sentence independently. Cross-sentence dependencies (e.g., topic-dependent tag preferences) are not captured. For NER, document-level coreference matters; neural models with longer context handle this much better.

5. **Decoding constraints.** In some tagging schemes (BIO/BIOES for NER), certain transitions are illegal (I-PER can't follow B-LOC). A CRF can encode this with infinite transition weights; an HMM needs to either learn it from data or constrain it manually.

## Code: a minimal CRF baseline (for "I want a sequence labeler that's better than an HMM but not a transformer")

```python
import sklearn_crfsuite

# X_train: list of sentences; each sentence is a list of feature dicts per token
# y_train: list of sentences; each sentence is a list of label strings per token

crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1, c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)
crf.fit(X_train, y_train)
y_pred = crf.predict(X_test)
```

Reasonable feature engineering is the hard part; the model is the easy part.

## Recommended reading

- Jurafsky & Martin, *Speech and Language Processing*, Chapter 8 (HMM tagging) and Chapter 17 (sequence labeling with CRFs). Free online drafts.
- Rabiner (1989), again — the speech recognition motivation is half the paper.
- Lafferty, McCallum, Pereira (2001), "Conditional Random Fields: Probabilistic models for segmenting and labeling sequence data." The CRF paper.
- Hannun et al. (2014), "Deep Speech": end-to-end speech recognition with CTC. Marks the transition era.
