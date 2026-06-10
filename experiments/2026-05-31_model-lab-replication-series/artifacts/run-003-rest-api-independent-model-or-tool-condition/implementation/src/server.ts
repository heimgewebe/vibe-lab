import Fastify from 'fastify';
import { Type } from '@sinclair/typebox';
import { TypeBoxTypeProvider } from '@fastify/type-provider-typebox';

const NewUserSchema = Type.Object({
  name: Type.String({ minLength: 1 }),
  email: Type.String({ format: 'email' }),
});

const UserPatchSchema = Type.Partial(NewUserSchema, { minProperties: 1 });

type UserRecord = {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
};

type NewUserBody = {
  name: string;
  email: string;
};

type UserPatchBody = Partial<NewUserBody>;

type EnvelopeMeta = Record<string, unknown> | null;

function success<T>(data: T, meta: EnvelopeMeta = null) {
  return { data, error: null, meta };
}

function failure(code: string, message: string, details?: unknown) {
  const error = details === undefined ? { code, message } : { code, message, details };
  return { data: null, error, meta: null };
}

function numericId(id: string) {
  return /^[0-9]+$/.test(id);
}

function nowIso() {
  return new Date().toISOString();
}

export function buildServer() {
  const app = Fastify({ logger: false }).withTypeProvider<TypeBoxTypeProvider>();
  const users = new Map<string, UserRecord>();
  let sequence = 1;

  const emailOwner = (email: string, exceptId?: string) =>
    [...users.values()].find((user) => user.email === email && user.id !== exceptId);

  app.setErrorHandler((error, _request, reply) => {
    if (error.validation) {
      reply.status(422).send(failure('VALIDATION_ERROR', 'Request validation failed.', error.validation));
      return;
    }
    reply.status(500).send(failure('INTERNAL_ERROR', 'Unexpected server error.'));
  });

  app.post<{ Body: NewUserBody }>('/users', { schema: { body: NewUserSchema } }, async (request, reply) => {
    if (emailOwner(request.body.email)) {
      return reply.status(409).send(failure('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }

    const stamp = nowIso();
    const user: UserRecord = {
      id: String(sequence++),
      name: request.body.name,
      email: request.body.email,
      createdAt: stamp,
      updatedAt: stamp,
    };
    users.set(user.id, user);
    return reply.status(201).send(success(user));
  });

  app.get<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    if (!numericId(request.params.id)) {
      return reply.status(400).send(failure('BAD_ID', 'User id must be numeric.'));
    }
    const user = users.get(request.params.id);
    if (!user) {
      return reply.status(404).send(failure('NOT_FOUND', 'User not found.'));
    }
    return reply.status(200).send(success(user));
  });

  app.put<{ Params: { id: string }; Body: UserPatchBody }>('/users/:id', { schema: { body: UserPatchSchema } }, async (request, reply) => {
    if (!numericId(request.params.id)) {
      return reply.status(400).send(failure('BAD_ID', 'User id must be numeric.'));
    }
    const existing = users.get(request.params.id);
    if (!existing) {
      return reply.status(404).send(failure('NOT_FOUND', 'User not found.'));
    }
    if (request.body.email && emailOwner(request.body.email, request.params.id)) {
      return reply.status(409).send(failure('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }

    const updated: UserRecord = {
      ...existing,
      ...request.body,
      updatedAt: nowIso(),
    };
    users.set(updated.id, updated);
    return reply.status(200).send(success(updated));
  });

  app.delete<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    if (!numericId(request.params.id)) {
      return reply.status(400).send(failure('BAD_ID', 'User id must be numeric.'));
    }
    if (!users.has(request.params.id)) {
      return reply.status(404).send(failure('NOT_FOUND', 'User not found.'));
    }
    users.delete(request.params.id);
    return reply.status(200).send(success({ deleted: true, id: request.params.id }));
  });

  app.get<{ Querystring: { page?: string; limit?: string } }>('/users', async (request, reply) => {
    const page = Number(request.query.page ?? '1');
    const limit = Number(request.query.limit ?? '20');
    if (!Number.isInteger(page) || page < 1 || !Number.isInteger(limit) || limit < 1 || limit > 100) {
      return reply.status(400).send(failure('BAD_PAGINATION', 'page and limit must be positive integers; limit must be <= 100.'));
    }
    const allUsers = [...users.values()];
    const offset = (page - 1) * limit;
    return reply.status(200).send(success(allUsers.slice(offset, offset + limit), { page, limit, total: allUsers.length }));
  });

  return app;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const app = buildServer();
  app
    .listen({ port: Number(process.env.PORT ?? 3000), host: '0.0.0.0' })
    .catch((error) => {
      console.error(error);
      process.exit(1);
    });
}
