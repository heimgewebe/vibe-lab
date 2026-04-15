// Step 6: Entry point — wiring the app with configuration

import { createApp } from './app';
import { MiddlewareStackConfig } from './types';

const config: MiddlewareStackConfig = {
  rateLimit: {
    windowMs: 60 * 1000, // 1 minute
    maxRequests: 100,
  },
  auth: {
    apiKeys: new Set(['test-key-1', 'test-key-2']),
    headerName: 'X-API-Key',
    excludePaths: ['/health'],
  },
  logging: {
    enabled: true,
    maxEntries: 1000,
  },
};

const app = createApp(config);
const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

export { app, config };
