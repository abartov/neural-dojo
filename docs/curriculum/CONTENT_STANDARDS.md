# Neural Dojo Content Standards

**The definitive guide to creating engaging, educational content.**

**Last Updated**: 2025-11-27
**Version**: 1.0.0

---

## Core Philosophy

> "Stories make concepts memorable. Learners remember 'the moth in Grace Hopper's computer' forever, but forget dry technical explanations."

We follow the **JamesBlonde Pattern**: content should be **entertaining, engaging, and educational** - in that order. If it's not fun to read, people won't learn from it.

---

## The Golden Rules

### 1. Theory First, Code Second

**Never show code without explaining WHY first.**

```
❌ BAD:
### Step Decay
The simplest schedule.
```python
scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
```

✅ GOOD:
### Step Decay: The Classic Approach

Imagine you're learning to ride a bike. At first, you need training wheels (high learning rate - big corrections). As you get better, you remove them and make smaller adjustments. Step decay does exactly this - it reduces the learning rate at fixed intervals, letting the model make finer adjustments as it gets closer to the optimal solution.

The original ResNet paper used this approach: divide by 10 at epochs 30, 60, and 90. It became so standard that it's still the default in many codebases today, even though smoother schedules often work better.

```python
scheduler = StepLR(optimizer, step_size=30, gamma=0.1)
```

Notice how we multiply by 0.1 (divide by 10) every 30 epochs. The `gamma` parameter controls how aggressive the decay is.
```

### 2. Prose-First, Code-Second

Every code block MUST be preceded by:
- **2-3 sentences minimum** explaining the concept
- **An analogy or real-world example** when possible
- **The WHY** - why does this matter? why this approach?

Every code block SHOULD be followed by:
- **"Notice how..."** or **"The key insight here is..."**
- **What to watch out for** (common mistakes)

### 3. Stories Throughout, Not Just at the End

**Don't cluster all "Did You Know?" sections at the end.** Sprinkle them:
- At the **BEGINNING** of major sections (most impactful)
- **After introducing a new concept** (reinforces learning)
- **Before diving into code** (builds context)

### 4. Name the Humans

Always include researcher/founder names:
- ❌ "Batch normalization was invented in 2015"
- ✅ "In 2015, Sergey Ioffe and Christian Szegedy at Google published..."

### 5. Include Real Numbers

Statistics make content credible and memorable:
- Citation counts ("cited 60,000 times")
- Revenue/impact ("Netflix generates $1B+ from recommendations")
- Performance gains ("100x faster than brute force")
- Costs ("GPT-3 cost $4.6M to train")
- Adoption rates ("75% of NeurIPS 2019 papers used PyTorch")

---

## Required Elements

### "Did You Know?" Sections

**Minimum**: 3-5 per module (aim for more in longer modules)
**Length**: 100-300 words each with a compelling narrative
**Placement**: Introduction, after each major section, before summary

**Types of stories to include:**

1. **Origin/Discovery Stories**
   - Who invented it and when
   - What problem were they solving
   - Accidents and surprises
   - Rejected papers that became influential

2. **Industry Adoption**
   - Which companies use this in production
   - Revenue/impact numbers
   - How it transformed their products

3. **Surprising Statistics**
   - Numbers that shock or enlighten
   - Comparisons that provide perspective

4. **Failures That Led to Success**
   - Production disasters that drove innovation
   - Bugs that cost millions
   - "Happy accidents" that became features

**Example formats:**
```markdown
> **Did You Know?** In 2019, a researcher at OpenAI was debugging a language model when they accidentally left the sampling temperature too high. Instead of fixing it, they noticed the outputs were more creative and interesting. This "bug" led to the development of nucleus sampling, now used in virtually every text generation system.

> **Did You Know?** The BatchNorm paper has been cited over 60,000 times, making it one of the most influential papers in machine learning history. For context, Einstein's special relativity paper has about 3,000 citations. A technique for training neural networks has influenced more research papers than Einstein's most famous work!
```

---

## Writing Style

### DO ✅

