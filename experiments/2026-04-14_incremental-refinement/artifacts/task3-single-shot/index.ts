// Task 3 — Single-Shot: Middleware Stack (Rate-Limiting, Auth, Logging)
// Generated as a single, comprehensive response to one prompt

import express, { Request, Response, NextFunction } from 'express';

// ---- Types ----
interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
}

interface AuthConfig {
  apiKeys: Set<string>;
  headerName: string;
}

interface RequestLog {
  timestamp: string;
  method: string;
  path: string;
  statusCode: number;
  duration: number;
  ip: string;
  userAgent: string;
}

// ---- Rate Limiter ----
function createRateLimiter(config: RateLimitConfig) {
  const requests: Map<string, { count: number; resetTime: number }> = new Map();

  return (req: Request, res: Response, next: NextFunction): void => {
    const key = req.ip || 'unknown';
    const now = Date.now();
    const record = requests.get(key);

    if (!record || now > record.resetTime) {
      requests.set(key, { count: 1, resetTime: now + config.windowMs });
      res.setHeader('X-RateLimit-Limit', config.maxRequests);
      res.setHeader('X-RateLimit-Remaining', config.maxRequests - 1);
      next();
      return;
    }

    if (record.count >= config.maxRequests) {
      res.setHeader('X-RateLimit-Limit', config.maxRequests);
      res.setHeader('X-RateLimit-Remaining', 0);
      res.setHeader('Retry-After', Math.ceil((record.resetTime - now) / 1000));
      res.status(429).json({ error: 'Too Many Requests', retryAfter: Math.ceil((record.resetTime - now) / 1000) });
      return;
    }

    record.count++;
    res.setHeader('X-RateLimit-Limit', config.maxRequests);
    res.setHeader('X-RateLimit-Remaining', config.maxRequests - record.count);
    next();
  };
}

// ---- Auth Middleware ----
function createAuthMiddleware(config: AuthConfig) {
  return (req: Request, res: Response, next: NextFunction): void => {
    // Skip auth for health endpoint
    if (req.path === '/health') {
      next();
      return;
    }

    const apiKey = req.headers[config.headerName.toLowerCase()] as string | undefined;

    if (!apiKey) {
      res.status(401).json({ error: 'Unauthorized', message: 'API key is required' });
      return;
    }

    if (!config.apiKeys.has(apiKey)) {
      res.status(403).json({ error: 'Forbidden', message: 'Invalid API key' });
      return;
    }

    next();
  };
}

// ---- Request Logger ----
function createRequestLogger() {
  const logs: RequestLog[] = [];

  const middleware = (req: Request, res: Response, next: NextFunction): void => {
    const start = Date.now();

    res.on('finish', () => {
      const log: RequestLog = {
        timestamp: new Date().toISOString(),
        method: req.method,
        path: req.path,
        statusCode: res.statusCode,
        duration: Date.now() - start,
        ip: req.ip || 'unknown',
        userAgent: req.headers['user-agent'] || 'unknown',
      };
      logs.push(log);
      console.log(`[${log.timestamp}] ${log.method} ${log.path} ${log.statusCode} ${log.duration}ms`);
    });

    next();
  };

  return { middleware, getLogs: () => [...logs] };
}

// ---- App Setup ----
const app = express();
app.use(express.json());

const rateLimiter = createRateLimiter({ windowMs: 60 * 1000, maxRequests: 100 });
const authMiddleware = createAuthMiddleware({
  apiKeys: new Set(['test-key-1', 'test-key-2']),
  headerName: 'X-API-Key',
});
const { middleware: requestLogger, getLogs } = createRequestLogger();

// Apply middleware stack (order matters!)
app.use(requestLogger);
app.use(rateLimiter);
app.use(authMiddleware);

// ---- Sample Routes ----
app.get('/health', (_req: Request, res: Response) => {
  res.json({ status: 'ok' });
});

app.get('/api/data', (_req: Request, res: Response) => {
  res.json({ message: 'Protected endpoint', data: [1, 2, 3] });
});

app.get('/api/logs', (_req: Request, res: Response) => {
  res.json({ logs: getLogs() });
});

// 404 handler
app.use((_req: Request, res: Response) => {
  res.status(404).json({ error: 'Not Found' });
});

// Error handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal Server Error' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

export { app, createRateLimiter, createAuthMiddleware, createRequestLogger, RateLimitConfig, AuthConfig, RequestLog };
