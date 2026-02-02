# Clean Code TypeScript

Clean Code principles adapted for TypeScript. Focus on readability, maintainability, and simplicity.

> "Any fool can write code that a computer can understand. Good programmers write code that humans can understand." — Martin Fowler

---

## Meaningful Names

### Use Intention-Revealing Names

```typescript
// ❌ Bad
const d = 86400000;
const list = users.filter(u => u.a);

// ✅ Good
const MILLISECONDS_PER_DAY = 86400000;
const activeUsers = users.filter(user => user.isActive);
```

### Use Pronounceable Names

```typescript
// ❌ Bad
type DtaRcrd = { createdYmdHms: Date; modYmdHms: Date };

// ✅ Good
type DataRecord = { createdAt: Date; modifiedAt: Date };
```

### Use Searchable Names

```typescript
// ❌ Bad: magic numbers
setTimeout(doSomething, 604800000);

// ✅ Good: named constant
const WEEK_IN_MS = 7 * 24 * 60 * 60 * 1000;
setTimeout(doSomething, WEEK_IN_MS);
```

### Boolean Naming Prefixes

```typescript
// Use: is, has, should, can, will, did
const isActive = true;
const hasPermission = user.role === 'admin';
const shouldRefresh = lastUpdate < threshold;
const canEdit = isOwner || hasPermission;
const willExpire = expiresAt < Date.now();
const didComplete = status === 'completed';
```

### Avoid Mental Mapping

```typescript
// ❌ Bad: requires mental translation
users.forEach(u => {
  const n = u.name;
  const e = u.email;
  sendEmail(e, `Hello ${n}`);
});

// ✅ Good: clear intent
users.forEach(user => {
  const { name, email } = user;
  sendEmail(email, `Hello ${name}`);
});
```

---

## Functions

### Small and Focused

Functions should do one thing and do it well.

```typescript
// ❌ Bad: does multiple things
function processUser(user: User) {
  // Validate
  if (!user.email.includes('@')) throw new Error('Invalid email');
  if (user.name.length < 2) throw new Error('Name too short');

  // Transform
  user.email = user.email.toLowerCase();
  user.name = user.name.trim();

  // Save
  database.save(user);

  // Notify
  sendWelcomeEmail(user);
  analytics.track('user_created', user);
}

// ✅ Good: single responsibility
function validateUser(user: User): void {
  if (!user.email.includes('@')) throw new Error('Invalid email');
  if (user.name.length < 2) throw new Error('Name too short');
}

function normalizeUser(user: User): User {
  return {
    ...user,
    email: user.email.toLowerCase(),
    name: user.name.trim(),
  };
}

function createUser(input: CreateUserInput): Promise<User> {
  validateUser(input);
  const user = normalizeUser(input);
  return database.save(user);
}

function notifyUserCreated(user: User): void {
  sendWelcomeEmail(user);
  analytics.track('user_created', user);
}
```

### Few Arguments

```typescript
// ❌ Bad: too many arguments
function createUser(
  name: string,
  email: string,
  age: number,
  role: string,
  department: string,
  manager: string,
  startDate: Date
) { ... }

// ✅ Good: options object
type CreateUserInput = {
  name: string;
  email: string;
  age: number;
  role: string;
  department: string;
  manager: string;
  startDate: Date;
};

function createUser(input: CreateUserInput) { ... }

// ✅ Also Good: builder pattern for complex objects
const user = UserBuilder.create()
  .withName('John')
  .withEmail('john@example.com')
  .withRole('admin')
  .build();
```

### Use Descriptive Names

```typescript
// ❌ Bad
function calc(a: number, b: number): number { ... }
function process(data: unknown): void { ... }
function handle(event: Event): void { ... }

// ✅ Good
function calculateTotalWithTax(subtotal: number, taxRate: number): number { ... }
function validateAndSaveUser(userData: unknown): void { ... }
function handleFormSubmission(event: SubmitEvent): void { ... }
```

### Pure Functions

Functions should not modify external state.

```typescript
// ❌ Bad: modifies external state
let total = 0;
function addToTotal(amount: number): number {
  total += amount;
  return total;
}

// ✅ Good: pure function
function add(a: number, b: number): number {
  return a + b;
}

const total = items.reduce((sum, item) => add(sum, item.price), 0);
```

### Command-Query Separation

Functions should either do something (command) or return something (query), not both.

```typescript
// ❌ Bad: does both
function setAndReturnUser(name: string): User {
  currentUser.name = name;  // Command: changes state
  return currentUser;        // Query: returns data
}

// ✅ Good: separated
function setUserName(name: string): void {
  currentUser.name = name;
}

function getUser(): User {
  return currentUser;
}
```

---

## Objects and Data

### Prefer Immutability

```typescript
// ❌ Bad: mutable
const user = { name: 'John', age: 30 };
user.age = 31;  // Mutation

// ✅ Good: immutable
const user = { name: 'John', age: 30 } as const;
const updatedUser = { ...user, age: 31 };  // New object
```

