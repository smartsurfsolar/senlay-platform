# Contributing

Use `develop` as the integration branch. Create a focused feature branch, add tests, and open a pull request into `develop`. Stable releases are promoted from `develop` to `main` after review.

Before submitting:

```bash
npm run check
npm test
```

Python connector tests use Python 3.9 or newer and have no third-party dependencies.

Do not submit credentials, personal data, proprietary provider payloads, production database content, or code copied from the private Senlay core. By contributing, you agree that your contribution is licensed under Apache-2.0.
