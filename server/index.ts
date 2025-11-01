import express from 'express';
import cookieParser from 'cookie-parser';
import dotenv from 'dotenv';
import path from 'path';
import https from 'https';
import { readFileSync } from 'fs';

dotenv.config({ quiet: true });

const app = express();
const PORT = process.env['PORT'] || 3001;

app.use(express.static(path.resolve('dist/')));
app.use(cookieParser());
app.use(express.json());


app.get('/api/test', (req, res) => {
  const timestamp = new Date();
  res.status(200).send({ message: 'test works!', timestamp });
});

// Any GET request that doesn't match an API route or static file should serve the React app's index.html
app.get('/{*path}', (req, res) => {
  res.status(200).sendFile(path.resolve('dist/index.html'));
});

const startServer = () => {
  const key = readFileSync('server/server.key');
  const cert = readFileSync('server/server.cert');
  if (key && cert) {
    https.createServer({ key, cert }, app).listen(PORT, () => {
      console.log(`Secure BFF listening on port ${PORT}`);
    });
  } else {
    app.listen(3001, () => console.log(`BFF listening on port ${PORT}`));
  }
}


startServer();