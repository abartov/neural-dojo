# Workflow 03: AI-Assisted Code Review

**Scenario**: Reviewing a pull request that adds a new payment processing feature

**Duration**: ~20 minutes (vs ~45-60 minutes manual review)

**Tools Used**:
- Claude Code (architecture and security review)
- GitHub Copilot (suggesting test improvements)

---

## 📋 The Pull Request

**Changes**: 8 files, +450 lines, -120 lines

**Feature**: Add Stripe payment processing
- New `PaymentService` class
- Payment models and migrations
- API endpoints for payment processing
- Webhook handler for Stripe events

---

## 🔍 Step 1: Get the Diff

```bash
# Option 1: Using git
git diff main feature/stripe-payments > pr_diff.txt

# Option 2: Using GitHub CLI
gh pr diff 123 > pr_diff.txt

# Option 3: Copy from GitHub PR page
```

---

## 🤖 Step 2: Architectural Review (Claude Code)

### Prompt

```
Please review this pull request for architectural soundness, best practices, and potential issues.

**Context**:
This adds Stripe payment processing to our FastAPI e-commerce app.

**PR Diff**:
[paste the full diff]

**Review focus areas**:
1. Architecture and design patterns
2. Error handling
3. Security concerns (especially payment data)
4. Code organization
5. Missing tests or edge cases
6. Performance considerations

Provide:
- High-level feedback on approach
- Specific line-by-line issues with file:line references
- Suggestions for improvements
```

### Example Claude Response

```markdown
## Architectural Review

### Overall Assessment
✅ **Good**: Separation of concerns (service layer, models, routes)
✅ **Good**: Using environment variables for Stripe keys
⚠️ **Concern**: Webhook verification could be stronger
❌ **Issue**: Missing transaction rollback on payment failure

### Specific Issues

#### 1. Security - Webhook Signature Verification
**File**: `src/api/webhooks.py:15`

**Issue**:
```python
# Current code:
signature = request.headers.get("Stripe-Signature")
if not signature:
    return {"error": "No signature"}
```

**Problem**: Should return 401, not 200 with error message. Stripe will retry if non-200.

**Fix**:
```python
signature = request.headers.get("Stripe-Signature")
if not signature:
    raise HTTPException(status_code=401, detail="Missing signature")
```

#### 2. Transaction Safety
**File**: `src/services/payment.py:45`

**Issue**:
```python
# Current code:
payment = Payment(...)
db.add(payment)
db.commit()

# Call Stripe API
stripe_result = stripe.PaymentIntent.create(...)

# Update payment status
payment.status = stripe_result.status
db.commit()
```

**Problem**: If Stripe call fails, payment record exists with wrong status.

**Fix**: Use try/except with rollback:
```python
payment = Payment(status="pending")
db.add(payment)
db.commit()

try:
    stripe_result = stripe.PaymentIntent.create(...)
    payment.status = "completed"
    payment.stripe_id = stripe_result.id
    db.commit()
except stripe.error.StripeError as e:
    payment.status = "failed"
    payment.error = str(e)
    db.commit()
    raise
```

#### 3. Missing Validation
**File**: `src/api/routes/payments.py:28`

**Missing**: Amount validation (should reject $0 or negative amounts)

**Add**:
```python
if payment_request.amount <= 0:
    raise HTTPException(status_code=400, detail="Amount must be positive")
```

#### 4. Test Coverage Gap
**Missing**: Tests for webhook replay attacks

**Add test**:
```python
def test_webhook_replay_attack():
    # Send same webhook twice
    # Second one should be rejected (idempotency check)
```

### Recommendations

1. **Immediate fixes required**:
   - Fix webhook error codes
   - Add transaction rollback
   - Add amount validation

2. **Nice to have**:
   - Add idempotency keys to Stripe calls
   - Log all payment attempts for audit trail
   - Add monitoring/alerts for failed payments

3. **Future improvements**:
   - Consider retry logic with exponential backoff
   - Add payment refund functionality
   - Support multiple payment providers (abstraction)
```

---

## ✅ Step 3: Security Scan (Claude Code)

### Focused Security Prompt

```
Review this payment processing code specifically for security vulnerabilities:

[paste payment-related files]

Check for:
- SQL injection
- Sensitive data logging
- API key exposure
- CSRF vulnerabilities
- Rate limiting
- Input validation
- PCI compliance issues
```

