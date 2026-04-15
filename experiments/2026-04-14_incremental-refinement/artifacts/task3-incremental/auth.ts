// Step 4: Auth middleware — API key checking

import { Request, Response, NextFunction } from 'express';
import { AuthConfig } from './types';

export function authMiddleware(config: AuthConfig) {
  const excludePaths = new Set(config.excludePaths ?? ['/health']);

  return (req: Request, res: Response, next: NextFunction): void => {
    // Skip auth for excluded paths
    if (excludePaths.has(req.path)) {
      next();
      return;
    }

    const headerValue = req.headers[config.headerName.toLowerCase()];
    const apiKey = Array.isArray(headerValue) ? headerValue[0] : headerValue;

    if (!apiKey) {
      res.status(401).json({
        error: 'Unauthorized',
        message: `Missing required header: ${config.headerName}`,
      });
      return;
    }

    if (!config.apiKeys.has(apiKey)) {
      res.status(403).json({
        error: 'Forbidden',
        message: 'Invalid API key',
      });
      return;
    }

    next();
  };
}
