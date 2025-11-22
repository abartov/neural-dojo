# Workflow 05: Learning a New Codebase with AI

**Scenario**: You just joined a team and need to understand a Django project (50K lines)

**Duration**: ~2 hours to get productive (vs ~2-3 days without AI)

**Tools Used**:
- Claude Code / ChatGPT / Gemini (codebase analysis)
- VSCode with Continue.dev (contextual Q&A)
- GitHub Copilot (learning by example)

---

## 🎯 Goal

Go from "never seen this code" to "can make changes confidently":
- Understand architecture
- Know where to find things
- Understand patterns and conventions
- Make first contribution

---

## 📋 Step 1: High-Level Overview (Claude Code / ChatGPT)

### First Prompt

```
I'm new to this codebase. Help me understand the architecture.

**Project**: Django e-commerce platform

**Directory structure**:
```
ls -la
```
[paste output]

**README.md**:
[paste README]

**requirements.txt**:
[paste requirements]

Questions:
1. What does this application do (high-level)?
2. What's the architecture pattern (monolith, microservices, etc.)?
3. What are the main components/apps?
4. What technologies/frameworks are used?
5. Where should I start reading code?
```

### AI Response Example

```
## Architecture Overview

**Application**: E-commerce platform for selling digital products

**Type**: Django monolith with:
- REST API (Django REST Framework)
- PostgreSQL database
- Redis caching
- Celery background tasks
- Stripe payment integration

**Main Django Apps**:
1. `products/` - Product catalog
2. `orders/` - Order management
3. `users/` - User accounts and auth
4. `payments/` - Stripe integration
5. `notifications/` - Email/SMS notifications

**Data Flow**:
```
User → Frontend → API (DRF) → Business Logic → Database
                              ↓
                        Background Tasks (Celery)
                              ↓
                        External Services (Stripe, Email)
```

**Start Here**:
1. `products/views.py` - Simple CRUD, good entry point
2. `orders/models.py` - Core data models
3. `api/urls.py` - All API endpoints

**Patterns Used**:
- Repository pattern (`repositories/`)
- Service layer (`services/`)
- Serializers for API (`serializers.py` in each app)
```

---

## 📋 Step 2: Understand Data Models (Continue.dev in VSCode)

Open VSCode, install Continue.dev, press **Cmd+L**:

### Prompts

```
@codebase What are the main data models and their relationships?
```

```
@codebase Explain the User → Order → Product relationship
```

```
@codebase Show me how orders are created (from API call to database)
```

Continue.dev will:
- Analyze your models.py files
- Show relationships (ForeignKey, ManyToMany)
- Trace the flow through the code

---

## 📋 Step 3: Find Code Patterns (GitHub Copilot)

Open an existing endpoint, read it, then try to write a new one:

### Example: Learning by Replication

**Step 1**: Read existing code
```python
# products/views.py
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        products = self.queryset.filter(is_active=True)
        serializer = self.serializer_class(products, many=True)
        return Response(serializer.data)
```

**Step 2**: Try to create similar endpoint
```python
# Type: class OrderViewSet
# Copilot suggests:

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        # Copilot suggests filtering for current user
        orders = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(orders, many=True)
        return Response(serializer.data)
```

Copilot **learned the pattern** from existing code!

---

## 📋 Step 4: Trace Complex Flows (Claude Code)

For complex workflows, ask Claude to trace the flow:

### Prompt

```
Trace the complete flow for "User places an order":

Starting from: POST /api/orders
Ending at: Order confirmation email sent

Show me:
1. API endpoint that handles the request
2. Validation steps
3. Database operations
4. Payment processing
5. Background tasks
6. Email sending

Provide file names and line numbers for each step.
```

### Claude Response Example

```
## Order Placement Flow

### 1. API Endpoint
**File**: `orders/views.py:45`
```python
@api_view(['POST'])
def create_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    # Call service layer
    order = order_service.create_order(
        user=request.user,
        items=serializer.validated_data['items']
    )

    return Response(OrderSerializer(order).data)
```

### 2. Service Layer
**File**: `orders/services.py:12`
```python
def create_order(user, items):
    # Validate inventory
    for item in items:
        if not inventory_service.check_availability(item):
            raise OutOfStockError()

    # Create order
    order = Order.objects.create(user=user, status='pending')

    # Add items
    for item in items:
        OrderItem.objects.create(order=order, ...)

    # Process payment
    payment_service.process_payment(order)

    # Send to background task
    tasks.send_order_confirmation.delay(order.id)

    return order
```

### 3. Payment Processing
**File**: `payments/services.py:28`
```python
def process_payment(order):
    stripe_payment = stripe.PaymentIntent.create(
        amount=order.total_amount,
        customer=order.user.stripe_id
    )

    order.payment_status = 'completed'
    order.save()
