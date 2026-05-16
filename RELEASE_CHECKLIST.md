# Release Checklist

Use this checklist before creating a GitHub release or Zenodo archive.

## Code and tests

- [ ] `make test` passes.
- [ ] `make reproduce-main` completes.
- [ ] Optional validation runs are documented.
- [ ] Artifact manifest is generated.
- [ ] README result claims match checked-in artifacts.

## Documentation

- [ ] README updated.
- [ ] `CITATION.cff` present.
- [ ] `CONTRIBUTING.md` present.
- [ ] `docs/` complete.
- [ ] `CHANGELOG.md` updated.
- [ ] License present.

## Release

- [ ] Version tag created, for example `v1.0.0`.
- [ ] GitHub release notes summarize changes.
- [ ] Zenodo integration enabled, if a DOI is desired.
- [ ] DOI added after Zenodo creates it.

Do not create a fake DOI, publication link, venue acceptance claim, or artifact
badge.
