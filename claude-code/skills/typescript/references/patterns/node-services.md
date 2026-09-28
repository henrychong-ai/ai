# Node Services — Fastify 5 + Temporal Workers

A pattern for backend services that are not dashboard-backed internal tools: a **Fastify 5** HTTP API that hands long-running or retry-heavy work to a **Temporal** workflow, with configuration validated by **Zod** at boot. Data access follows `tech-stack/orm.md` (Prisma 7 for these services). Temporal operations (namespaces, inspection, troubleshooting): Temporal's documentation.

Internal tools (Hono API + dashboard + MCP) follow `tech-stack/typescript-ironclad-stack.md` instead.

## Shape

```
src/
├── config.ts              # Zod-validated config, parsed once at boot
├── server.ts              # Entry: builds the app, starts HTTP and/or the worker by SERVICE_TYPE
├── app.ts                 # buildApp(): Fastify instance + plugins + routes (no listen) — testable
├── plugins/               # fastify-plugin wrappers (config, auth, db)
├── routes/                # One plugin per resource
├── services/              # Business logic; no Fastify types
└── temporal/
    ├── client.ts          # Temporal Client (used by routes/services)
    ├── worker.ts          # Worker: task queue, workflowsPath, activities
    ├── workflows/         # Deterministic workflow code — no I/O, no Node APIs
    └── activities/        # Side effects: HTTP calls, DB writes, notifications
```

One image can run in three modes selected by an environment variable (`SERVICE_TYPE=api|worker|combined`). Split API and worker into separate deployments once load or failure isolation matters.

## Configuration (Zod, fail fast)

```typescript
// src/config.ts
import { z } from 'zod';

const ConfigSchema = z.object({
  NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  PORT: z.coerce.number().int().positive().default(3000),
  SERVICE_TYPE: z.enum(['api', 'worker', 'combined']).default('combined'),
  DATABASE_URL: z.url(),
  TEMPORAL_ADDRESS: z.string().min(1),
  TEMPORAL_NAMESPACE: z.string().min(1),
  TEMPORAL_TASK_QUEUE: z.string().min(1),
});

export type Config = z.infer<typeof ConfigSchema>;

export function loadConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const parsed = ConfigSchema.safeParse(env);
  if (!parsed.success) {
    throw new Error(`Invalid configuration:\n${z.prettifyError(parsed.error)}`);
  }
  return parsed.data;
}
```

Secrets arrive as environment variables from the platform's secret store at deploy time. Never commit `.env` files.

## Fastify app

```typescript
// src/app.ts
import Fastify, { type FastifyInstance } from 'fastify';
import { z } from 'zod';
import type { Config } from './config.js';

const CreatePaymentBody = z.object({
  paymentId: z.string().min(1),
  amountMinor: z.number().int().positive(), // integer minor units, never floats for money
  currency: z.string().length(3),
});

type StartPaymentWorkflow = (input: z.infer<typeof CreatePaymentBody>) => Promise<string>;

export function buildApp(config: Config, startPaymentWorkflow: StartPaymentWorkflow): FastifyInstance {
  const app = Fastify({ logger: { level: config.NODE_ENV === 'test' ? 'silent' : 'info' } });

  app.get('/health', async () => ({ status: 'ok' }));

  app.post('/payments', async (request, reply) => {
    const body = CreatePaymentBody.safeParse(request.body);
    if (!body.success) {
      return reply.code(400).send({ error: 'VALIDATION_FAILED', issues: body.error.issues });
    }
    const workflowId = await startPaymentWorkflow(body.data);
    return reply.code(202).send({ workflowId });
  });

  return app;
}
```

- Keep `buildApp()` free of `listen()`, so tests call `app.inject()` with no open port.
- Validate with Zod at the route (as above) or register a Zod type provider; either way, one schema per request shape.
- Return `202 Accepted` with the workflow ID when the route only starts work.

## Temporal: starting work idempotently

