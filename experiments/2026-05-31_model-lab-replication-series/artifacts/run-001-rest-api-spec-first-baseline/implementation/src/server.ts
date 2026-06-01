import Fastify from 'fastify';
import { Type } from '@sinclair/typebox';
import { TypeBoxTypeProvider } from '@fastify/type-provider-typebox';

const UserInput = Type.Object({
  name: Type.String({ minLength: 1 }),
  email: Type.String({ format: 'email' }),
});

const UserUpdate = Type.Partial(UserInput, { minProperties: 1 });

type User = {
  id: string;
  name: string;
  email: string;
  createdAt: string;
  updatedAt: string;
};

type UserInputBody = {
  name: string;
  email: string;
};

type UserUpdateBody = Partial<UserInputBody>;

function ok<T>(data: T, meta: Record<string, unknown> | null = null) {
  return { data, error: null, meta };
}

function fail(code: string, message: string, details: unknown = null) {
  return { data: null, error: { code, message, details }, meta: null };
}

function isValidId(id: string) {
  return /^\d+$/.test(id);
}

export function buildServer() {
  const users = new Map<string, User>();
  let nextId = 1;
  const findByEmail = (email: string, exceptId?: string) =>
    [...users.values()].find((user) => user.email === email && user.id !== exceptId);
  const app = Fastify({ logger: false }).withTypeProvider<TypeBoxTypeProvider>();

  app.setErrorHandler((error, _request, reply) => {
    if (error.validation) {
      reply.status(422).send(fail('VALIDATION_ERROR', 'Request validation failed.', error.validation));
      return;
    }
    reply.status(500).send(fail('INTERNAL_ERROR', 'Unexpected server error.'));
  });

  app.post<{ Body: UserInputBody }>('/users', { schema: { body: UserInput } }, async (request, reply) => {
    if (findByEmail(request.body.email)) {
      return reply.status(409).send(fail('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }
    const now = new Date().toISOString();
    const user: User = {
      id: String(nextId++),
      name: request.body.name,
      email: request.body.email,
      createdAt: now,
      updatedAt: now,
    };
    users.set(user.id, user);
    return reply.status(201).send(ok(user));
  });

  app.get<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    const { id } = request.params;
    if (!isValidId(id)) {
      return reply.status(400).send(fail('BAD_ID', 'User id must be numeric.'));
    }
    const user = users.get(id);
    if (!user) {
      return reply.status(404).send(fail('NOT_FOUND', 'User not found.'));
    }
    return reply.status(200).send(ok(user));
  });

  app.put<{ Params: { id: string }; Body: UserUpdateBody }>('/users/:id', { schema: { body: UserUpdate } }, async (request, reply) => {
    const { id } = request.params;
    if (!isValidId(id)) {
      return reply.status(400).send(fail('BAD_ID', 'User id must be numeric.'));
    }
    const existing = users.get(id);
    if (!existing) {
      return reply.status(404).send(fail('NOT_FOUND', 'User not found.'));
    }
    if (request.body.email && findByEmail(request.body.email, id)) {
      return reply.status(409).send(fail('EMAIL_CONFLICT', 'A user with this email already exists.'));
    }
    const updated: User = {
      ...existing,
      ...request.body,
      updatedAt: new Date().toISOString(),
    };
    users.set(id, updated);
    return reply.status(200).send(ok(updated));
  });

  app.delete<{ Params: { id: string } }>('/users/:id', async (request, reply) => {
    const { id } = request.params;
    if (!isValidId(id)) {
      return reply.status(400).send(fail('BAD_ID', 'User id must be numeric.'));
    }
    if (!users.has(id)) {
      return reply.status(404).send(fail('NOT_FOUND', 'User not found.'));
    }
    users.delete(id);
    return reply.status(200).send(ok({ deleted: true, id }));
  });

  app.get<{ Querystring: { page?: string; limit?: string } }>('/users', async (request, reply) => {
    const page = Number(request.query.page ?? '1');
    const limit = Number(request.query.limit ?? '20');
    if (!Number.isInteger(page) || page < 1 || !Number.isInteger(limit) || limit < 1 || limit > 100) {
      return reply.status(400).send(fail('BAD_PAGINATION', 'page and limit must be positive integers; limit must be <= 100.'));
    }
    const all = [...users.values()];
    const start = (page - 1) * limit;
    const data = all.slice(start, start + limit);
    return reply.status(200).send(ok(data, { page, limit, total: all.length }));
  });

  return app;
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const app = buildServer();
  app.listen({ port: Number(process.env.PORT ?? 3000), host: '0.0.0.0' });
}
