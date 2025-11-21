# Module 6 Examples: Introduction to Large Language Models

This directory contains code examples for Module 6: Introduction to Large Language Models.

## Prerequisites

```bash
pip install -r requirements.txt
```

Make sure you have your API key in `.env`:
```bash
ANTHROPIC_API_KEY=your_key_here
```

## Examples

### 01_model_comparison.py
**Description**: Comprehensive demonstration of LLM API integration and model comparison.

**What it demonstrates**:
- Making API calls to Claude
- Measuring latency and token usage
- Testing different model capabilities (reasoning, code, long context)
- System prompts for behavior control
- Temperature for controlling randomness

**Run**:
```bash
python 01_model_comparison.py
```

**Expected output**:
- Model responses for various tasks
- Token usage statistics
- Latency measurements
- Comparison of deterministic vs creative outputs

**Cost**: ~$0.05-0.10 in API credits

## Key Concepts Demonstrated

1. **API Integration**: How to call LLM APIs programmatically
2. **Model Selection**: Choosing the right model for the task
3. **Token Counting**: Understanding token usage for cost optimization
4. **Latency Measurement**: Tracking response times
5. **System Prompts**: Controlling model behavior
6. **Temperature**: Controlling output randomness

## Tips

- Start with small prompts to minimize costs while learning
- Monitor token usage to understand costs
- Compare outputs across multiple runs for non-deterministic settings
- Use temperature=0.0 for consistent outputs in testing

## Next Steps

After running these examples:
1. Try modifying prompts to see how responses change
2. Test with your own use cases
3. Compare token usage for different prompt styles
4. Move on to Module 7 to learn about tokenization

---

For theory and detailed explanations, see:
`docs/curriculum/notes/module_06_intro_to_llms.md`