### Use Readonly

```typescript
type User = {
  readonly id: string;
  readonly name: string;
  readonly email: string;
};

function processUsers(users: ReadonlyArray<User>): void {
  // Cannot modify array or its contents
}
```

### Law of Demeter

Only talk to immediate friends, not strangers.

```typescript
// ❌ Bad: train wreck
const city = user.getAddress().getCity().getName();

// ✅ Good: encapsulate the chain
const city = user.getCityName();

// ✅ Also Good: destructure at the boundary
const { city } = user.address;
```

### Prefer Composition Over Inheritance

```typescript
// ❌ Bad: deep inheritance
class Animal { }
class Mammal extends Animal { }
class Dog extends Mammal { }
class ServiceDog extends Dog { }

// ✅ Good: composition
type Animal = { name: string };
type CanBark = { bark: () => void };
type CanFetch = { fetch: () => void };
type CanAssist = { assist: () => void };

type Dog = Animal & CanBark & CanFetch;
type ServiceDog = Dog & CanAssist;

const createDog = (name: string): Dog => ({
  name,
  bark: () => console.log('Woof!'),
  fetch: () => console.log('Fetching...'),
});
```

---

## Error Handling

### Throw Early, Catch Late

```typescript
// Throw at the source
function divide(a: number, b: number): number {
  if (b === 0) {
    throw new Error('Division by zero');
  }
  return a / b;
}

// Catch at the appropriate level (usually boundaries)
async function handleRequest(req: Request): Promise<Response> {
  try {
    const result = await processRequest(req);
    return new Response(JSON.stringify(result));
  } catch (error) {
    logger.error(error);
    return new Response('Internal error', { status: 500 });
  }
}
```

### Use Custom Error Classes

```typescript
class AppError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode: number = 500
  ) {
    super(message);
    this.name = 'AppError';
  }
}

class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} not found: ${id}`, 'NOT_FOUND', 404);
    this.name = 'NotFoundError';
  }
}

class ValidationError extends AppError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR', 400);
    this.name = 'ValidationError';
  }
}
```

### Don't Return Null for Collections

```typescript
// ❌ Bad
function getUsers(): Array<User> | null {
  return users.length > 0 ? users : null;
}

// Caller must check
const users = getUsers();
if (users) {
  users.forEach(u => ...);
}

// ✅ Good
function getUsers(): Array<User> {
  return users;  // Empty array if none
}

// Caller can use directly
getUsers().forEach(u => ...);
```

### Provide Context in Errors

```typescript
// ❌ Bad: no context
throw new Error('Failed');

// ✅ Good: actionable context
throw new Error(
  `Failed to fetch user ${userId}: ${response.status} ${response.statusText}`
);
```

---

## Comments

### Code Should Be Self-Documenting

```typescript
// ❌ Bad: comment explains bad code
// Check if user is eligible for discount
if (u.a > 18 && u.m > 12 && u.t > 1000) { ... }

// ✅ Good: code explains itself
const isAdult = user.age > 18;
const isLoyalCustomer = user.membershipMonths > 12;
const isHighSpender = user.totalPurchases > 1000;

if (isAdult && isLoyalCustomer && isHighSpender) { ... }
```

### Explain Why, Not What

```typescript
// ❌ Bad: explains what (obvious from code)
// Increment counter by 1
counter += 1;

// ✅ Good: explains why (not obvious)
// Retry count starts at 1 because the initial request counts as first attempt
counter += 1;
```

### JSDoc for Public APIs

```typescript
/**
 * Calculates the total price including tax and discounts.
 *
 * @param items - Cart items to calculate
 * @param taxRate - Tax rate as decimal (e.g., 0.1 for 10%)
 * @param discountCode - Optional discount code to apply
 * @returns Total price in cents
 * @throws {ValidationError} If items array is empty
 *
 * @example
 * const total = calculateTotal(cartItems, 0.1, 'SAVE20');
 */
function calculateTotal(
  items: ReadonlyArray<CartItem>,
  taxRate: number,
  discountCode?: string
): number { ... }
```

### Delete Commented-Out Code

```typescript
// ❌ Bad: commented-out code
function processOrder(order: Order) {
  // const discount = calculateDiscount(order);
  // order.total -= discount;
  // logger.info('Applied discount:', discount);

  validateOrder(order);
  saveOrder(order);
}

// ✅ Good: remove it (use version control)
function processOrder(order: Order) {
  validateOrder(order);
  saveOrder(order);
}
```

---

## SOLID Principles

### Single Responsibility (S)

A class/module should have only one reason to change.

```typescript
// ❌ Bad: multiple responsibilities
class UserService {
  createUser(data: CreateUserInput) { ... }
  sendEmail(to: string, subject: string) { ... }
  generateReport(userId: string) { ... }
  validateInput(data: unknown) { ... }
}

