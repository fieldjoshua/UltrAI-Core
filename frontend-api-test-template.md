# Frontend API Contract Test Template (Jest + supertest)

Install dependencies:

```
npm install --save-dev jest supertest
```

Example test file (`api.e2e.test.js`):

```js
const request = require('supertest');
const API_URL = 'http://localhost:8000';

describe('Ultra API E2E', () => {
  let jwtToken;

  it('should login and get JWT', async () => {
    const res = await request(API_URL)
      .post('/api/auth/login')
      .send({ username: 'user@example.com', password: 'yourpassword' });
    expect(res.statusCode).toBe(200);
    expect(res.body.access_token).toBeDefined();
    jwtToken = res.body.access_token;
  });

  it('should get user balance (JWT required)', async () => {
    const res = await request(API_URL)
      .get('/api/user/balance')
      .set('Authorization', `Bearer ${jwtToken}`);
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('balance');
  });

  it('should call orchestrator/analyze (JWT required)', async () => {
    const res = await request(API_URL)
      .post('/api/orchestrator/analyze')
      .set('Authorization', `Bearer ${jwtToken}`)
      .send({ input: 'Test input' });
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('result');
  });
});
```

- Run with: `npx jest api.e2e.test.js`
- Adjust endpoints and payloads as needed for your frontend.
