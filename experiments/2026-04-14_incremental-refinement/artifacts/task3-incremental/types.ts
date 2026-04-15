// Step 1: Types for the middleware stack

export interface RateLimitConfig {
  windowMs: number;
  maxRequests: number;
  keyGenerator?: (ip: string) => string;
}

export interface RateLimitRecord {
  count: number;
  resetTime: number;
}

export interface RateLimitInfo {
  limit: number;
  remaining: number;
  retryAfterSeconds?: number;
}

export interface AuthConfig {
  apiKeys: Set<string>;
  headerName: string;
  excludePaths?: string[];
}

export interface RequestLogEntry {
  id: string;
  timestamp: string;
  method: string;
  path: string;
  statusCode: number;
  durationMs: number;
  ip: string;
  userAgent: string;
  contentLength?: number;
}

export interface MiddlewareStackConfig {
  rateLimit: RateLimitConfig;
  auth: AuthConfig;
  logging: {
    enabled: boolean;
    maxEntries: number;
  };
}
