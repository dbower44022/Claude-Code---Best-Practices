# Testing and Debugging

## Overview

Testing and debugging are where Claude Code delivers some of its highest-value contributions. Claude can generate comprehensive test suites from specifications, trace bugs through unfamiliar code, and explain failures in context. This document covers practical workflows for test-driven development, targeted test generation, systematic debugging, and maintaining test quality at scale.

## Test-Driven Development with Claude

Test-driven development with Claude inverts the typical AI coding workflow. Instead of asking Claude to write code and then hoping it is correct, you write the tests first and ask Claude to make them pass. The tests serve as an unambiguous specification that Claude can target.

**The TDD pattern with Claude:**

1. You write a test describing the desired behavior
2. You ask Claude to make the test pass
3. You review the implementation
4. You refactor if needed, keeping tests green

**Example: Building a rate limiter with TDD**

Start by writing the test yourself:

```python
# tests/test_rate_limiter.py
import pytest
from datetime import datetime, timedelta
from services.rate_limiter import RateLimiter, RateLimitExceeded

class TestRateLimiter:
    def test_allows_requests_under_limit(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            assert limiter.check("user-123") is True

    def test_blocks_requests_over_limit(self):
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        for _ in range(5):
            limiter.check("user-123")
        with pytest.raises(RateLimitExceeded) as exc_info:
            limiter.check("user-123")
        assert exc_info.value.retry_after > 0

    def test_separate_limits_per_key(self):
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        limiter.check("user-a")
        limiter.check("user-a")
        # user-b should still have their full allowance
        assert limiter.check("user-b") is True

    def test_window_resets_after_expiry(self, monkeypatch):
        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.check("user-123")
        # Advance time past the window
        future = datetime.now() + timedelta(seconds=61)
        monkeypatch.setattr("services.rate_limiter.datetime",
                          type("MockDatetime", (), {"now": staticmethod(lambda: future)}))
        assert limiter.check("user-123") is True
```

Now give these tests to Claude:

```
Here are my tests for a rate limiter in tests/test_rate_limiter.py. Implement the
RateLimiter class in services/rate_limiter.py that makes all these tests pass. Use
an in-memory sliding window approach. Don't add any dependencies beyond the standard library.
```

Claude produces an implementation targeted at your exact specification. If it passes the tests, you know it meets your requirements. If it does not, the test failures tell you exactly what is wrong.

**When TDD with Claude works best:**

- Pure functions and services with clear inputs and outputs
- API endpoint handlers where you can write request/response tests
- Data transformations where you can specify input/output pairs
- Business rules where you can enumerate the cases

**When TDD with Claude is harder:**

- UI components where behavior is visual
- Infrastructure code where the tests need complex mocking
- Performance-sensitive code where correctness is necessary but not sufficient

In these cases, you may want to write the implementation first and add tests after, or write integration tests that exercise the full stack.

## Generating Meaningful Tests

When you ask Claude to write tests, the quality of the output depends directly on how specific your request is. Vague requests produce vague tests. Specific scenario lists produce targeted, useful tests.

**Weak prompt:**
```
Write tests for the OrderService.
```

This produces generic tests that check the happy path and maybe one error case. They pass, but they do not catch real bugs.

**Strong prompt:**
```
Write tests for OrderService.create_order in tests/test_order_service.py.
Cover these scenarios:

1. Valid order — all fields present, inventory available, payment succeeds
2. Missing required fields — no shipping_address, no line_items, empty line_items
3. Insufficient inventory — one item has stock=0, one item has stock less than quantity
4. Payment failure — payment gateway returns declined, gateway timeout
5. Concurrent order conflict — two orders for the last unit of the same item
6. Price changed since cart — item price in the order doesn't match current price
7. Order total calculation — tax calculation, discount application, free shipping threshold

Use the existing fixtures in conftest.py for test data. Mock the payment gateway
using the MockPaymentGateway in tests/mocks/. For the concurrency test, use
threading to simulate simultaneous requests.
```

This produces tests that actually exercise the edge cases where bugs live.

**Ask for test descriptions first on complex domains:**

If you are not sure what scenarios to test, ask Claude to help you enumerate them before writing test code:

```
I need to test the subscription billing system in services/billing.py. Before
writing any tests, list the scenarios we should cover for the renew_subscription
method. Consider: payment states, subscription states, plan changes, proration,
trial periods, grace periods, and error conditions.
```

Review the list, add anything Claude missed, remove anything irrelevant, then ask Claude to write the tests.

