# HMMs in Bioinformatics

The application area where HMMs are most central and least displaced by neural methods. The default tools are different from the rest of this skill — `HMMER`, not `hmmlearn`.

## When this is the relevant reference

- Anything involving Pfam, InterPro, or protein families
- "I have a protein/DNA sequence and I want to identify domains / classify it / find homologs"
- Profile HMM construction, hmmbuild, hmmsearch, hmmscan, jackhmmer
- Gene-finding (GENSCAN, AUGUSTUS, GeneMark, Glimmer)
- Multiple sequence alignment as input to HMM building
- CpG islands, transmembrane prediction (TMHMM), signal peptides (SignalP, older HMM versions)
- Pair HMMs for pairwise alignment

## Profile HMMs (the central object)

A profile HMM models a *family* of related sequences (proteins or nucleotides) as a position-specific probabilistic model. It has a left-to-right architecture with three types of states at each column of the alignment:

- **Match states (M_k)** — emit residues at conserved positions, with position-specific emission probabilities (e.g., position 27 of a kinase domain is often a lysine).
- **Insert states (I_k)** — emit residues that aren't part of the consensus (insertions relative to the family).
- **Delete states (D_k)** — silent (no emission); allow skipping match positions (deletions).

Transitions go forward only (M_k → M_{k+1}, M_k → I_k, M_k → D_{k+1}, etc.). This is the **Plan 7** architecture that HMMER uses; details in the HMMER user guide.

Built from a multiple sequence alignment using `hmmbuild`. Searched against sequences (or sequence databases) using `hmmsearch` / `hmmscan`. The output is a list of hits with E-values; statistically significant hits are considered family members.

Why this dominates: profile HMMs encode position-specific conservation explicitly, handle insertions/deletions correctly, and the scoring (log-odds against a null model) is statistically grounded. Pfam — one of the most-used databases in biology — is built entirely on profile HMMs.

## HMMER — the canonical toolkit

`HMMER` (current version 3.4, released August 2023; check `hmmer.org` for newer) is the production tool. Command-line, BSD-licensed, written in C, ported to all major OSes. Maintained by Sean Eddy's lab.

Core commands:

| Command | Purpose |
|---|---|
| `hmmbuild` | Build a profile HMM from a multiple sequence alignment |
| `hmmalign` | Align sequences to a profile HMM |
| `hmmsearch` | Search profile(s) against a sequence database |
| `hmmscan` | Search sequence(s) against a profile database (e.g., Pfam-A) |
| `phmmer` | Search a single sequence against a database (no MSA needed) |
| `jackhmmer` | Iterative search (like PSI-BLAST but with HMMs) |
| `hmmpress` | Prepare an HMM database for fast searching |
| `hmmemit` | Sample sequences from an HMM |
| `hmmstat` | Statistics on profile HMMs |

Typical workflow for "what is this protein?":

```bash
# Download Pfam-A.hmm from Pfam/InterPro and press it once
hmmpress Pfam-A.hmm

# Scan your sequence against all Pfam families
hmmscan --tblout hits.tbl Pfam-A.hmm my_protein.fasta
```

Typical workflow for "find homologs of this family":

```bash
# Build a profile from a curated MSA
hmmbuild my_family.hmm my_family.aln

# Search a target proteome
hmmsearch --tblout hits.tbl my_family.hmm uniprot.fasta
```

E-value interpretation: report `--tblout` (per-target) or `--domtblout` (per-domain). E-values < 1e-5 are usually solid; < 1e-3 worth a look; > 0.01 marginal. Use full-sequence E-values for "is this a member of the family"; domain E-values for "does this region contain the domain."

## Python access: `pyhmmer`