```typescript
// src/temporal/client.ts
import { Client, Connection, WorkflowExecutionAlreadyStartedError } from '@temporalio/client';
import { WorkflowIdReusePolicy } from '@temporalio/common';
import type { Config } from '../config.js';

export async function createStarter(config: Config) {
  const connection = await Connection.connect({ address: config.TEMPORAL_ADDRESS });
  const client = new Client({ connection, namespace: config.TEMPORAL_NAMESPACE });

  return async function startPaymentWorkflow(input: { paymentId: string; amountMinor: number; currency: string }) {
    const workflowId = `payment-${input.paymentId}`; // deterministic: one workflow per business key
    try {
      await client.workflow.start('paymentWorkflow', {
        taskQueue: config.TEMPORAL_TASK_QUEUE,
        workflowId,
        workflowIdReusePolicy: WorkflowIdReusePolicy.REJECT_DUPLICATE,
        args: [input],
      });
    } catch (error) {
      // The deterministic ID + REJECT_DUPLICATE pair IS the idempotency guard:
      // a rejected duplicate is a success, not an error.
      if (!(error instanceof WorkflowExecutionAlreadyStartedError)) throw error;
    }
    return workflowId;
  };
}
```

Recognise SDK errors by class (`instanceof`), never by matching message text: message wording changes between SDK versions.

## Temporal: workflows and activities

```typescript
// src/temporal/workflows/payment.ts — deterministic: no I/O, no Date.now(), no Math.random()
import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from '../activities/index.js';

const { checkPaymentStatus } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30 seconds',
  retry: { maximumAttempts: 5, backoffCoefficient: 2 },
});

export async function paymentWorkflow(input: { paymentId: string }): Promise<'captured' | 'failed'> {
  for (let attempt = 0; attempt < 20; attempt++) {
    const status = await checkPaymentStatus(input.paymentId);
    if (status !== 'pending') return status;
    await sleep('30 seconds'); // durable timer
  }
  return 'failed';
}
```

```typescript
// src/temporal/worker.ts
import { fileURLToPath } from 'node:url';
import { NativeConnection, Worker } from '@temporalio/worker';
import type { Config } from '../config.js';
import * as activities from './activities/index.js';

export async function runWorker(config: Config): Promise<void> {
  const connection = await NativeConnection.connect({ address: config.TEMPORAL_ADDRESS });
  const worker = await Worker.create({
    connection,
    namespace: config.TEMPORAL_NAMESPACE,
    taskQueue: config.TEMPORAL_TASK_QUEUE,
    // The directory, not index.js: under tsx only index.ts exists. fileURLToPath, not .pathname (%20 for spaces).
    workflowsPath: fileURLToPath(new URL('./workflows', import.meta.url)),
    activities,
  });
  await worker.run();
}
```

- Relative imports carry `.js` because these services compile with `module`/`moduleResolution` `NodeNext` (`coding-standards/tooling.md`); tsx and Temporal's workflow bundler both resolve those `.js` imports to the `.ts` source in development.
- Workflow code runs in Temporal's deterministic sandbox and is bundled by the worker from `workflowsPath`: import only `@temporalio/workflow` and pure code there.
- Activities hold every side effect and must be idempotent (Temporal retries them).
- Test workflows with `@temporalio/testing` (`TestWorkflowEnvironment`), activities as plain functions.

## Build and run

- Develop with `tsx watch src/server.ts`; type-check with `tsc --noEmit`.
- Production: run the compiled output (`tsc` emit) or `tsx` directly; bundle with tsdown only if you need a single file. tsup is unmaintained upstream (`tech-stack/version-policy.md`).
- Graceful shutdown: on `SIGTERM`, stop accepting HTTP (`app.close()`) and let the worker drain (`worker.shutdown()`).

## Testing

- Routes: `buildApp(config, fakeStarter)` + `app.inject()`; assert status, body and that the fake starter received the parsed input.
- Services with a database: integration tests against a disposable database (Testcontainers or a CI service container), marked so the unit suite stays fast.
- Workflows: `TestWorkflowEnvironment.createTimeSkipping()`.

---

*Companion to: `tech-stack/orm.md`, `patterns/error-handling.md`.*
