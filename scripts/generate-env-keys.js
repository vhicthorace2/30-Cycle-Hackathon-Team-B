const { generateKeyPairSync } = require('crypto');
const fs = require('fs');
const path = require('path');

const out = path.join(__dirname, '..', '.env');

function gen(namedCurve){
  return generateKeyPairSync('ec', {
    namedCurve,
    publicKeyEncoding: { type: 'spki', format: 'pem' },
    privateKeyEncoding: { type: 'pkcs8', format: 'pem' },
  });
}

const es256 = gen('P-256');
const es512 = gen('P-521');

function esc(pem) {
  return pem.replace(/\r?\n/g, '\\n').trim();
}

const env = [
  'NODE_ENV=development',
  'APP_PORT=3000',
  'PORT=3000',
  'HOST=localhost',
  'POSTGRES_DB=ciap',
  'POSTGRES_USER=ciap',
  'POSTGRES_PASSWORD=ciap_dev_password',
  'POSTGRES_PORT=5432',
  'DATABASE_URL=postgresql://ciap:ciap_dev_password@localhost:5432/ciap?sslmode=disable',
  'REDIS_PASSWORD=redis_dev_password',
  'REDIS_PORT=6379',
  'REDIS_URL=redis://:redis_dev_password@localhost:6379',
  'BULLMQ_PREFIX=bull',
  'CORS_ORIGIN=http://localhost:3000',
  'CORS_CREDENTIALS=true',
  'API_VERSION=v1',
  'API_PREFIX=/api',
  'JWT_ACCESS_EXPIRES_IN=15m',
  'JWT_REFRESH_EXPIRES_IN=7d',
  `JWT_ACCESS_PRIVATE_KEY=${esc(es256.privateKey)}`,
  `JWT_ACCESS_PUBLIC_KEY=${esc(es256.publicKey)}`,
  `JWT_REFRESH_PRIVATE_KEY=${esc(es512.privateKey)}`,
  `JWT_REFRESH_PUBLIC_KEY=${esc(es512.publicKey)}`,
  'ADMIN_SIGNUP_KEY=replace-with-strong-admin-signup-key',
  'LOG_ENABLED=true',
  'LOG_BACKEND=pino',
  'LOG_HTTP_ENABLED=true',
  'LOG_HTTP_MODE=errors',
  'LOG_LEVEL=debug',
  'LOG_FORMAT=pretty',
  'LOG_TO_FILE=false',
  'LOG_FILE_PATH=./logs/ciap.log',
  'LOG_FILE_LEVEL=info',
  'LOG_FILE_SIZE=50m',
  'LOG_FILE_FREQUENCY=daily',
].join('\n') + '\n';

fs.writeFileSync(out, env);
console.log('WROTE .env at', out);
