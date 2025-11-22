# Workflow 02: Debugging Production Issues with AI

**Scenario**: Users reporting intermittent 500 errors on `/api/orders` endpoint

**Duration**: ~45 minutes (vs ~2-3 hours without AI)

**Tools Used**:
- Claude Code (root cause analysis)
- Copilot (writing fixes and tests)

---

## 🚨 The Problem

**User Reports**:
- "Sometimes I get 500 errors when placing orders"
- "Works most of the time, fails randomly"
- "No pattern - morning/evening, large/small orders"

**Initial Observation**:
- No errors in development environment
- Happens in production only
- Intermittent (not every request)

---

## 📋 Step 1: Gather Context

Before asking AI, collect the data:

```bash
# Get recent error logs
grep "500" /var/log/app/error.log | tail -50 > errors.txt

# Get the endpoint code
cat src/api/routes/orders.py

# Check recent changes
git log --oneline --since="1 week ago" src/api/routes/orders.py

# Get full stack trace
grep -A 20 "Traceback" /var/log/app/error.log | head -30 > stacktrace.txt
```

**Collected Data**:
```
Error: KeyError: 'inventory_id'
File: src/api/routes/orders.py, line 45
Recent changes: "Add inventory check before order" (3 days ago)
```

---

## 📋 Step 2: Systematic Analysis (Claude Code)

### Prompt Template

```
I have an intermittent production bug. Help me debug systematically.

**Error**:
[paste error message and stack trace]

**Endpoint Code**:
[paste src/api/routes/orders.py]

**Recent Changes**:
[paste git log or git diff]

**Environment**:
- Dev: Works fine
- Prod: Intermittent 500 errors (KeyError: 'inventory_id')

**Questions**:
1. Why would this work in dev but fail intermittently in prod?
2. What could cause 'inventory_id' to be missing sometimes?
3. How should I debug this step by step?

Please analyze and suggest:
- Root cause hypotheses (ranked by likelihood)
- Investigation steps
- Potential fixes
```

### Claude's Analysis Example

```
Analysis of the KeyError: 'inventory_id' issue:

**Most Likely Causes** (ranked):

1. **Race Condition (80% likely)**:
   - Code assumes inventory record exists
   - Another request might delete/update inventory between check and access
   - Explains why it's intermittent (timing-dependent)
   - Explains why dev works (low traffic, synchronous testing)

2. **Data Inconsistency (15% likely)**:
   - Some products missing inventory records in prod database
   - Works in dev because test data is complete
   - Should be consistent, not intermittent

3. **Caching Issue (5% likely)**:
   - Stale cache returning incomplete data
   - Less likely given KeyError (not wrong value)

**Investigation Steps**:

1. Add defensive checks:
   ```python
   inventory = inventory_dict.get('inventory_id')
   if inventory is None:
       logger.error(f"Missing inventory_id for product {product_id}")
       # Log full inventory_dict for debugging
   ```

2. Check database:
   ```sql
   -- Find products without inventory
   SELECT p.id, p.name
   FROM products p
   LEFT JOIN inventory i ON p.id = i.product_id
   WHERE i.id IS NULL;
   ```

3. Add logging before the error line:
   ```python
   logger.info(f"Inventory dict: {inventory_dict}")
   # Then access inventory_dict['inventory_id']
   ```

**Recommended Fix**:

Use .get() with default and proper error handling:

```python
# Bad (current):
inventory_id = inventory_dict['inventory_id']  # KeyError if missing!

# Good:
inventory_id = inventory_dict.get('inventory_id')
if inventory_id is None:
    logger.error(f"Product {product_id} missing inventory")
    raise HTTPException(
        status_code=400,
        detail="Product inventory not found"
    )
```
```

---

## 📋 Step 3: Add Defensive Logging (Copilot)

Open `src/api/routes/orders.py` and add logging:

```python
# Type: # Add detailed logging before inventory access
# Copilot suggests:

logger.info(f"Processing order for product {product_id}")
logger.debug(f"Inventory dict: {inventory_dict}")

# Then use safe access
inventory_id = inventory_dict.get('inventory_id')
if inventory_id is None:
    logger.error(
        f"Missing inventory_id for product {product_id}. "
        f"Available keys: {inventory_dict.keys()}"
    )
    raise HTTPException(status_code=400, detail="Product inventory not found")
```

---

## 📋 Step 4: Deploy Logging and Monitor

```bash
# Deploy with new logging
git add src/api/routes/orders.py
git commit -m "Add defensive logging for inventory access"
git push

# Watch logs in prod
tail -f /var/log/app/error.log | grep "inventory"
```

**Wait for the error to occur again** to see detailed logging.

---

## 📋 Step 5: Root Cause Confirmed (Example)

After deploying, logs show:

```
ERROR: Missing inventory_id for product 12345
ERROR: Available keys: dict_keys(['product_id', 'quantity', 'warehouse'])
```

**Aha!** The inventory query returns a dict without `inventory_id` field!

---

## 📋 Step 6: Fix the Root Cause (Claude Code)

