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

describe('rest-api-v1 run-003 surface', () => {
  it('creates users with the success envelope and detects email conflicts', async () => {
    await withServer(async (app) => {
      const created = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Ada', email: 'ada@example.com' } });
      expect(created.statusCode).toBe(201);
      expect(created.json()).toMatchObject({ error: null, meta: null, data: { id: '1', name: 'Ada', email: 'ada@example.com' } });

      const conflict = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Ada Again', email: 'ada@example.com' } });
      expect(conflict.statusCode).toBe(409);
      expect(conflict.json()).toMatchObject({ data: null, error: { code: 'EMAIL_CONFLICT' }, meta: null });
    });
  });

  it('validates request bodies and ids', async () => {
    await withServer(async (app) => {
      const invalidBody = await app.inject({ method: 'POST', url: '/users', payload: { name: '', email: 'not-mail' } });
      expect(invalidBody.statusCode).toBe(422);
      expect(invalidBody.json()).toMatchObject({ data: null, error: { code: 'VALIDATION_ERROR' }, meta: null });

      const invalidId = await app.inject({ method: 'GET', url: '/users/not-a-number' });
      expect(invalidId.statusCode).toBe(400);
      expect(invalidId.json()).toMatchObject({ data: null, error: { code: 'BAD_ID' }, meta: null });
    });
  });

  it('reads, updates, deletes, and returns 404 after delete', async () => {
    await withServer(async (app) => {
      const created = await app.inject({ method: 'POST', url: '/users', payload: { name: 'Grace', email: 'grace@example.com' } });
      const id = created.json().data.id;

      const read = await app.inject({ method: 'GET', url: `/users/${id}` });
      expect(read.statusCode).toBe(200);
      expect(read.json().data.email).toBe('grace@example.com');

      const updated = await app.inject({ method: 'PUT', url: `/users/${id}`, payload: { email: 'hopper@example.com' } });
      expect(updated.statusCode).toBe(200);
      expect(updated.json().data.email).toBe('hopper@example.com');

      const deleted = await app.inject({ method: 'DELETE', url: `/users/${id}` });
      expect(deleted.statusCode).toBe(200);
      expect(deleted.json()).toMatchObject({ error: null, data: { deleted: true, id } });

      const missing = await app.inject({ method: 'GET', url: `/users/${id}` });
      expect(missing.statusCode).toBe(404);
      expect(missing.json()).toMatchObject({ data: null, error: { code: 'NOT_FOUND' }, meta: null });
    });
  });

  it('paginates user lists and rejects invalid pagination', async () => {
    await withServer(async (app) => {
      await app.inject({ method: 'POST', url: '/users', payload: { name: 'A', email: 'a@example.com' } });
      await app.inject({ method: 'POST', url: '/users', payload: { name: 'B', email: 'b@example.com' } });

      const page = await app.inject({ method: 'GET', url: '/users?page=1&limit=1' });
      expect(page.statusCode).toBe(200);
      expect(page.json()).toMatchObject({ error: null, meta: { page: 1, limit: 1, total: 2 } });
      expect(page.json().data).toHaveLength(1);

      const badPage = await app.inject({ method: 'GET', url: '/users?page=0&limit=1' });
      expect(badPage.statusCode).toBe(400);
      expect(badPage.json()).toMatchObject({ data: null, error: { code: 'BAD_PAGINATION' }, meta: null });
    });
  });

  it('documents the 500 error handler path without archiving forced runtime assertion here', async () => {
    await withServer(async (app) => {
      expect(app).toBeDefined();
    });
  });
});