**Testing patterns that Claude generates well:**

Parameterized tests are a natural fit for Claude because they are structured and repetitive:

```
Write parameterized tests for the currency conversion function. Test these pairs:
USD→EUR, EUR→GBP, JPY→USD, BTC→USD. For each pair, test: a standard amount,
zero, a very large amount (1 billion), and a negative amount (should raise ValueError).
Use @pytest.mark.parametrize.
```

Claude handles the boilerplate of parameterized tests well and rarely makes mistakes in the test structure itself.

**Fixture-based tests** also work well because Claude can read your existing fixtures and follow the pattern:

```
I have fixtures in tests/conftest.py for creating test users and organizations.
Write integration tests for the TeamService that use these fixtures. Each test
should create a fresh team using the fixture data, perform the operation, and
verify the result by querying the database.
```

## Debugging Workflows

Claude is a strong debugger when you give it enough context. It excels at logical debugging — reading code, tracing execution paths, analyzing stack traces, and identifying root causes from error messages. It cannot attach debuggers, inspect runtime state, or profile performance, so for those tasks use your standard tooling and share the output with Claude for analysis.

The key is to provide the error, the relevant code, and the circumstances under which the error occurs.

**Basic debugging pattern:**

```
I'm getting this error when processing orders with more than 10 line items:

```
Traceback (most recent call last):
  File "services/order_processor.py", line 145, in process_order
    events = self.event_bus.publish(order_event)
  File "services/event_bus.py", line 67, in publish
    serialized = self.serializer.serialize(event)
  File "services/serializer.py", line 23, in serialize
    return json.dumps(payload)
TypeError: Object of type Decimal is not JSON serializable
```

The error only happens with large orders. Small orders (under 10 items) work fine.
The order_event is created in services/order_processor.py around line 140.
Can you trace through the code and figure out why this only affects large orders?
```

Claude reads the referenced files, traces the code path, and identifies that large orders trigger a different code path (perhaps a batch processing branch) that does not convert Decimal fields to floats before serialization.

**Debugging with log output:**

When the error is not a crash but incorrect behavior, share the relevant log output:

```
Users are reporting that their notification preferences are being reset after
updating their profile. Here's what I see in the logs:

```
2025-01-15 14:23:01 INFO  UserService.update_profile user_id=456 fields=["display_name"]
2025-01-15 14:23:01 DEBUG UserSerializer.serialize including_fields=["id","display_name","email","notification_prefs"]
2025-01-15 14:23:02 INFO  UserService.save user_id=456
2025-01-15 14:23:02 DEBUG UserRepository.update SET display_name='New Name', notification_prefs=NULL
```

It looks like notification_prefs is being set to NULL during the profile update,
but the user only changed their display_name. The relevant code is in
services/user_service.py (update_profile method) and api/serializers.py
(UserSerializer). Can you investigate?
```

Claude can read the serializer and service code to identify that the serializer is including notification_prefs in the update payload with a null value when the field is not provided, and the repository is interpreting null as "set to NULL" rather than "do not update."

**Debugging with reproduction steps:**

For intermittent bugs, providing the conditions that trigger the bug is more valuable than the error itself:

```
We have a race condition in the session management system. It happens
when a user has two tabs open and both tabs make API requests at the same time.
About 1 in 20 times, one of the requests gets a 401 Unauthorized even though the
user is logged in. The session token is stored in Redis (see config/redis.py) and
validated in middleware/auth.py. The token refresh logic is in services/auth.py.
I suspect the token refresh in one tab is invalidating the token that the other
tab is using. Can you trace through the code and confirm?
```

## Understanding Unfamiliar Test Failures

When tests fail and you do not immediately understand why, Claude can investigate systematically. This is especially useful when you are working in an unfamiliar part of the codebase, dealing with inherited code, or encountering failures in tests you did not write.

**Share the test output and ask Claude to investigate:**

```
This test is failing and I'm not sure why:

```
FAILED tests/integration/test_checkout.py::TestCheckout::test_apply_discount_code
AssertionError: assert 89.99 == 90.00
```

The test is in tests/integration/test_checkout.py. The discount logic is in
services/pricing.py. I think the fixtures are in tests/fixtures/discounts.json.
Can you read these files and explain what's going wrong?
```

Claude reads the test, the code under test, and the fixtures, then explains the discrepancy. Maybe the test expects a 10% discount on a $100 item to produce $90.00, but the code applies the discount after tax, resulting in $89.99.

