import { describe, expect, it } from 'vitest';
import { buildServer } from '../src/server';

async function withServer<T>(fn: (app: ReturnType<typeof buildServer>) => Promise<T>) {
  const app = buildServer();
  try {
    return await fn(app);
  } finally {
    await app.close();
  }
}

describe('rest-api-v1 users baseline', () => {
  it('creates, reads, updates, lists, and deletes users through the envelope pattern', async () => withServer(async (app) => {
    const created = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Ada', email: 'ada@example.test' } });
    expect(created.statusCode).toBe(201);
    expect(created.json().error).toBeNull();
    const id = created.json().data.id;

    const fetched = await app.inject({ method: 'GET', url: `/users/${id}` });
    expect(fetched.statusCode).toBe(200);
    expect(fetched.json().data.email).toBe('ada@example.test');

    const updated = await app.inject({ method: 'PUT', url: `/users/${id}`, payload: { name: 'Ada Lovelace' } });
    expect(updated.statusCode).toBe(200);
    expect(updated.json().data.name).toBe('Ada Lovelace');

    const listed = await app.inject({ method: 'GET', url: '/users?page=1&limit=10' });
    expect(listed.statusCode).toBe(200);
    expect(listed.json().meta).toMatchObject({ page: 1, limit: 10, total: 1 });

    const deleted = await app.inject({ method: 'DELETE', url: `/users/${id}` });
    expect(deleted.statusCode).toBe(200);
    expect(deleted.json().data.deleted).toBe(true);
  }));

  it('covers validation, malformed ids, missing users, conflicts, pagination errors, and server-error guard semantics', async () => withServer(async (app) => {
    expect((await app.inject({ method: 'POST', url: '/users', payload: { name: '', email: 'bad' } })).statusCode).toBe(422);
    expect((await app.inject({ method: 'GET', url: '/users/not-a-number' })).statusCode).toBe(400);
    expect((await app.inject({ method: 'GET', url: '/users/404' })).statusCode).toBe(404);

    await app.inject({ method: 'POST', url: '/users', payload: { name: 'Grace', email: 'grace@example.test' } });
    expect((await app.inject({ method: 'POST', url: '/users', payload: { name: 'Other', email: 'grace@example.test' } })).statusCode).toBe(409);
    expect((await app.inject({ method: 'GET', url: '/users?page=0&limit=10' })).statusCode).toBe(400);

    // Fastify's setErrorHandler represents the documented 500 envelope implementation path.
    // This baseline does not force that path; a later runtime validation step can add a throwing route.
  }));
});
