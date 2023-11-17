# pytest-order Release Notes

## [Version 1.2.0](https://pypi.org/project/pytest-order/1.2.0/) (2023-11-18)
Allows using custom markers for ordering.

### New features
* added option `--order-marker-prefix` to allow using custom markers for ordering

### Infrastructure
- added pre-commit hook for linters
- added Python 3.12 to supported versions

## [Version 1.1.0](https://pypi.org/project/pytest-order/1.1.0/) (2023-03-10)
Adds support for executing tests more than once using order marks.

### New features
- added support for multiple test order markers

### Changes
- removed official support for Python 3.6

### Infrastructure
- added pytest 7.x to CI tests
- added Python 3.11 to and removed Python 3.6 from CI tests
- moved documentation to [Read the Docs](https://pytest-order.readthedocs.io)

## [Version 1.0.1](https://pypi.org/project/pytest-order/1.0.1/) (2022-01-09)
Bugfix release.

### Fixes
- correctly handle combined class and test order markers,
  see [#45](https://github.com/pytest-dev/pytest-order/issues/45)
- adapt code to changed type of `automark_dependency` in development branch
  of `pytest-dependency`,
  see [#58](https://github.com/pytest-dev/pytest-order/issues/58)

## [Version 1.0.0](https://pypi.org/project/pytest-order/1.0.0/) (2021-05-30)
First Python 3 only version.

### Breaking changes
- removed support for Python 2.7 and 3.5
- removed official support for pytest < 5.0.0 (older versions may still
  work, but they are not tested)
- changed notation of relative markers in other modules - instead of using
  the dot notation, the standard pytest nodeid is used,
  see [#24](https://github.com/pytest-dev/pytest-order/issues/24)
- using parametrized test names that include the parameter is no longer
  supported, just use the name without the parameter instead

### New features
- added support for the ``pytest-dependency`` option ``automark_dependency``
- added support for relative ordering of parametrized tests using the test
  name without the parameter value,
  see [#38](https://github.com/pytest-dev/pytest-order/issues/38)

### Infrastructure
- re-added Python 3.10 to CI tests (for pytest >= 6.2.4)
- added type hints

## [Version 0.11.0](https://pypi.org/project/pytest-order/0.11.0/) (2021-04-11)
Adds support for multiple relative markers for the same test.

### New features
- added support for more than one relative marker for the same test

### Infrastructure
- added Python 3.10 to CI tests

## [Version 0.10.0](https://pypi.org/project/pytest-order/0.10.0/) (2021-03-18)
Adds support for class-level relative markers and directory level scope.

### New features
- added support for class level relative markers,
  see [#7](https://github.com/pytest-dev/pytest-order/issues/7)
- added option `--order-scope-level` which allows grouping tests on the
  same directory level,
  see [#8](https://github.com/pytest-dev/pytest-order/issues/8)

### Fixes
- fixed sorting of dependency markers that depend on an item with the same
  name in different modules

### Infrastructure
- added performance tests to prevent performance degradation
- added automated deploy workflow step triggered on creating a tag

## [Version 0.9.5](https://pypi.org/project/pytest-order/0.9.5/) (2021-02-16)
Introduces hierarchical ordering option and fixes ordering of session-scoped
dependency markers.

### Changes
- tests with unresolved relative markers are now handled like tests
  without order markers instead of being enqueued after all other tests

### New features
- added `group-order-scope` option to allow hierarchical ordering on module
  and class scope,
  see [#6](https://github.com/pytest-dev/pytest-order/issues/6)

### Fixes
- the dependency marker scope is now considered for resolving marker names
  (module scope had been assumed before)
- dependency markers in session scope referenced by the nodeid are now
  correctly sorted if using the `order-dependencies` option


## [Version 0.9.4](https://pypi.org/project/pytest-order/0.9.4/) (2021-01-27)
Patch release to make packaging easier.

### Infrastructure
- use codecov instead of coveralls, that is failing
- added pytest 6.2 to CI tests
- added tests, examples and documentation to source package,
  see [#5](https://github.com/pytest-dev/pytest-order/issues/5)

## [Version 0.9.3](https://pypi.org/project/pytest-order/0.9.3/) (2021-01-14)
Bugfix release.

### Fixes
- fixed handling of more than one attribute in an order marker

## [Version 0.9.2](https://pypi.org/project/pytest-order/0.9.2/) (2020-11-13)
Friday the 13th release.

### Changes
- changed definition of classes in before/after markers (now uses `::` as
  delimiter)

### Fixes
- fixed handling of before/after markers in different classes and modules
- fixed handling of names in dependencies - did not match the actual
  behavior of `pytest-dependency`

## [Version 0.9.1](https://pypi.org/project/pytest-order/0.9.1/) (2020-11-11)
This is a bugfix only release.

### Fixes
- fixed handling of relative markers in classes
- fixed handling of dependencies (could have been added twice)

## [Version 0.9.0](https://pypi.org/project/pytest-order/0.9.0/) (2020-11-08)
This is the last major version that will support Python 2 - Python 2 support
will be dropped in version 1.0. There is no timeline for that release, as there
are currently no new features planned - further development will be
demand-driven.

### Changes
- removed support for pytest 3.6 (it still may work, just isn't tested anymore)

### New features
- added configuration option for sparse sorting, e.g. the possibility to
  fill gaps between ordinals with unordered tests (see also
  [this issue](https://github.com/ftobia/pytest-ordering/issues/14) in
  `pytest-ordering`)
- ignore ordering if it would break a dependency defined by the
  `pytest-dependency` plugin
- experimental: added configuration option for ordering all dependencies
  defined by the `pytest-dependency` plugin
- added ``index`` keyword for ordering as alternative to raw number

### Fixes
- correctly handle combined index and dependency attributes

### Infrastructure
- added list of open issues in `pytest-ordering` with respective state
  in `pytest-order`

## [Version 0.8.1](https://pypi.org/project/pytest-order/0.8.1/) (2020-11-02)

### New features
- added configuration option for sorting scope,
  see [#2](https://github.com/pytest-dev/pytest-order/issues/2)

## [Version 0.8.0](https://pypi.org/project/pytest-order/0.8.0/) (2020-10-30)
This release is mostly related to the consolidation of infrastructure
(documentation build and tests in CI build) and documentation.

### Fixes
- fixed the handling of unknown marker attributes (test had been skipped)

### Infrastructure
- added automatic documentation build on change
- added Python 3.9, pypy3 and pytest 6.0 and 6.1 to CI builds
- use GitHub Actions for CI builds to speed them up, added Windows CI builds
- added regression test for ``pytest-xdist``
  (imported from [PR #52](https://github.com/ftobia/pytest-ordering/pull/52))

## [Version 0.7.1](https://pypi.org/project/pytest-order/0.7.1/) (2020-10-24)
Update after renaming the repository and the package.

### Changes
- renamed repository and package from ``pytest-ordering2`` to ``pytest-order``
- changed the used marker from ``run`` to ``order``, removed all additional
  markers (see [#38](https://github.com/ftobia/pytest-ordering/issues/38))

### Documentation
- use separate documentation pages for release and development versions

## Version 0.7.0 (2020-10-22)
Imported version from [pytest-ordering](https://github.com/ftobia/pytest-ordering),
including some PRs (manually merged).
Note: this version has been removed from PyPi to avoid confusion with the
changed name in the next release.

### New features
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
- moved documentation to [GitHub Pages](https://pytest-dev.github.io/pytest-order/)
