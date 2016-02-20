# -*- coding: utf-8 -*-
#
# Copyright (c) 2015-2016 Alessandro Amici
#

from pytest_nodev import plugin


TEST_PASS_PY = '''
def test_pass():
    assert True
'''
TEST_FACTORIAL_PY = '''
def test_factorial(wish):
    factorial = wish
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(21) == 51090942171709440000
'''
TEST_FACTORIAL_TXT = '''
# test
math:fabs # comment
math:factorial
'''


def test_import_coverage():
    """Fix the coverage by pytest-cov, that may trigger after pytest_nodev is already imported."""
    from imp import reload  # Python 2 and 3 reload
    reload(plugin)


#
# pytest hooks
#
def test_pytest_addoption(testdir):
    """The plugin is registered with pytest."""
    result = testdir.runpytest(
        '--help',
    )
    # fnmatch_lines does an assertion internally
    result.stdout.fnmatch_lines([
        'wish:',
        '*--wish-from-stdlib*',
        '*--wish-fail*',
    ])


def test_pytest_generate_tests(testdir):
    testdir.makepyfile(TEST_FACTORIAL_PY + TEST_PASS_PY)
    result = testdir.runpytest(
        '--wish-from-modules=math',
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*math:factorial*XPASS',
        '*test_pass*PASSED',
    ])
    assert result.ret == 0

    result = testdir.runpytest(
        '--wish-from-modules=math',
        '--wish-fail',
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*math:factorial*PASSED',
        '*test_pass*PASSED',
    ])
    assert result.ret == 1


def test_pytest_terminal_summary(testdir):
    testdir.makepyfile(TEST_PASS_PY)
    result = testdir.runpytest(
        '-v'
    )
    result.stdout.fnmatch_lines([
        '*test_pass*PASSED',
    ])
    assert result.ret == 0

    testdir.makepyfile(TEST_FACTORIAL_PY)
    result = testdir.runpytest(
        '--wish-from-modules=math',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*math:factorial*HIT',
    ])
    assert result.ret == 0


#
# command line options
#
def test_pytest_run_no_wish(testdir):
    """We didn't break pytest."""
    testdir.makepyfile(TEST_PASS_PY)
    result = testdir.runpytest(
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_pass*PASSED',
    ])
    assert result.ret == 0


def test_pytest_run_no_wish_option(testdir):
    """Skip tests with the *wish* fixture if no ``--wish-*`` option is given."""
    testdir.makepyfile(TEST_FACTORIAL_PY)
    result = testdir.runpytest(
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*wish*SKIPPED',
    ])
    assert result.ret == 0


def test_pytest_run_from_modules(testdir):
    testdir.makepyfile(TEST_FACTORIAL_PY)
    result = testdir.runpytest(
        '--wish-from-modules=math',
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*math:fabs*xfail',
        '*test_factorial*math:factorial*XPASS',
    ])
    assert result.ret == 0


def test_pytest_run_from_specs(testdir):
    testdir.makepyfile(TEST_FACTORIAL_PY)
    result = testdir.runpytest(
        '--wish-from-specs=pip',
        '--wish-includes=pip.exceptions',
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*pip.exceptions:*xfail',
    ])
    assert result.ret == 0


def test_pytest_run_from_stdlib(testdir):
    testdir.makepyfile(TEST_FACTORIAL_PY)
    result = testdir.runpytest(
        '--wish-from-stdlib',
        '--wish-includes=math',
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*math:fabs*xfail',
        '*test_factorial*math:factorial*XPASS',
    ])
    assert result.ret == 0


def test_pytest_run_from_all(testdir, monkeypatch):
    testdir.makepyfile(TEST_FACTORIAL_PY)
    result = testdir.runpytest(
        '--wish-from-all',
        '--wish-includes=math:factorial|pip.exceptions',
        '-v',
    )
    assert result.ret == 1

    monkeypatch.setenv('PYTEST_NODEV_MODE', 'FEARLESS')
    result = testdir.runpytest(
        '--wish-from-all',
        '--wish-includes=math:factorial|pip.exceptions',
        '-v',
    )
    result.stdout.fnmatch_lines([
        '*test_factorial*math:factorial*XPASS',
        '*test_factorial*pip.exceptions:*xfail',
    ])
    assert result.ret == 0


def test_wish_modules_object_blacklist(testdir):
    testdir.makepyfile(TEST_FACTORIAL_PY)
    result = testdir.runpytest(
        '--wish-from-modules=posix',
        '--wish-includes=.*exit',
        '-v',
    )
    assert result.ret == 0