### Prompt

```
The inventory query returns a dict without 'inventory_id'.

Here's the query code:
[paste inventory query code]

The dict has: product_id, quantity, warehouse
But we need: inventory_id

Please fix the query to include inventory_id in the result.
```

Claude identifies the issue in the query and provides fix:

```python
# Bad (current):
inventory_dict = {
    'product_id': row.product_id,
    'quantity': row.quantity,
    'warehouse': row.warehouse
    # Missing: 'inventory_id': row.id
}

# Good (fixed):
inventory_dict = {
    'inventory_id': row.id,  # ← Added!
    'product_id': row.product_id,
    'quantity': row.quantity,
    'warehouse': row.warehouse
}
```

---

## 📋 Step 7: Write Regression Test (Copilot)

**File**: `tests/test_orders.py`

```python
# Type: def test_order_with_complete_inventory():
# Copilot suggests:

def test_order_with_complete_inventory():
    """Test that order endpoint handles complete inventory data."""
    response = client.post("/api/orders", json={
        "product_id": 123,
        "quantity": 5
    })
    assert response.status_code == 200

# Type: def test_order_with_missing_inventory_id():
# Copilot suggests regression test:

def test_order_with_missing_inventory_id():
    """Regression test for KeyError: 'inventory_id'."""
    # Mock inventory without 'inventory_id' field
    with patch('src.api.routes.orders.get_inventory') as mock:
        mock.return_value = {
            'product_id': 123,
            'quantity': 10,
            'warehouse': 'A'
            # Missing 'inventory_id'!
        }
        response = client.post("/api/orders", json={
            "product_id": 123,
            "quantity": 5
        })
        # Should return 400, not 500
        assert response.status_code == 400
        assert "inventory not found" in response.json()["detail"].lower()
```

---

## 📋 Step 8: Verify Fix

```bash
# Run tests
pytest tests/test_orders.py -v

# Deploy to staging
git push staging

# Test manually
curl -X POST https://staging.api/orders \
  -H "Content-Type: application/json" \
  -d '{"product_id": 12345, "quantity": 2}'

# Monitor for 24 hours - no more 500 errors!

# Deploy to production
git push production
```

---

## ✅ Debugging Checklist

- [ ] **Gather Context**: Logs, stack traces, recent changes
- [ ] **AI Analysis**: Get hypotheses ranked by likelihood
- [ ] **Add Logging**: Make the invisible visible
- [ ] **Monitor**: Wait for error with detailed logs
- [ ] **Confirm Root Cause**: Verify hypothesis with data
- [ ] **Fix**: Apply solution
- [ ] **Regression Test**: Ensure it doesn't happen again
- [ ] **Deploy**: Staging → Production
- [ ] **Verify**: Monitor for 24-48 hours

---

## 📊 Time Comparison

**Without AI** (estimated):
- Reproduce bug: 30-60 min
- Debug (trial and error): 1-2 hours
- Fix: 15 min
- Test: 15 min
- **Total: 2-3 hours**

**With AI** (actual):
- Gather context: 10 min
- AI analysis: 5 min
- Add logging: 10 min
- Root cause (after monitoring): 15 min
- Fix and test: 15 min
- **Total: ~45 minutes (plus waiting time)**

**Savings: 60-70%** (plus higher confidence in fix)

---

## 🎓 Key Learnings

1. **Provide Full Context**: Error message + code + environment differences
2. **AI is Great at Pattern Recognition**: It spots "race condition" or "missing data" patterns quickly
3. **But AI Can't Run Your Code**: You still need logging and monitoring
4. **Systematic > Random**: AI helps create investigation plan
5. **Always Add Regression Test**: Prevent the bug from coming back

---

## 🔄 Common Debugging Patterns

### Pattern 1: Works in Dev, Fails in Prod
**AI Prompt**: "This works in dev but fails in prod with error X. What environmental differences could cause this?"

**Common Causes AI Will Suggest**:
- Database differences (data, schema, constraints)
- Environment variables
- Concurrency (prod has more traffic)
- File permissions
- Network/firewall rules
- Timing/race conditions

---

### Pattern 2: Intermittent Errors
**AI Prompt**: "This error happens randomly, not every time. Error: X. Code: Y. What could cause intermittent failures?"

**Common Causes AI Will Suggest**:
- Race conditions
- Memory leaks (fails after N requests)
- Cache invalidation issues
- Network timeouts
- Resource exhaustion

---

### Pattern 3: Worked Before, Broke Recently
**AI Prompt**: "This broke after recent changes: [git diff]. Error: X. What in the diff likely caused this?"

**AI Will**:
- Analyze the diff
- Point to likely culprit
- Explain why that change breaks the code
- Suggest fix

---

## 🚀 Next Steps

- Practice this workflow on your own bugs
- Build a debugging checklist for your team
- Collect common error patterns and fixes
- Share learnings with team

---

**Remember**: AI accelerates debugging but can't replace systematic thinking. Use AI to augment your problem-solving, not replace it.
