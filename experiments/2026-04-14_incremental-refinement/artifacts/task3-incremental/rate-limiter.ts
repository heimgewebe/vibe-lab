// Step 3: Rate limiter core logic

import { Request, Response, NextFunction } from 'express';
import { RateLimitConfig, RateLimitRecord, RateLimitInfo } from './types';

export function rateLimitMiddleware(config: RateLimitConfig) {
  const store = new Map<string, RateLimitRecord>();

  // Periodic cleanup to prevent memory leaks
  const cleanupInterval = setInterval(() => {
    const now = Date.now();
    for (const [key, record] of store) {
      if (now > record.resetTime) {
        store.delete(key);
      }
    }
  }, config.windowMs);

  // Allow cleanup timer to not keep the process alive
  if (cleanupInterval.unref) {
    cleanupInterval.unref();
  }

  return (req: Request, res: Response, next: NextFunction): void => {
    const key = config.keyGenerator
      ? config.keyGenerator(req.ip || 'unknown')
      : req.ip || 'unknown';

    const now = Date.now();
    let record = store.get(key);

    // Reset if window has passed
    if (!record || now > record.resetTime) {
      record = { count: 0, resetTime: now + config.windowMs };
      store.set(key, record);
    }

    record.count++;

    const info: RateLimitInfo = {
      limit: config.maxRequests,
      remaining: Math.max(0, config.maxRequests - record.count),
    };

    // Set rate limit headers on every response
    res.setHeader('X-RateLimit-Limit', info.limit);
    res.setHeader('X-RateLimit-Remaining', info.remaining);
    res.setHeader('X-RateLimit-Reset', Math.ceil(record.resetTime / 1000));

    if (record.count > config.maxRequests) {
      info.retryAfterSeconds = Math.ceil((record.resetTime - now) / 1000);
      res.setHeader('Retry-After', info.retryAfterSeconds);
      res.status(429).json({
        error: 'Too Many Requests',
        message: `Rate limit exceeded. Try again in ${info.retryAfterSeconds} seconds.`,
        retryAfter: info.retryAfterSeconds,
      });
      return;
    }

    next();
  };
}
