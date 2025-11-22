# Module 8 Examples: Text Generation & Sampling Strategies

**The Creativity Controls**: Master the dials that transform LLMs from boring robots to creative writers.

---

## 🎨 What You'll Discover

These examples demonstrate how **sampling strategies** (temperature, top-p) are like the **mixing board for an AI DJ** - they control the balance between predictability and creativity in LLM outputs.

**Think of it this way**: Every word an LLM generates is chosen from a probability distribution. Temperature and top-p are the knobs that reshape that distribution:
- **Temperature**: How adventurous the model is (0 = always safe choice, 1+ = experimental)
- **Top-p**: How much of the probability space to consider (0.5 = only top choices, 1.0 = all possibilities)

**You'll learn**: How to dial in the perfect creativity level for any use case - from deterministic code generation to wild brainstorming.

## Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

**Required**:
- Anthropic API key (set in `.env` file as `ANTHROPIC_API_KEY`)
- Examples use Claude 3.5 Sonnet (claude-sonnet-4-5-20250929)

**Create .env file**:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

**Note**: API access is separate from Claude Pro/ChatGPT Plus subscriptions. See [Module 0 theory](../../docs/curriculum/notes/module_00_prerequisites.md#-api-keys-setup) for setup instructions and free alternatives.

## Examples

### Example 1: Sampling Strategy Playground (`01_sampling_playground.py`)

**What it does**: Comprehensive demonstration of sampling strategies with real Claude API outputs.

**Run**:
```bash
python 01_sampling_playground.py
```

**Demonstrations**:
1. **Temperature Effect** - How temperature (0.0 → 1.0) affects variation
2. **Top-p (Nucleus Sampling)** - How top-p filters unlikely tokens
3. **Chatbot Use Case** - Optimal config for conversational AI
4. **Code Generation** - Optimal config for code
5. **Creative Writing** - Optimal config for stories
6. **JSON Extraction** - Optimal config for structured data
7. **Side-by-Side Comparison** - Compare configs directly

**You'll learn**:
- How temperature controls randomness
- When to use different temperature values
- How top-p complements temperature
- Real-world configurations for different use cases

**Sample output**:
```
Configuration: Deterministic (T=0.0)
Temperature: 0.0
Top-p: 1.0
Description: Always picks highest probability - same output every time

Sample 1:
  Photosynthesis is the process by which plants...
Sample 2:
  Photosynthesis is the process by which plants...  (identical!)
Sample 3:
  Photosynthesis is the process by which plants...  (identical!)

✅ Deterministic - same every time
```

**Cost warning**: This example makes multiple API calls (~50-70 requests). Estimated cost: $0.10-0.20 per run.

---

### Example 2: Temperature Explorer (`02_temperature_explorer.py`)

**What it does**: Statistical analysis of temperature effects with variation metrics.

**Run**:
```bash
python 02_temperature_explorer.py
```

**Features**:
1. **Temperature Sweep** - Test multiple temperatures systematically
2. **Variation Analysis** - Statistical metrics on uniqueness
3. **Practical Temperature Finder** - Test on real use cases
4. **Decision Tree** - Interactive guide to choosing temperature

**You'll learn**:
- How to measure output variation
- How to choose optimal temperature for your use case
- Statistical analysis of sampling strategies
- Decision-making framework for temperature selection

**Sample output**:
```
ANALYSIS: Temperature = 0.7
==========================================
Variation metrics:
  Total samples: 10
  Unique full outputs: 7/10 (70%)
  Unique first words: 5/10 (50%)

Most common first words:
  'Photosynthesis': 3/10 (30%) ██████
  'Through': 2/10 (20%) ████
  'Plants': 2/10 (20%) ████

Variability: 🟢 Medium variation - Balanced
```

**Cost warning**: This example makes ~30-40 API calls. Estimated cost: $0.05-0.10 per run.

---

## Quick Start

**Run both examples sequentially**:
```bash
python 01_sampling_playground.py
python 02_temperature_explorer.py
```

**Or run individually based on what you want to learn.**

---

## Key Takeaways

### Temperature: The Creativity Dial

**The Personality**: Temperature is your AI's improvisational coach.

**How it works**: At each word, the LLM has a probability distribution over all possible next words. Temperature **reshapes** this distribution:
- **T=0.0**: Always pick the highest probability word → robotic consistency
- **T=0.5**: Slightly broaden the choices → controlled variety
- **T=1.0**: Use the natural probabilities → balanced creativity
- **T=2.0**: Flatten the distribution → chaotic experimentation

**Real-world analogy**: Directing a play
- `T=0.0`: Actors read the script word-for-word every performance (boring but reliable)
- `T=0.7`: Actors improvise tone and delivery (natural variation)
- `T=1.5`: Actors ad-lib entire scenes (creative, sometimes brilliant, occasionally off-script)

**When to use**:
- **Testing/QA**: `0.0` - Need identical outputs for regression tests
- **Code generation**: `0.2-0.3` - Consistency matters more than variety
- **Chatbots**: `0.7` - Natural conversation with controlled randomness
- **Creative writing**: `1.0-1.2` - Maximum creativity without chaos

### Did You Know?

The term "temperature" comes from **statistical physics** (Boltzmann distribution). In physics, higher temperature means more chaotic particle movement. In LLMs, higher temperature means more chaotic token selection. The metaphor is surprisingly literal!

### Top-p (Nucleus Sampling): The Quality Filter

**The Personality**: Top-p is the bouncer at the creativity club - it decides which words even get considered.

**How it works**: Instead of considering ALL possible next words (tens of thousands!), top-p sets a **cumulative probability threshold**:
- `top_p=0.9`: "Only consider words until their cumulative probability hits 90%"
- This filters out the unlikely, low-quality "tail" of the distribution

**Real-world analogy**: Restaurant menu filtering
- `top_p=1.0`: Full menu (including mystery meat surprise) - all options available
- `top_p=0.9`: Chef's recommended menu - top 90% quality dishes only
- `top_p=0.5`: Prix fixe menu - only the absolute best dishes

**Why it matters**: Even with temperature=1.0, there are millions of possible words. Most are terrible choices. Top-p throws out the garbage before the model even considers them.

**When to use**:
- **Most cases**: `0.9` - Filters out nonsense while allowing creativity
- **Very focused**: `0.5-0.7` - Only high-probability, safe choices
- **Maximum creativity**: `0.95-1.0` - Keep more options on the table

### Did You Know?

Top-p sampling was introduced in a 2019 paper called **"The Curious Case of Neural Text Degeneration"**. Researchers discovered that traditional sampling led to "degenerate" text (repetitive, incoherent). Top-p solved this by dynamically adjusting the candidate pool based on the probability distribution's shape. It's now the default in most LLM APIs!

### Common Configurations

| Use Case | Temperature | Top-p | Why |
|----------|-------------|-------|-----|
| **Code** | 0.2 | 0.5 | Consistency + correctness |
| **JSON** | 0.0 | 1.0 | Deterministic structured data |
| **Chatbot** | 0.7 | 0.9 | Natural variation + quality |
| **Creative** | 1.0 | 0.95 | Creativity + filtering |
| **Brainstorming** | 1.2 | 0.95 | Push creative boundaries |

---

## Understanding the Output

### Deterministic (Temperature = 0.0)
```
Sample 1: "The benefits of AI include improved efficiency."
Sample 2: "The benefits of AI include improved efficiency."
Sample 3: "The benefits of AI include improved efficiency."

→ Perfect for: Testing, structured data, reproducibility
→ Problem: Can be boring, repetitive
```

### Balanced (Temperature = 0.7)
```
Sample 1: "The benefits of AI include improved efficiency and automation."
Sample 2: "AI offers advantages like increased productivity and better decision-making."
Sample 3: "Artificial intelligence provides benefits including enhanced accuracy."

→ Perfect for: Chatbots, content generation, most use cases
→ Problem: None - this is the goldilocks zone!
```

### Creative (Temperature = 1.0)
```
Sample 1: "AI transforms industries by unlocking unprecedented capabilities."
Sample 2: "From healthcare to finance, artificial intelligence reshapes our world."
Sample 3: "The promise of AI lies in augmenting human potential."

→ Perfect for: Creative writing, brainstorming, varied content
→ Problem: Can occasionally be too unpredictable
```

---

## Practical Exercises

After running the examples, try these exercises:

### Exercise 1: Find Your Use Case Temperature

1. **Identify your use case** (e.g., chatbot, code generation, creative writing)
2. **Start with recommended temperature** from the decision tree
3. **Generate 5-10 samples** with that temperature
4. **Evaluate**:
   - Are outputs varied enough? → Increase temperature
   - Are outputs too random? → Decrease temperature
   - Are outputs repetitive? → Increase temperature
5. **Iterate** until you find the sweet spot

### Exercise 2: A/B Test Configurations

1. **Choose a prompt** relevant to your project
2. **Test 3 configurations**:
   - Conservative: `T=0.3, top_p=0.5`
   - Balanced: `T=0.7, top_p=0.9`
   - Creative: `T=1.0, top_p=0.95`
3. **Generate 5 samples each**
4. **Compare quality and variation**
5. **Choose the best** for your use case

### Exercise 3: Measure Consistency

1. **For critical applications** (code, data extraction):
2. **Test temperature=0.0**:
   - Generate 10 samples
   - Verify all outputs are identical
   - If not, investigate why (different model version?)
3. **Test temperature=0.2**:
   - Generate 10 samples
   - Count unique outputs
   - Should have 1-3 unique outputs for good consistency

---

## Common Issues and Solutions

### Issue: "Outputs are all the same"
**Cause**: Temperature too low
**Solution**: Increase temperature to 0.5-0.7 for more variation

### Issue: "Outputs are nonsensical"
**Cause**: Temperature too high
**Solution**: Decrease temperature to 0.7-1.0, or lower top-p

### Issue: "Outputs are repetitive (same phrases)"
**Cause**: Model behavior, not sampling
**Solution**:
- Try different prompts
- Add "be concise" or "vary your phrasing" to prompt
- (Repetition penalty not supported in Claude API, but is in other APIs)

### Issue: "Temperature=0.0 still gives different outputs"
**Cause**: Unlikely, but possible with model updates
**Solution**: Verify API parameters are being sent correctly

### Issue: "Top-p doesn't seem to do anything"
**Cause**: Temperature=0.0 overrides top-p
**Solution**: Use temperature > 0.0 to see top-p effects

---

## Tips for Production

### Always Set Both Parameters
```python
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    temperature=0.7,  # Always explicit
    top_p=0.9,        # Always explicit
    max_tokens=500,   # Control length and cost
    messages=[...]
)
```

### Log Sampling Parameters
```python
# For debugging and optimization
logger.info(f"Generated with temp={temperature}, top_p={top_p}")
logger.info(f"Output tokens: {response.usage.output_tokens}")
```

### A/B Test in Production
```python
# Randomly assign users to different configs
config = random.choice([
    {"temperature": 0.7, "top_p": 0.9},  # Control
    {"temperature": 0.5, "top_p": 0.8},  # Variant A
])
# Track user satisfaction for each config
```

### Use Caching for Deterministic Outputs
```python
# For temperature=0.0, you can cache responses
if temperature == 0.0:
    cache_key = hash(prompt)
    if cache_key in cache:
        return cache[cache_key]
    # Generate and cache
```

---

## Further Reading

- [Anthropic Claude API Docs](https://docs.anthropic.com/claude/reference/messages_post)
- [OpenAI API Docs - Parameters](https://platform.openai.com/docs/api-reference/chat/create)
- [Nucleus Sampling Paper](https://arxiv.org/abs/1904.09751) (Top-p)
- [Hugging Face - Generation Strategies](https://huggingface.co/docs/transformers/generation_strategies)

---

## Next Steps

After mastering sampling strategies:
- **Module 9**: Embeddings & Semantic Similarity
  - What embeddings are (vectors representing meaning)
  - How to calculate semantic similarity
  - Applications: search, clustering, recommendations

---

## Cost Optimization

**Sampling strategies are free!** Changing temperature or top-p doesn't cost extra.

**What does cost**:
- Number of input tokens (prompt)
- Number of output tokens (response length)
- Number of requests

**Cost-saving tips**:
1. Use `max_tokens` to cap response length
2. Cache responses for temperature=0.0 (identical outputs)
3. Batch requests when possible
4. Test with smaller sample sizes first

**Estimated costs for examples**:
- `01_sampling_playground.py`: ~50-70 requests = $0.10-0.20
- `02_temperature_explorer.py`: ~30-40 requests = $0.05-0.10
- **Total**: ~$0.15-0.30 per full run

---

**🥋 Neural Dojo - Master sampling, control your LLM! 🧠⚡**
