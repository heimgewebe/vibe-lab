// Step 3 (continued): Request logger middleware

import { Request, Response, NextFunction } from 'express';
import { RequestLogEntry } from './types';

let logStore: RequestLogEntry[] = [];
let maxEntries = 1000;
let entryCounter = 0;

function generateLogId(): string {
  return `req-${++entryCounter}`;
}

export function requestLoggerMiddleware(maxLogEntries: number) {
  maxEntries = maxLogEntries;

  return (req: Request, res: Response, next: NextFunction): void => {
    const startTime = Date.now();
    const logId = generateLogId();

    // Attach log ID to request for tracing
    res.setHeader('X-Request-Id', logId);

    res.on('finish', () => {
      const entry: RequestLogEntry = {
        id: logId,
        timestamp: new Date().toISOString(),
        method: req.method,
        path: req.originalUrl || req.path,
        statusCode: res.statusCode,
        durationMs: Date.now() - startTime,
        ip: req.ip || 'unknown',
        userAgent: req.headers['user-agent'] || 'unknown',
        contentLength: res.getHeader('content-length')
          ? parseInt(res.getHeader('content-length') as string, 10)
          : undefined,
      };

      logStore.push(entry);

      // Trim oldest entries if over limit
      if (logStore.length > maxEntries) {
        logStore = logStore.slice(-maxEntries);
      }

      console.log(
        `[${entry.timestamp}] ${entry.id} ${entry.method} ${entry.path} → ${entry.statusCode} (${entry.durationMs}ms)`
      );
    });

    next();
  };
}

export function getRequestLogs(): RequestLogEntry[] {
  return [...logStore];
}
