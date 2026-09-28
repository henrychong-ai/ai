# NestJS — Core Patterns & Best Practices

**Scope:** core NestJS only — the framework concepts and idioms that apply to any Nest backend. NestJS is **not** part of the ironclad stack (Hono + `@hono/zod-openapi`); it is covered here for existing or inherited NestJS codebases. Conventions specific to one codebase belong in that repository's `AGENTS.md`, not here. For depth beyond this reference, use the official NestJS documentation (docs.nestjs.com).

> **Classes are correct here:** the style guide's functional-first preference does not apply to framework-required classes. NestJS controllers, providers, modules, guards, interceptors, pipes and filters are **classes with decorators** by design — that's idiomatic and required (DI resolves classes). Use classes for these; keep pure functions for stateless helpers.

## Mental model
NestJS = **modules** that wire up **providers** (injectable classes) via **dependency injection**, with **decorators** declaring roles. A request flows through a fixed middleware/guard/interceptor/pipe/handler/filter pipeline. Favour many small single-responsibility providers over large ones.

## Modules
- `@Module({ imports, controllers, providers, exports })` groups a feature. Export only what other modules need.
- **Feature modules** per domain; **shared modules** for reusable providers (export them); **dynamic modules** (`forRoot`/`forFeature`) for configurable infra (e.g. TypeORM, config).
- Mark a module `@Global()` only for truly cross-cutting providers (config, logging) — overuse hides the dependency graph.
- One module per directory; barrel `index.ts` for clean imports.

## Providers & Dependency Injection
- `@Injectable()` + **constructor injection** is the default: `constructor(private readonly users: UserService) {}`.
- **Custom providers** (illustrative): `useClass` (swap implementation), `useValue` (constants/mocks), `useFactory` (computed, can inject deps), `useExisting` (alias). Inject non-class tokens with `@Inject(TOKEN)`.
- **Injection scopes:** prefer `DEFAULT` (singleton) — fastest. Use `REQUEST` scope only when you genuinely need per-request state; it bubbles up the whole dependency chain and costs performance. Avoid `TRANSIENT` unless required.
- **Avoid circular dependencies.** `forwardRef()` exists to break them but is a smell — restructure (extract a shared provider) instead.

## Request lifecycle (order matters)
A request passes through these stages **in this order** — know it to place cross-cutting logic correctly:

```
Middleware → Guards → Interceptors (pre) → Pipes → Route handler
           → Interceptors (post/response) → Exception filters (on throw)
```

- **Middleware** — earliest, framework-level (raw req/res), e.g. logging/cors.
- **Guards** — authZ/authN decision (return boolean / throw). authentication and route protection.
- **Interceptors (pre)** — wrap the handler (timing, context).
- **Pipes** — validate/transform handler inputs (DTO validation).
- **Handler** — controller method (thin — delegates to a service).
- **Interceptors (post)** — transform/shape the response.
- **Exception filters** — catch thrown errors and map to responses.

## Controllers, DTOs & validation
- Controllers are **thin**: parse the request, call a service, return the result. No business logic.
- Define request shapes as **DTO classes** with `class-validator` decorators; enable a global `ValidationPipe({ whitelist: true, transform: true })` so unknown props are stripped and payloads are typed.
- Param decorators read from the request: `@Body()`, `@Param()`, `@Query()`, plus custom ones (below).

## Guards
- Implement `CanActivate.canActivate(ctx)` → boolean / throw. Use for authentication and authorization.
- Integrate authentication via `@nestjs/passport`: a Passport **strategy** (`PassportStrategy`) validates the credential and returns the principal; `AuthGuard('strategy')` enforces it. Apply with `@UseGuards()` (method/controller) or as a global guard.

## Interceptors
- Implement `NestInterceptor.intercept(ctx, next)` and operate on the RxJS stream from `next.handle()`. Use for cross-cutting concerns (illustrative): logging, response envelope/transformation, caching, timeouts. Keep authorization **decisions** in guards, not interceptors.

## Pipes
- Implement `PipeTransform.transform(value, metadata)` for input validation/transformation. `ValidationPipe` (DTO validation) and `ParseUUIDPipe`/`ParseIntPipe` are built in. Prefer declarative DTO validation over manual checks.

## Exception filters
- Throw `HttpException` subclasses (`NotFoundException`, `ForbiddenException`, …) from services; Nest maps them to responses.
- A custom `@Catch()` `ExceptionFilter` centralises error→response shaping. Never swallow exceptions silently.

## Custom param decorators
- `createParamDecorator((data, ctx) => …)` extracts request-derived values into handler params — e.g. a `@CurrentUser()` decorator reading the principal a guard attached to the request. Keep them thin; they read, they don't authorize.

## Configuration
- Use `@nestjs/config` + `ConfigService` (validate env at boot with a schema). Inject `ConfigService` rather than reading `process.env` scattered through the code.

## Persistence, jobs, GraphQL (brief)
- **TypeORM:** `@nestjs/typeorm` — `forRoot` for the connection, `forFeature([Entity])` per module, inject repositories with `@InjectRepository`.
- **Background jobs:** `@nestjs/bullmq` (Redis-backed) — `@Processor`/`@Process` for workers; keep job handlers idempotent.
- **GraphQL:** `@nestjs/graphql` code-first (resolvers + decorated types) is the common Nest approach; `@Resolver`, `@Query`, `@Mutation`, field resolvers.

## Lifecycle hooks
- Implement as needed (illustrative): `OnModuleInit`, `OnApplicationBootstrap` (startup wiring), `OnModuleDestroy`, `OnApplicationShutdown` (graceful cleanup; enable shutdown hooks for clean container exits).

## Testing
- `@nestjs/testing` `Test.createTestingModule({...}).compile()` builds an isolated DI container; override providers with mocks via `.overrideProvider(X).useValue(mock)`.
- Unit-test services with mocked dependencies; e2e-test the HTTP surface with `supertest` against a booted app. Test behaviour, not wiring.

## Best practices
- **Thin controllers, logic in services**; one responsibility per provider.
- **Module boundaries**: export deliberately; don't reach into another module's internals.
- **Named exports**, barrel `index.ts` per module.
- **DTO validation at the edge** (global `ValidationPipe`), domain rules in services.
- **Config via `ConfigService`**, validated at boot.
- **Singleton (DEFAULT) scope** unless per-request state is genuinely needed.
- Enable shutdown hooks for graceful container lifecycle.

## Anti-patterns (avoid)
- Business logic in controllers, guards, or interceptors (belongs in services).
- Overusing `REQUEST` scope (performance) or `forwardRef()` (restructure instead).
- "God" modules/services; scattered `process.env` reads; swallowed exceptions.
- Reaching across module boundaries instead of importing/exporting providers.

## Going deeper
This is the core surface. For specifics (microservices, websockets/gateways, CQRS, advanced DI, caching, OpenAPI/Swagger), consult the official NestJS documentation (docs.nestjs.com) rather than guessing.