```

### 4. Background Task
**File**: `tasks/notifications.py:15`
```python
@celery.task
def send_order_confirmation(order_id):
    order = Order.objects.get(id=order_id)
    send_email(
        to=order.user.email,
        template='order_confirmation',
        context={'order': order}
    )
```

**Summary**: Request → View → Service → Payment → Background Task → Email
```

---

## 📋 Step 5: Understanding Tests (Learn by Example)

Read existing tests to understand how things work:

```python
# tests/test_orders.py

def test_create_order_success():
    # Shows how to:
    # - Set up test data
    # - Make API requests
    # - Assert expectations

    user = User.objects.create(email="test@example.com")
    product = Product.objects.create(name="Test", price=10)

    response = client.post('/api/orders', {
        'items': [{'product_id': product.id, 'quantity': 1}]
    })

    assert response.status_code == 201
    assert Order.objects.count() == 1
```

**Insight**: Tests are documentation! They show how the code is *supposed* to work.

---

## 📋 Step 6: Ask Specific Questions (Continue.dev)

As you work, ask questions:

```
Cmd+L in VSCode with Continue.dev:

"@codebase How do I add a new field to the Order model?"

"@codebase Where are email templates defined?"

"@codebase How does authentication work in this project?"

"@codebase What's the convention for naming API endpoints?"
```

---

## 📋 Step 7: Make Your First Change

**Task**: Add a "gift message" field to orders

### Prompt to Claude/ChatGPT

```
I want to add a "gift_message" field to orders.

**Requirements**:
- Optional text field (max 500 chars)
- Include in Order model
- Show in API responses
- Add to order creation form

Following this project's patterns, what files do I need to change?
```

### AI Response

```
Files to change:

1. **Model**: `orders/models.py`
   Add field to Order model

2. **Migration**: Generate migration
   `python manage.py makemigrations`

3. **Serializer**: `orders/serializers.py`
   Add field to OrderSerializer

4. **Validation**: `orders/serializers.py`
   Add max_length validation

5. **Tests**: `tests/test_orders.py`
   Test gift message in order creation

Here's the code for each:
[AI provides implementation]
```

### Implement with Copilot

**File**: `orders/models.py`

```python
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)

    # Type: # Add gift message field (optional, max 500 chars)
    # Copilot suggests:
    gift_message = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional gift message to include with order"
    )
```

**File**: `orders/serializers.py`

```python
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'created_at', 'status', 'gift_message']  # Added

    # Type: def validate_gift_message
    # Copilot suggests validation:
    def validate_gift_message(self, value):
        if value and len(value) > 500:
            raise serializers.ValidationError("Gift message too long")
        return value
```

---

## ✅ Learning Checklist

After 2 hours, you should be able to:

- [ ] Explain what the application does
- [ ] Navigate to any major component
- [ ] Understand the data model relationships
- [ ] Trace a request through the system
- [ ] Write code following project patterns
- [ ] Run tests and understand test structure
- [ ] Make a small contribution (like adding a field)

---

## 📊 Time Comparison

**Without AI**:
- Read documentation: 2 hours
- Read code randomly: 4 hours
- Ask team members: 2 hours (interrupt their work)
- Trial and error: 4 hours
- **Total: ~2-3 days to be productive**

**With AI**:
- High-level overview (AI): 20 min
- Understand models (AI): 30 min
- Trace flows (AI): 40 min
- Read tests: 20 min
- Make first change: 30 min
- **Total: ~2 hours to be productive**

**Speedup: 10x faster onboarding!**

---

## 🎓 Key Learnings

1. **Start High-Level**: Architecture first, details later
2. **AI is a Tour Guide**: It can show you around faster than reading randomly
3. **Tests are Documentation**: Always read tests to understand expected behavior
4. **Learn by Doing**: Make a small change early
5. **Ask Specific Questions**: The more context you give AI, the better
6. **Copilot Learns Patterns**: Great for matching team's coding style

---

## 💡 Advanced: Create a Codebase Summary

Use AI to create a markdown doc for your team:

### Prompt

```
Create a comprehensive onboarding document for this codebase.

Include:
1. Architecture overview
2. Data model diagram (mermaid)
3. Main workflows (user signup, order placement, etc.)
4. Code organization and patterns
5. How to run locally
6. How to run tests
7. Common tasks (adding a field, creating an endpoint, etc.)

Output as markdown suitable for README or docs/.
```

Save the output as `docs/ONBOARDING.md` for the next new team member!

---

**Remember**: AI accelerates learning, but there's no substitute for actually writing code. Use AI to understand faster, then get your hands dirty.
