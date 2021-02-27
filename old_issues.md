List of issues in pytest-ordering 
---------------------------------

Tracks the state of all open issues in pytest-ordering for reference.

- [Implement "before" and "after" markers](https://github.com/ftobia/pytest-ordering/issues/6)  
  manually merged respective [PR](https://github.com/ftobia/pytest-ordering/pull/37)
  by Jonas Zinn :heavy_check_mark:
- [Custom markers](https://github.com/ftobia/pytest-ordering/issues/10)  
  will not be implemented (see 
  [this issue](https://github.com/ftobia/pytest-ordering/issues/38)) :-1:
- [Support for ordering testcases](https://github.com/ftobia/pytest-ordering/issues/12)  
  unclear question, will ignore :-1:
- [Test sparse ordinal behavior](https://github.com/ftobia/pytest-ordering/issues/14)
  - added tests from [this PR](https://github.com/ftobia/pytest-ordering/pull/29),
  - added `sparse-ordering` option, implemented behavior :heavy_check_mark:
- [Doesn't work when using inside a class](https://github.com/ftobia/pytest-ordering/issues/18)  
  seems to be fixed :heavy_check_mark:
- [Allow ordering on per-class or per-module basis, instead of just per-session](https://github.com/ftobia/pytest-ordering/issues/20)  
  added `--order-scope` option :heavy_check_mark:
- [Ordering with multiple files](https://github.com/ftobia/pytest-ordering/issues/25)  
  behavior can be configured with `--order-scope=module` :heavy_check_mark:
- [Move to pytest-dev organization](https://github.com/ftobia/pytest-ordering/issues/32)  
  handled in mirrored [issue](https://github.com/mrbean-bremen/pytest-order/issues/4) :heavy_check_mark:
- [Ordering of test suite](https://github.com/ftobia/pytest-ordering/issues/33)  
  don't understand the issue, ignoring :-1:
- [Ensure compatibility with xdist](https://github.com/ftobia/pytest-ordering/issues/36)  
  added/adapted [respective test](https://github.com/ftobia/pytest-ordering/pull/52) by Andrew Gilbert :heavy_check_mark:
- [Standardize on a single marker name: "order"](https://github.com/ftobia/pytest-ordering/issues/38)  
  implemented :heavy_check_mark:
- [Remove not existing "relative ordering" feature from docs](https://github.com/ftobia/pytest-ordering/issues/39)  
  obsolete, docs are up-to-date :heavy_check_mark:
- [Ordering ignored on specification of multiple testcases](https://github.com/ftobia/pytest-ordering/issues/42)  
  added respective test, seems to work correctly :heavy_check_mark:
- [Order will work between diffrent testClass](https://github.com/ftobia/pytest-ordering/issues/53)  
  behavior can be configured with `--order-scope=class` :heavy_check_mark:
- [Unknown mark warning](https://github.com/ftobia/pytest-ordering/issues/57)  
  obsolete with registered marker :heavy_check_mark:
- [pytest-ordering doesn't honor test dependencies](https://github.com/ftobia/pytest-ordering/issues/58)  
  - ignore ordering if it would break a dependency
  - added configuration option for ordering all dependencies :heavy_check_mark:
- [should pytest-ordering be deprecated in favor of pytest-dependency?](https://github.com/ftobia/pytest-ordering/issues/59)  
  has been answered (`pytest-dependency` does not support ordering) :heavy_check_mark: 
- [py.test ordering doesn't works when methods with order greater than 9 are present](https://github.com/ftobia/pytest-ordering/issues/61)  
  not reproducible, probably obsolete :-1:
- [All ordering tests are failing (git develop)](https://github.com/ftobia/pytest-ordering/issues/62)  
  not reproducible, will ignore :-1:
- [Packaging the license file](https://github.com/ftobia/pytest-ordering/issues/63)  
  done in [this PR](https://github.com/ftobia/pytest-ordering/pull/68)
  by Álvaro Mondéjar :heavy_check_mark:
- [pytest ordering excecute in reverse order](https://github.com/ftobia/pytest-ordering/issues/64)  
  not reproducible, will ignore :-1:
- [The module relative order don't working???](https://github.com/ftobia/pytest-ordering/issues/65)  
  see [Implement "before" and "after" markers](https://github.com/ftobia/pytest-ordering/issues/6) :heavy_check_mark:  
- [Travis.CI results not showing up in GitHub](https://github.com/ftobia/pytest-ordering/issues/70)  
  not an issue here :heavy_check_mark:
- [Test ordering is completely broken](https://github.com/ftobia/pytest-ordering/issues/73)  
  obsolete, shall work with respective `order` markers :heavy_check_mark: 
- [license is showing as UNKNOWN in pip show command.](https://github.com/ftobia/pytest-ordering/issues/75)  
  fixed by adding the license to `setup.py` :heavy_check_mark:
