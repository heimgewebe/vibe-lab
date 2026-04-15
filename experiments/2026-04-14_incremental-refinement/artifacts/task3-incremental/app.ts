// Step 2: Express app skeleton and route structure

import express from 'express';
import { rateLimitMiddleware } from './rate-limiter';
import { authMiddleware } from './auth';
import { requestLoggerMiddleware, getRequestLogs } from './logger';
import { notFoundHandler, errorHandler } from './errors';
import { MiddlewareStackConfig } from './types';

export function createApp(config: MiddlewareStackConfig): express.Application {
  const app = express();
  app.use(express.json());

  // Middleware stack — order: logging first, then rate limit, then auth
  if (config.logging.enabled) {
    app.use(requestLoggerMiddleware(config.logging.maxEntries));
  }
  app.use(rateLimitMiddleware(config.rateLimit));
  app.use(authMiddleware(config.auth));

  // Routes
  app.get('/health', (_req, res) => {
    res.json({ status: 'ok', uptime: process.uptime() });
  });

  app.get('/api/data', (_req, res) => {
    res.json({ message: 'Protected resource', data: [1, 2, 3] });
  });

  app.get('/api/logs', (_req, res) => {
    res.json({ logs: getRequestLogs() });
  });

  // Error handling
  app.use(notFoundHandler);
  app.use(errorHandler);

  return app;
}