- Write in **second person** ("you will learn...", "notice how...")
- Use **analogies and metaphors** before technical explanations
- Include **real-world examples** from named companies
- Explain **WHY**, not just WHAT and HOW
- **Break down** complex concepts step-by-step
- Use **diagrams** (mermaid/ASCII) where helpful
- **Anticipate questions** ("You might wonder why...")
- Include **common pitfalls** and how to avoid them
- Add **personality** - be conversational, not academic
- Use **humor** when appropriate (but don't force it)

### DON'T ❌

- **Handwave** complex topics ("it just works", "for reasons beyond this tutorial")
- **Skip fundamentals** assuming the reader knows them
- Use **jargon without explanation**
- Write **walls of text** without structure
- **Assume prior knowledge** beyond stated prerequisites
- **Copy-paste** from official documentation
- Leave **concepts unexplained**
- Write **dry, academic prose**
- Use **passive voice** when active is clearer
- Show **code without context**

---

## Section Structure Template

```markdown
## [Topic Name]: [Engaging Subtitle]

[Opening hook - why should the reader care? Make it interesting!]

### The Story Behind [Topic]

[Origin story with researcher names, dates, context]
[What problem were they solving?]
[Any surprises, accidents, or rejected papers?]

> **Did You Know?** [Compelling narrative with specific details]

### Understanding [Core Concept]

[Plain English explanation - no code yet!]
[Analogy to everyday experience]
[Why this matters in practice]

### [Concept] in Practice

[Explain what the code will do and WHY before showing it]

```python
# Code with inline comments for non-obvious parts
```

[After code: "Notice how..." or "The key insight here is..."]
[Common mistakes to avoid]

### When to Use [Topic]

[Decision framework or comparison table]
[Real-world scenarios]

> **Did You Know?** [Another story or statistic]

### Common Pitfalls

1. **[Pitfall 1]**: [What goes wrong and how to fix it]
2. **[Pitfall 2]**: [What goes wrong and how to fix it]
```

---

## Code Block Rules

### Before Every Code Block

**Minimum 2-3 sentences** answering:
1. What does this code do?
2. Why would you use this approach?
3. What problem does it solve?

### Inside Code Blocks

- **Comments** for non-obvious parts only (don't over-comment obvious code)
- **Type hints** for function signatures
- **Realistic variable names** (not `x`, `y`, `foo`, `bar`)

### After Code Blocks

- Explain the **key insight** or **pattern**
- Point out **what to notice**
- Mention **common variations** or alternatives
- Warn about **common mistakes**

### Code Block Length

- **Ideal**: 10-25 lines
- **Maximum**: 40 lines before breaking up with explanation
- **If longer**: Split into multiple blocks with prose between them

---

## Analogies Library

Use relatable metaphors. Some examples:

| Concept | Analogy |
|---------|---------|
| Gradient descent | Walking downhill in fog, feeling for the steepest slope |
| Learning rate | Step size when walking - too big and you overshoot, too small and you never arrive |
| Batch normalization | Standardizing ingredients in a recipe so it works consistently |
| Dropout | Training a team where random members are absent, forcing everyone to be useful |
| Embeddings | GPS coordinates for words - similar meanings are nearby |
| Attention | A spotlight that highlights relevant parts of the input |
| Overfitting | Memorizing answers vs understanding concepts |
| Regularization | Adding friction to prevent the model from being too confident |
| Transfer learning | Starting a new job with experience from a previous similar role |
| Vanishing gradients | Telephone game - the message gets garbled over many steps |

---

## Quality Checklist

Before marking a module complete, verify:

### Content Quality
- [ ] **Opening hook** - Does it grab attention?
- [ ] **Stories throughout** - Not just at the end?
- [ ] **3-5+ "Did You Know?"** sections with narratives?
- [ ] **Researcher names** included in origin stories?
- [ ] **Real statistics** and numbers?
- [ ] **Analogies** before technical explanations?
- [ ] **Prose before every code block** (2-3 sentences minimum)?
- [ ] **"Notice how..."** after code blocks?
- [ ] **Common pitfalls** section?
- [ ] **No walls of code** without explanation?

### Entertainment Value
- [ ] Would YOU want to read this?
- [ ] Is there personality in the writing?
- [ ] Are there surprising facts or stories?
- [ ] Does it explain WHY things matter?
- [ ] Is jargon explained on first use?

### Technical Accuracy
- [ ] All code tested and working?
- [ ] No handwaving ("it just works")?
- [ ] Prerequisites clearly stated?
- [ ] Edge cases mentioned?

---

## Examples of Excellence

### Good Module Sections (from our curriculum)

**Module 11 (Vector Databases)** - Origin story at the beginning:
> "The vector database gold rush began quietly in 2012 when Google researchers published a paper that would change information retrieval forever..."

**Module 27 (PyTorch)** - Engaging opening:
> "In the mid-2010s, deep learning was dominated by TensorFlow. Google's framework was everywhere... But researchers were frustrated. TensorFlow's 'define-then-run' approach meant you had to build your entire computation graph before seeing any results."

**Module 28 (Training)** - Analogy before code:
> "Think of a team where one person does all the work. If that person gets sick, the team fails. But if everyone shares responsibility, losing any one person is survivable. Dropout forces every neuron to be useful on its own."

---

## Anti-Patterns to Avoid

### The "Textbook Dump"
```
❌ BAD:
## Batch Normalization

Batch normalization normalizes the activations.

```python
nn.BatchNorm1d(256)
```

This normalizes the batch.
```

### The "Code Wall"
```
❌ BAD:
Here's the complete implementation:

```python
[80 lines of code with no breaks or explanation]
```
```

### The "Wikipedia Summary"
```
❌ BAD:
Dropout was proposed in 2014. It randomly sets neurons to zero during training.
This helps prevent overfitting.
```

### The "Jargon Fest"
```
❌ BAD:
The KL divergence between the posterior and prior is minimized via the ELBO
using reparameterization trick for backpropagation through stochastic nodes.
```

---

## Final Reminder

**Ask yourself before publishing:**

1. If I knew nothing about this topic, would this make sense?
2. Would I enjoy reading this?
3. Will I remember this tomorrow?
4. Have I explained WHY, not just WHAT?
5. Are there stories that make the concepts stick?

If the answer to any of these is "no" - revise until it's "yes."

---

_"The best technical writing doesn't feel like technical writing. It feels like a knowledgeable friend explaining something cool they learned."_