`pyhmmer` is a maintained Python binding to HMMER (Cython wrapper around HMMER's library code). Use when you want to script HMMER searches programmatically rather than shelling out, or to integrate profile HMMs into a Python pipeline.

```python
import pyhmmer

# Load a pressed Pfam database
with pyhmmer.plan7.HMMFile("Pfam-A.hmm") as hmm_file:
    hmms = list(hmm_file)

# Read query sequences
with pyhmmer.easel.SequenceFile("my_proteins.fasta", digital=True) as seq_file:
    sequences = list(seq_file)

# Search each HMM against the sequences
for hits in pyhmmer.hmmer.hmmscan(sequences, hmms):
    for hit in hits:
        if hit.included:
            print(hit.name.decode(), hit.evalue, hit.score)
```

Faster than shelling out for many short queries.

## Gene finding (a specific HMM architecture)

Gene-finders use HMMs with hand-crafted state architectures encoding the biology: exons, introns, intergenic regions, splice donor and acceptor sites, start and stop codons, UTRs. State transitions enforce the structural constraints (e.g., an exon must end before an intron starts; a stop codon must be in-frame).

- **GENSCAN** (Burge & Karlin, 1997) — classic eukaryotic gene-finder.
- **AUGUSTUS** — modern, still widely used; supports hints from RNA-seq or homology.
- **Glimmer** — prokaryotic gene-finder (interpolated Markov models, technically variable-order Markov rather than HMM).
- **GeneMark** — both prokaryotic and eukaryotic variants.

These are not jobs for `hmmlearn`. Use the dedicated tool. For new organisms without a trained model, parameter estimation from a curated training set is the bottleneck — often the model is trained on a related species.

## CpG islands — the classic textbook example

Two HMMs (or one HMM with two state-sets): "CpG island" state set emits Cs and Gs with elevated frequency and CpG dinucleotides at expected rate; "non-island" state set emits with depleted CpG dinucleotides (reflecting methylation-induced deamination). Posterior decoding gives a probability per position of being inside an island. Worked in Durbin et al. Chapter 3 — read that chapter if you've never built one.

## Pair HMMs for pairwise alignment

Standard Needleman-Wunsch / Smith-Waterman can be reformulated as decoding a "pair HMM" with three states (Match, Insert-in-X, Insert-in-Y) emitting pairs of residues. Gives a probabilistic interpretation of alignment scores and posterior probabilities of alignment columns. Used in some statistical alignment tools; conceptually clarifying even if you stick with classical aligners in practice.

## Things that bite in bioinformatics specifically

- **Sequence weighting.** Members of an MSA aren't independent — many are near-duplicates from the same clade. `hmmbuild` does sequence weighting (default: Henikoff position-based) to downweight redundancy. Disabling this gives badly biased profiles.

- **Effective sequence number.** Profile HMMs use Dirichlet mixture priors over emission probabilities, with the prior strength controlled by an "effective number" of sequences. Defaults work for most cases; tweak only with reason.

- **The null model.** HMMER scores against a null background model of residue frequencies. Custom null models matter when your sequence composition is unusual (e.g., very biased GC content, signal peptides).

- **Genomic-scale searches need pressed databases.** `hmmpress` is required before `hmmscan` against Pfam-A. People forget this and complain about speed.

- **Profile-profile comparison.** For very remote homology (sequence identity below the "twilight zone" of ~25%), you sometimes need profile-profile comparison rather than sequence-profile. HHsuite (`hhsearch`, `hhblits`) is the standard tool; conceptually related to HMMER but a different algorithm.

- **AlphaFold did not kill profile HMMs.** Sequence-level family classification (Pfam) still uses them. Structure prediction is a different task.

## Recommended reading

- Eddy (1998), "Profile hidden Markov models," *Bioinformatics* 14(9). Eddy is the author of HMMER; this is the canonical paper.
- Krogh, Brown, Mian, Sjölander, Haussler (1994), "Hidden Markov models in computational biology: Applications to protein modeling," *J. Mol. Biol.* 235(5). The paper that established the field.
- Durbin, Eddy, Krogh, Mitchison (1998), *Biological Sequence Analysis*. The textbook. Chapters 3, 5, and 6 are the core.
- HMMER User's Guide (`hmmer.org/documentation.html`). Has the Plan 7 details and worked examples.