// ✅ Good: single responsibility each
class UserRepository {
  create(data: CreateUserInput): Promise<User> { ... }
  findById(id: string): Promise<User | null> { ... }
}

class EmailService {
  send(to: string, subject: string, body: string): Promise<void> { ... }
}

class UserValidator {
  validate(data: unknown): CreateUserInput { ... }
}
```

### Open/Closed (O)

Open for extension, closed for modification.

```typescript
// ❌ Bad: must modify to add new payment type
function processPayment(type: string, amount: number) {
  if (type === 'credit') {
    // process credit
  } else if (type === 'debit') {
    // process debit
  } else if (type === 'crypto') {
    // added later - had to modify function
  }
}

// ✅ Good: extend without modification
type PaymentProcessor = {
  type: string;
  process: (amount: number) => Promise<void>;
};

const processors: Array<PaymentProcessor> = [
  { type: 'credit', process: processCreditPayment },
  { type: 'debit', process: processDebitPayment },
  // Add new processors without changing existing code
];

function processPayment(type: string, amount: number) {
  const processor = processors.find(p => p.type === type);
  if (!processor) throw new Error(`Unknown payment type: ${type}`);
  return processor.process(amount);
}
```

### Liskov Substitution (L)

Subtypes must be substitutable for their base types.

```typescript
// ❌ Bad: Square violates Rectangle contract
class Rectangle {
  constructor(public width: number, public height: number) {}

  setWidth(w: number) { this.width = w; }
  setHeight(h: number) { this.height = h; }
  area() { return this.width * this.height; }
}

class Square extends Rectangle {
  setWidth(w: number) { this.width = w; this.height = w; }  // Violates LSP
  setHeight(h: number) { this.width = h; this.height = h; }
}

// ✅ Good: separate types
type Shape = { area: () => number };
type Rectangle = Shape & { width: number; height: number };
type Square = Shape & { side: number };

const createRectangle = (width: number, height: number): Rectangle => ({
  width,
  height,
  area: () => width * height,
});

const createSquare = (side: number): Square => ({
  side,
  area: () => side * side,
});
```

### Interface Segregation (I)

Many specific interfaces are better than one general interface.

```typescript
// ❌ Bad: fat interface
type Worker = {
  work: () => void;
  eat: () => void;
  sleep: () => void;
  attendMeeting: () => void;
  writeReport: () => void;
};

// ✅ Good: segregated interfaces
type Workable = { work: () => void };
type Eatable = { eat: () => void };
type Sleepable = { sleep: () => void };
type Meetable = { attendMeeting: () => void };
type Reportable = { writeReport: () => void };

type Developer = Workable & Eatable & Meetable;
type Manager = Workable & Eatable & Meetable & Reportable;
type Robot = Workable;  // Doesn't eat or sleep
```

### Dependency Inversion (D)

Depend on abstractions, not concretions.

```typescript
// ❌ Bad: depends on concrete implementation
class UserService {
  private database = new PostgresDatabase();

  async getUser(id: string) {
    return this.database.query(`SELECT * FROM users WHERE id = $1`, [id]);
  }
}

// ✅ Good: depends on abstraction
type Database = {
  query: <T>(sql: string, params: Array<unknown>) => Promise<T>;
};

const createUserService = (database: Database) => ({
  getUser: (id: string) =>
    database.query<User>(`SELECT * FROM users WHERE id = $1`, [id]),
});

// Inject the dependency
const userService = createUserService(postgresDatabase);
// Or for testing
const testService = createUserService(mockDatabase);
```

---

## Testing Guidelines

### F.I.R.S.T. Principles

| Letter | Principle | Meaning |
|--------|-----------|---------|
| F | Fast | Tests run quickly |
| I | Independent | No test depends on another |
| R | Repeatable | Same result every run |
| S | Self-validating | Pass or fail, no manual check |
| T | Timely | Written with or before code |

### Arrange-Act-Assert

```typescript
it('should apply discount to order total', () => {
  // Arrange
  const order = createOrder({ items: [{ price: 100 }] });
  const discountCode = 'SAVE20';

  // Act
  const total = calculateTotal(order, discountCode);

  // Assert
  expect(total).toBe(80);
});
```

### Test Behavior, Not Implementation

```typescript
// ❌ Bad: tests implementation
it('should call database.save with correct params', () => {
  const spy = vi.spyOn(database, 'save');
  createUser({ name: 'John' });
  expect(spy).toHaveBeenCalledWith({ name: 'John', createdAt: expect.any(Date) });
});

// ✅ Good: tests behavior
it('should create a user with the given name', async () => {
  const user = await createUser({ name: 'John' });
  expect(user.name).toBe('John');
  expect(user.id).toBeDefined();
});
```

---

*Companion to: style-guide.md, type-patterns.md*
*Last updated: 2025-12-31*