**For cascading failures where many tests fail at once:**

```
After merging the latest changes, 14 tests in tests/integration/ are failing.
They all seem related to database operations. Here's the output from the first
three failures:

[paste test output]

The common error is "relation 'orders_v2' does not exist." I think this is
related to the migration we added in migrations/0047_rename_orders_table.py.
Can you look at the migration and the test database setup to figure out
what's wrong?
```

Claude can check whether the test database setup is running all migrations, whether the migration has a dependency issue, or whether the test fixtures reference the old table name.

**When tests pass locally but fail in CI:**

```
This test passes on my machine but fails in CI:

```
FAILED tests/test_report_generator.py::test_generate_monthly_report
AssertionError: Expected PDF to contain "January 2025" but got "December 2024"
```

The CI environment is Ubuntu 22.04, Python 3.11. My local machine is macOS,
Python 3.11. The test is in tests/test_report_generator.py and the code is
in services/report_generator.py. Could this be a timezone issue?
```

Claude reads the code and identifies whether the report generator uses local time (which differs between the developer's machine and the CI server) versus UTC, and suggests the fix.

## Testing Strategies for Large Codebases

As a codebase grows and you use Claude to generate more tests, keeping the test suite fast, maintainable, and meaningful requires deliberate strategy.

**Unit vs. integration test decisions:**

Use unit tests for:
- Business logic and calculations
- Data transformations and validation
- Pure functions and stateless services
- Anything with complex branching logic

Use integration tests for:
- API endpoint behavior (request in, response out)
- Database operations (queries, transactions, migrations)
- Service-to-service interactions
- Workflows that span multiple components

When asking Claude to write tests, specify which kind you want:

```
Write unit tests for the PricingService.calculate_total method. Mock all
external dependencies (database, payment gateway, inventory service). I want
to test the calculation logic in isolation.
```

vs.

```
Write integration tests for the checkout API endpoint POST /api/checkout.
Use the test database and real service classes. I want to verify the full
flow from request to database state.
```

**Keeping AI-generated tests maintainable:**

Claude-generated tests can become verbose and repetitive. After Claude writes a test file, review it for:

- **Duplicate setup logic** that should be extracted into fixtures or helper functions. Ask Claude to consolidate: "There's a lot of repeated setup in these tests. Extract common setup into pytest fixtures in the conftest.py for this directory."

- **Overly specific assertions** that test implementation details rather than behavior. If a test asserts the exact SQL query string, it will break on any refactor. Ask Claude to use behavioral assertions instead: "Change the database assertions to check the final state of the record, not the specific query used."

- **Missing edge cases** in the generated tests. Claude tends to test the cases you specify and obvious error cases but may miss domain-specific edge cases. Review and add: "Also add a test for the case where a subscription renews on a leap day. What should happen on Feb 29?"

**Testing patterns for large codebases:**

For services with many dependencies, build a test helper module:

```
Create a tests/helpers/service_factory.py module that provides factory functions
for creating test instances of our services with all dependencies mocked by
default. I want to be able to write:

    service = create_test_order_service()

and get an OrderService with mocked database, mocked payment gateway, and mocked
inventory service. But I should also be able to override specific mocks:

    service = create_test_order_service(inventory=real_inventory_service)

Base this on the existing service initialization in services/__init__.py.
```

Once this helper exists, tell Claude about it in future prompts:

```
Write tests for the new refund method on OrderService. Use the
create_test_order_service factory from tests/helpers/service_factory.py
for setup.
```

This keeps Claude-generated tests consistent and reduces the boilerplate in each test file.

**Parameterized tests for data-driven validation:**

When a function needs to handle many input variations, parameterized tests keep the test file readable:

```
The validate_address function needs to handle addresses from US, CA, UK, DE, JP,
and AU. Each country has different required fields and format rules. Write
parameterized tests that cover: a valid address for each country, missing required
fields for each country, and invalid format (e.g., wrong postal code format) for
each country. Use @pytest.mark.parametrize with clear test IDs like
"us-valid", "us-missing-state", "uk-invalid-postcode".
```

Claude produces a clean, tabular test structure that is easy to extend when you add support for new countries.

## See Also

- [Implementation Patterns](05-implementation-patterns.md) -- Incremental implementation patterns that pair with TDD
- [Code Review and Quality](07-code-review-and-quality.md) -- Ensuring test quality during code review
- [Prompting Strategies](03-prompting-strategies.md) -- Prompt techniques that improve test generation
