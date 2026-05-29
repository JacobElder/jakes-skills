# Diagnosing Data Structure: Nested, Crossed, and Everything Between

Before any modeling, correctly identify how your grouping factors relate to each other. Misdiagnosing the structure leads to wrong formulas, wrong inference, and sometimes silent errors that look fine in output but are statistically wrong. This reference is the diagnostic step that should happen before opening `references/random_effects_specification.md`.

## The four structures you'll encounter

### 1. Strictly nested

Each lower-level unit belongs to **exactly one** higher-level unit. Students belong to one classroom; classrooms belong to one school. Patients belong to one clinic; clinics belong to one hospital.

Visual signature:

```
School A          School B          School C
├── Class 1       ├── Class 3       ├── Class 5
│   ├── Stu 1     │   ├── Stu 11    │   ├── Stu 21
│   └── Stu 2     │   └── Stu 12    │   └── Stu 22
└── Class 2       └── Class 4       └── Class 6
    └── Stu 3         └── Stu 13        └── Stu 23
```

Stu 1 is *only* in Class 1, which is *only* in School A.

### 2. Crossed

Two or more grouping factors where **every (or most) combination is observed**. The classic case: subjects × items in a psycholinguistic experiment — every subject sees every item.

Visual signature (a matrix, not a tree):

```
         Item 1  Item 2  Item 3  Item 4
Subj A     ✓       ✓       ✓       ✓
Subj B     ✓       ✓       ✓       ✓
Subj C     ✓       ✓       ✓       ✓
```

There's no hierarchy — subjects don't "contain" items and items don't "contain" subjects. They're orthogonal sources of variation.

### 3. Cross-classified

Two grouping factors where lower-level units belong to **multiple higher-level units that don't nest into each other**. Students belong to schools *and* to neighborhoods, but schools and neighborhoods aren't hierarchical — kids from one neighborhood attend several schools, and one school draws from several neighborhoods.

Visual signature:

```
                School 1    School 2    School 3
Nbhd Alpha      Stu 1       Stu 4
Nbhd Bravo      Stu 2       Stu 5,6     Stu 8
Nbhd Charlie                Stu 7       Stu 9,10
```

Each student is in exactly one school and exactly one neighborhood, but the (school, neighborhood) combinations are sparse and non-hierarchical.

### 4. Partially crossed

Mostly crossed but with missing combinations. Common in psycholinguistics with latin-square designs (each subject sees each *item*, but each subject sees only one *version* of each item), or in education research where teachers move between schools over time but not all teachers teach in all schools.

Visual signature: a sparse matrix.

```
         Item 1  Item 2  Item 3  Item 4
Subj A     ✓               ✓
Subj B             ✓               ✓
Subj C     ✓       ✓
```

## How to diagnose your structure

Mechanical procedure with code you can run on the data:

### Step A: List the grouping factors

What are the variables that identify clusters? `subject_id`, `item_id`, `school_id`, `classroom_id`, etc.

### Step B: For each pair of grouping factors, count co-occurrences

```r
# R
library(dplyr)

# Does each lower-level unit map to exactly one higher-level unit?
d %>% 
  group_by(student_id) %>% 
  summarize(n_classrooms = n_distinct(classroom_id)) %>% 
  count(n_classrooms)
# If all n_classrooms == 1, students are nested in classrooms.

d %>% 
  group_by(classroom_id) %>% 
  summarize(n_schools = n_distinct(school_id)) %>% 
  count(n_schools)
# If all n_schools == 1, classrooms are nested in schools.
```

```python
# Python
d.groupby("student_id")["classroom_id"].nunique().value_counts()
d.groupby("classroom_id")["school_id"].nunique().value_counts()
```

If every grouping at the lower level maps to exactly one at the upper level, it's **nested**.

### Step C: For crossed candidates, check the cross-tabulation

```r
# How many subjects see each item? How many items per subject?
with(d, table(subject_id, item_id)) %>% 
  { 
    cat("Cells with 0 observations:", sum(. == 0), "of", length(.), "\n")
    cat("Cells with >=1 observation:", sum(. >= 1), "\n")
    cat("Range of cell counts:", range(.), "\n")
  }
```

- If most cells > 0 and roughly balanced: **fully crossed** (or close enough)
- If most cells > 0 but with systematic gaps (e.g., latin square): **partially crossed**
- If cells form a block-diagonal pattern with each subject only in one block: probably **nested**

### Step D: For cross-classified candidates, check that the two upper-level factors aren't nested in each other

```r
# Are neighborhoods nested in schools (or vice versa)?
d %>% group_by(neighborhood_id) %>% summarize(n_schools = n_distinct(school_id)) %>% count(n_schools)
d %>% group_by(school_id) %>% summarize(n_neighborhoods = n_distinct(neighborhood_id)) %>% count(n_neighborhoods)
```

