# Repositories and releases

| Repository | Visibility | Contents |
| --- | --- | --- |
| `smartsurfsolar/senlay-platform` | Public | Apache-2.0 protocol, SDK, edge gateway, examples and API documentation |
| `smartsurfsolar/senlay-world` | Public | Website source, styles and curated public assets; retains its website license |
| `smartsurfsolar/senlay-platform-core` | Private | Backend, authentication, admin services, sensor integration, memory implementation and operations |

Each uses `main` for stable work and `develop` for development. Visibility belongs to the repository: branches inside a public repository are public too. Private implementation and Git history are never merged into a public repository.

The production domain is `senlay.cloud`; `senlay-world` is the historical repository name. Browser pages contain client code only. Account records, credentials, runtime observations, databases, logs and backups are not published.

Registering a station does not automatically remove API limits. Contributor access is arranged during pilot onboarding. Upcoming provider-key connections and documentation-review features should not be treated as generally available until announced and verified.
