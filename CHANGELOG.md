# pytest-order Release Notes

## Unreleased

### Fixes
- fixed the handling of unknown marker attributes (test had been skipped)

### Infrastructure
- added automatic documentation build on change 
- add Python 3.9, pypy3 and pytest 6.0 and 6.1 to CI builds
- use GitHub Actions for builds, add Windows builds
- add regression test for ``pytest-xdist`` 
  (imported from [PR #52](https://github.com/ftobia/pytest-ordering/pull/52))

## [Version 0.7.1](https://pypi.org/project/pytest-order/0.7.1/)
Update after renaming the repository and the package.

### Changes
- renamed repository and package from ``pytest-orderin2`` to ``pytest-order``
- changed the used marker from ``run`` to ``order``, removed all additional
  markers (see [#38](https://github.com/ftobia/pytest-ordering/issues/38))
  
### Documentation
- use separate documentation pages for release and development versions

## [Version 0.7.0](https://pypi.org/project/pytest-ordering2/0.7.0/)
Imported version from [pytest-ordering](https://github.com/ftobia/pytest-ordering), 
including some PRs (manually merged).

### Added
- added support for markers like run(before=...), run(after=),
  run("first") etc.
  (imported from [PR #37](https://github.com/ftobia/pytest-ordering/pull/37))
- added ``--indulgent-ordering`` to request that the sort from
  pytest-ordering be run before other plugins.  This allows the built-in
  ``--failed-first`` implementation to override the ordering.
  (imported from [PR #50](https://github.com/ftobia/pytest-ordering/pull/50))
- include LICENSE file in distribution
  (imported from [PR #68](https://github.com/ftobia/pytest-ordering/pull/68))

### Infrastructure
- added more pytest versions, fix pytest-cov compatibility issue,
  remove Python 3.4, add Python 3.8
  (imported from [PR #74](https://github.com/ftobia/pytest-ordering/pull/74))
- moved documentation to [GitHub Pages](https://mrbean-bremen.github.io/pytest-order/)