If neighborhoods span multiple schools AND schools span multiple neighborhoods, it's **cross-classified**.

## The ID gotcha that silently breaks nested models

The single most common silent failure: **non-unique IDs across higher-level units.**

Suppose your data has `school_id` and `student_id`, and student IDs are 1–30 within each school (so Student 1 in School A is a different person from Student 1 in School B).

```r
# WRONG — treats Student 1 in School A and Student 1 in School B as the same person
lmer(y ~ x + (1 | school) + (1 | student_id), data = d)

# RIGHT — uses nesting syntax to make student unique within school
lmer(y ~ x + (1 | school) + (1 | school:student_id), data = d)

# ALSO RIGHT — create globally unique IDs first
d$student_uid <- with(d, paste(school, student_id, sep = "_"))
lmer(y ~ x + (1 | school) + (1 | student_uid), data = d)

# ALSO RIGHT — explicit nesting shorthand
lmer(y ~ x + (1 | school/student_id), data = d)
# This expands to (1 | school) + (1 | school:student_id)
```

**Always check ID uniqueness before fitting nested models.** Quick check:

```r
n_distinct(d$student_id) == nrow(unique(d[, c("school_id", "student_id")]))
# TRUE → IDs are globally unique; either syntax works
# FALSE → IDs reused across schools; must use nesting syntax or recode
```

## Formula syntax cheat sheet

For lme4, brms, glmmTMB, bambi, pymer4 (same syntax across all of these):

| Structure | Formula |
|---|---|
| Two-level nested (students in schools), unique student IDs | `(1 \| school) + (1 \| student)` |
| Two-level nested, non-unique student IDs within schools | `(1 \| school/student)` or `(1 \| school) + (1 \| school:student)` |
| Three-level nested (students in classes in schools), all unique | `(1 \| school) + (1 \| class) + (1 \| student)` |
| Three-level nested, IDs unique only within parent | `(1 \| school/class/student)` |
| Crossed: subjects × items, random intercepts | `(1 \| subject) + (1 \| item)` |
| Crossed with random slopes on within-cluster predictor x | `(1 + x \| subject) + (1 + x \| item)` |
| Cross-classified: students in schools and neighborhoods | `(1 \| school) + (1 \| neighborhood)` |
| Cross-classified + students: students in schools × neighborhoods | `(1 \| school) + (1 \| neighborhood) + (1 \| student)` |
| Repeated measures: trials within subjects | `(1 \| subject)` (with random slopes for within-subject predictors) |
| Longitudinal growth: time within subjects | `(1 + time \| subject)` |

## Diagnostic questions to ask the user when structure is unclear

If the user describes the design ambiguously, ask explicitly:

- "Does each [lower unit] belong to exactly one [upper unit], or can they appear in multiple?"
- "Are your subject/student/cluster IDs globally unique, or do they restart within each higher-level group?"
- "Does every subject see every item, or only a subset (e.g., a latin square)?"
- "Are [factor A] and [factor B] hierarchical (one contains the other) or do they cross each other?"

A 30-second clarification here saves a fundamentally wrong model later.

## Worked example: identifying the structure of a real dataset

Suppose the user uploads data with columns `id`, `score`, `class`, `school`, `district`, `treatment`, `pretest`. What do you do?

1. **Check what each row represents.** `nrow(d)` vs `n_distinct(d$id)` — if equal, one row per student. If `nrow` > `n_distinct(id)`, multiple observations per student (longitudinal? repeated measures?).
2. **Check nesting between class, school, district.** Run the diagnostic code from Step B.
3. **Check where treatment varies.** `d %>% group_by(school) %>% summarize(n_tx = n_distinct(treatment))` — if `n_tx == 1` for all schools, treatment is school-level (between-school). If `n_tx > 1`, it varies within schools.
4. **Check ID uniqueness** before fitting.

Once those are established, the model practically writes itself:

> Students nested in classes nested in schools nested in districts. Treatment is at the school level. Pretest varies within classes (it's a student-level baseline). 

```r
lmer(score ~ treatment + pretest + 
     (1 | district/school/class), 
     data = d)
# Treatment is between-school, so no random slope for treatment is possible.
# Pretest varies within classes; if you want to model variability in its 
# effect across classes, add (1 + pretest | class) — though you may already
# have it inside the nesting shorthand.
```

## Bottom line

Spending 5 minutes diagnosing the structure with the user before writing any formula prevents the most common class of MLM errors. Use the cross-tabulation diagnostics above; they're cheap and they catch what eyeballing the data misses.
