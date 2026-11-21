# Contributing

This document describes how changes are proposed, reviewed and released.

## Workflow

1. **Open an issue** for each planned change, using the *Task* or *Bug report*
   template. The issue holds the technical detail: affected files, message
   contracts, test cases and acceptance criteria.
2. **Create a branch from `main`**, one per issue:

   | Prefix | Use |
   |---|---|
   | `feat/` | New behaviour |
   | `fix/` | Bug fix |
   | `refactor/` | Internal change with no behaviour change |
   | `docs/` | Documentation only |
   | `test/` | Tests only |
   | `chore/` | Tooling, dependencies, CI, build |

   Example: `fix/mqtt-resubscribe`.
3. **Open a pull request** with the template filled in, and link the issue
   with `Closes #N`. Keep pull requests reviewable in one sitting (as a guide,
   under 400 changed lines).
4. **Merge with squash** once CI is green. The squash commit title follows
   Conventional Commits.

`main` is protected: every change goes through a pull request.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(optional scope): <short summary in the imperative>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`.
A breaking change adds `!` after the type (`feat!: …`) and explains it in the body.

## Architecture decisions

Any change that affects the architecture (a new component, a protocol, a
storage choice, a message contract) needs an
[Architecture Decision Record](docs/adr/README.md) in the same pull request.
A change that contradicts an accepted ADR adds a new ADR that supersedes it;
existing ADRs are never rewritten.

## Versioning and releases

The project follows [Semantic Versioning](https://semver.org/).

- `0.x` versions are pre-stable: MQTT messages and the API may change incompatibly between minor versions.
- `v0.1.0` is the version delivered for the course.
- Each completed roadmap phase is released as the next minor version (`v0.2.0`, `v0.3.0`, …).
- `v1.0.0` marks the first stable release. From then on, incompatible changes bump the major version.

A phase is complete when CI is green, `docker compose up` starts cleanly and
the reference scenario runs. Every release updates [`CHANGELOG.md`](CHANGELOG.md).

## Running the project

```bash
docker compose up --build
```

See the [README](README.md) for local (non-Docker) instructions.
