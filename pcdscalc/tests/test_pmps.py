import logging

import pytest

from pcdscalc.pmps import (LFE, KFE, select_bitmask_boundaries,
                           get_bitmask, check_bitmask, check_actual_range,
                           describe_bitmask)


logger = logging.getLogger(__name__)

# 32 bits, using numbers from 1 to 32
test_boundaries = list(range(1, 33))

# Define some utility bitmasks
allow_none = 0
allow_all = 2**32-1
bm1 = 0b1111_0000_0000_0000_0000_0000_0000_1111
bm2 = 0b0000_0000_0000_1111_1111_0000_0000_0000
bm3 = 0b0000_0000_0000_0001_0000_0000_0000_0000
bm4 = 0b1111_1111_1111_1110_1111_1111_1111_1111


@pytest.mark.parametrize(
    "test_input,expected",
    [('k', KFE), ('kfe', KFE), ('sxr', KFE),
     ('L', LFE), ('LFE', LFE), ('HXR', LFE)]
    )
def test_select_bounds(test_input, expected):
    logger.debug(f'test_select_bounds({test_input}, {expected})')
    assert select_bitmask_boundaries(test_input) is expected


@pytest.mark.parametrize(
    "lower,upper,allow,expected",
    [(0, 100, True, allow_all),
     (0, 100, False, allow_none),
     (0, 15.5, True,     0b0000_0000_0000_0000_0111_1111_1111_1111),
     (15.5, 100, True,   0b1111_1111_1111_1111_0000_0000_0000_0000),
     (14.5, 21.5, True,  0b0000_0000_0001_1111_1000_0000_0000_0000),
     (14.5, 21.5, False, 0b1111_1111_1100_0000_0011_1111_1111_1111),
     (15, 20, True,      0b0000_0000_0000_1111_1000_0000_0000_0000)])
def test_get_bitmask(lower, upper, allow, expected):
    logger.debug(f'test_get_bitmask({lower}, {upper}, {allow}, {expected})')
    bitmask = get_bitmask(lower, upper, allow, 'tst', bounds=test_boundaries)
    assert bitmask == expected


@pytest.mark.parametrize(
    "energy,bitmask,expected",
    [(-1, allow_all, False), (100, allow_all, False), (16, allow_all, True),
     (0, allow_none, False), (15, allow_none, False), (30, allow_none, False),
     (0, bm1, True), (16, bm1, False), (30, bm1, True), (40, bm1, False),
     (0, bm2, False), (16, bm2, True), (30, bm2, False), (-1, bm2, False),
     (7, bm3, False), (16, bm3, False), (16.5, bm3, True), (17, bm3, False),
     (15, bm4, True), (16, bm4, False), (16.5, bm4, False), (17, bm4, False)])
def test_check_bitmask(energy, bitmask, expected):
    logger.debug(f'test_check_bitmask({energy}, {bitmask}, {expected}')
    ok = check_bitmask(energy, bitmask, 'tst', bounds=test_boundaries)
    assert ok == expected


@pytest.mark.parametrize(
    "lower,upper,allow,expected",
    [(0, 100, True, (0, 32)),
     (10, 20, True, (10, 20)),
     (10.5, 20.5, True, (11, 20)),
     (11, 21, False, (11, 21)),
     (9.5, 15.5, False, (9, 16)),
     (10.4, 10.6, True, (10.4, 10.4))])
def test_actual_range(lower, upper, allow, expected):
    logger.debug(f'test_actual_range({lower}, {upper}, {allow}, {expected})')
    span = check_actual_range(lower, upper, allow, 'tst',
                              bounds=test_boundaries)
    assert span == expected


@pytest.mark.parametrize(
    "test_input",
    [allow_none, allow_all, bm1, bm2, bm3, bm4])
def test_describe_bitmask(test_input):
    logger.debug(f'test_describe_bitmask({test_input})')
    describe_bitmask(test_input, 'tst', bounds=test_boundaries)
