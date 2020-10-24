# pytest-order Release Notes

## Unreleased

### Changes
- changed the used marker from ``run`` to ``order``, removed all additional
  markers (see [#38](https://github.com/ftobia/pytest-ordering/issues/38))
- renamed repository and package from ``pytest-orderin2`` to ``pytest-order``

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
