import { test, expect } from 'vitest';
import { buildServer } from '../src/server';

test('forced 500 error envelope is correct', async () => {
  const app = buildServer();

  try {
    app.get('/__force_500', async () => {
    throw new Error('Forced Internal Server Error');
  });

  const response = await app.inject({
    method: 'GET',
    url: '/__force_500'
  });

  expect(response.statusCode).toBe(500);
  const payload = JSON.parse(response.payload);
  expect(payload.data).toBeNull();
  expect(payload.error).toBeDefined();
  expect(payload.error.code).toBe('INTERNAL_ERROR');
  expect(payload.error.message).toBeDefined();
  expect(payload.meta).toBeNull();
  } finally {
    await app.close();
  }
});
