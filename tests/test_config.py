# -*- coding: utf-8 -*-


def test_cmd_cfg(testdir, options):
    """test config through command line arguments"""
    src = options.printtest()
    testdir.makepyfile(src)
    result = testdir.runpytest(*options.options2arg("cmd_options"))
    assert result.ret == 0


def test_env_cfg(testdir, options):
    """test config through env variables"""
    src = options.printtest()
    testdir.makepyfile(src)
    options.options_setenv("cmd_options")
    result = testdir.runpytest()
    options.options_unsetenv("cmd_options")

    assert result.ret == 0


def test_marker_cfg(testdir, options):
    """test config through fixtures"""
    src = options.printmarkertest()
    testdir.makepyfile(src)
    result = testdir.runpytest()

    assert result.ret == 0