Claude will identify:
- Hardcoded secrets (if any)
- Missing rate limiting on payment endpoints
- Logging sensitive data (card numbers, CVV)
- Missing HTTPS enforcement

---

## 🧪 Step 4: Test Quality Review (Copilot)

Open the test file and use Copilot to suggest missing tests:

```python
# In tests/test_payments.py
# Type: # Test cases to add:
# Copilot suggests:

# Test cases to add:
# - Payment with invalid amount (negative, zero)
# - Payment with expired card
# - Payment with insufficient funds
# - Webhook with invalid signature
# - Webhook with replay attack
# - Concurrent payment requests (race condition)
# - Payment timeout handling

# Then implement each:
def test_payment_negative_amount():
    # Copilot fills in the test
    ...
```

---

## 📝 Step 5: Leave PR Comments

Use Claude's output to create actionable PR comments:

**GitHub Comment Format**:

```markdown
## Architecture Review

Great work on the payment integration! A few issues to address:

### 🔴 Must Fix

1. **Webhook error codes** (`webhooks.py:15`)
   - Return 401 instead of 200 for invalid signatures
   - Reason: Stripe retries on non-200, won't retry on 200

2. **Transaction safety** (`payment.py:45`)
   - Add rollback on Stripe API failure
   - See suggested code above

3. **Amount validation** (`routes/payments.py:28`)
   - Reject negative/zero amounts

### 🟡 Should Fix

4. **Missing tests**
   - Webhook replay attacks
   - Invalid amount handling
   - Payment failures

5. **Security**
   - Add rate limiting on payment endpoints (prevent abuse)
   - Ensure no sensitive data in logs

### 💡 Future Improvements

- Idempotency keys for all Stripe calls
- Monitoring/alerts for failed payments
- Refund functionality

Let me know if you want help implementing any of these!
```

---

## ✅ Code Review Checklist

### Automated Checks (AI-assisted)

- [ ] **Architecture**: Separation of concerns, design patterns
- [ ] **Security**: Vulnerabilities, data exposure, authentication
- [ ] **Error Handling**: Try/catch, rollbacks, proper status codes
- [ ] **Testing**: Coverage, edge cases, integration tests
- [ ] **Performance**: N+1 queries, caching, inefficient algorithms
- [ ] **Code Quality**: Readability, naming, comments
- [ ] **Documentation**: API docs, README updates, inline comments

### Manual Checks (Human required)

- [ ] **Business Logic**: Requirements met correctly
- [ ] **User Experience**: API design, error messages
- [ ] **Compliance**: GDPR, PCI-DSS, industry regulations
- [ ] **Team Standards**: Follows project conventions
- [ ] **Dependencies**: New packages justified and secure

---

## 📊 Time Savings

**Manual Review**:
- Read through all changes: 20 min
- Check for issues: 15 min
- Test manually: 10 min
- Write comments: 10 min
- **Total: ~45-60 minutes**

**AI-Assisted Review**:
- Get diff: 2 min
- AI analysis: 5 min (while you make coffee!)
- Review AI findings: 8 min
- Manual checks (business logic): 5 min
- Write comments: 5 min
- **Total: ~20 minutes**

**Savings: 50-65%** + higher quality review

---

## 🎓 Key Learnings

1. **AI Spots Patterns**: Excellent at finding common anti-patterns
2. **AI Doesn't Understand Business Logic**: You still need to verify requirements
3. **AI is Thorough**: Often finds issues humans miss (transaction rollback, edge cases)
4. **Combine with Tests**: Ask AI to suggest missing tests
5. **Iterative**: Review AI feedback, then review code yourself

---

## 🚀 Advanced: Automated PR Review

Create a script that automatically reviews PRs:

```bash
#!/bin/bash
# review-pr.sh

PR_NUMBER=$1
gh pr diff $PR_NUMBER > /tmp/pr_diff.txt

# Use Claude API or local model
cat > /tmp/review_prompt.txt << EOF
Review this pull request for issues.
Focus on: security, performance, best practices.

$(cat /tmp/pr_diff.txt)
EOF

# Call AI (example with Claude API)
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "messages": [{"role": "user", "content": "'$(cat /tmp/review_prompt.txt)'"}]
  }' | jq -r '.content[0].text'
```

Run on every PR: `./review-pr.sh 123`

---

**Remember**: AI reviews are a **supplement**, not a replacement. Always apply human judgment, especially for business logic and compliance.
