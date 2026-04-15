// Step 6: App entry point — wiring everything together

import express from 'express';
import { bookmarkRouter } from './routes';
import { errorHandler } from './errors';

const app = express();

app.use(express.json());
app.use('/bookmarks', bookmarkRouter);
app.use(errorHandler);

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});

export { app };
