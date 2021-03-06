# Copyright (c) 2015,Vienna University of Technology,
# Department of Geodesy and Geoinformation
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the Vienna University of Technology,
#      Department of Geodesy and Geoinformation nor the
#      names of its contributors may be used to endorse or promote products
#      derived from this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
Tests for the temporal matching module
Created on Wed Jul  8 19:37:14 2015
"""


from copy import deepcopy
from datetime import datetime
import numpy as np
import numpy.testing as nptest
import pandas as pd
import pytesmo.temporal_matching as tmatching
import pytest


def test_df_match_borders():
    """
    Border values can be problematic for temporal matching.

    See issue #51
    """

    ref_df = pd.DataFrame(
        {"data": np.arange(5)},
        index=pd.date_range(datetime(2007, 1, 1, 0), "2007-01-05", freq="D"),
    )
    match_df = pd.DataFrame(
        {"matched_data": np.arange(5)},
        index=[
            datetime(2007, 1, 1, 9),
            datetime(2007, 1, 2, 9),
            datetime(2007, 1, 3, 9),
            datetime(2007, 1, 4, 9),
            datetime(2007, 1, 5, 9),
        ],
    )
    with pytest.deprecated_call():
        matched = tmatching.df_match(ref_df, match_df)

    nptest.assert_allclose(
        np.array([0.375, 0.375, 0.375, 0.375, 0.375]), matched.distance.values
    )
    nptest.assert_allclose(np.arange(5), matched.matched_data)


def test_df_match_match_on_window_border():
    """
    test matching if a value lies exactly on the window border.
    """

    ref_df = pd.DataFrame(
        {"data": np.arange(5)},
        index=pd.date_range(datetime(2007, 1, 1, 0), "2007-01-05", freq="D"),
    )
    match_df = pd.DataFrame(
        {"matched_data": np.arange(4)},
        index=[
            datetime(2007, 1, 1, 9),
            datetime(2007, 1, 2, 9),
            datetime(2007, 1, 3, 12),
            datetime(2007, 1, 5, 9),
        ],
    )
    with pytest.deprecated_call():
        matched = tmatching.df_match(ref_df, match_df, window=0.5)

    nptest.assert_allclose(
        np.array([0.375, 0.375, 0.5, -0.5, 0.375]), matched.distance.values
    )
    nptest.assert_allclose([0, 1, 2, 2, 3], matched.matched_data)

    # test asym_window keyword
    with pytest.deprecated_call():
        matched = tmatching.df_match(
            ref_df, match_df, window=0.5, asym_window="<="
        )

    nptest.assert_allclose(
        np.array([0.375, 0.375, 0.5, np.nan, 0.375]), matched.distance.values
    )
    nptest.assert_allclose([0, 1, 2, np.nan, 3], matched.matched_data)

    with pytest.deprecated_call():
        matched = tmatching.df_match(
            ref_df, match_df, window=0.5, asym_window=">="
        )

    nptest.assert_allclose(
        np.array([0.375, 0.375, np.nan, -0.5, 0.375]), matched.distance.values
    )
    nptest.assert_allclose([0, 1, np.nan, 2, 3], matched.matched_data)


def test_df_match_borders_unequal_query_points():
    """
    Border values can be problematic for temporal matching.

    See issue #51
    """

    ref_df = pd.DataFrame(
        {"data": np.arange(5)},
        index=pd.date_range(datetime(2007, 1, 1, 0), "2007-01-05", freq="D"),
    )
    match_df = pd.DataFrame(
        {"matched_data": np.arange(4)},
        index=[
            datetime(2007, 1, 1, 9),
            datetime(2007, 1, 2, 9),
            datetime(2007, 1, 4, 9),
            datetime(2007, 1, 5, 9),
        ],
    )
    with pytest.deprecated_call():
        matched = tmatching.df_match(ref_df, match_df)

    nptest.assert_allclose(
        np.array([0.375, 0.375, -0.625, 0.375, 0.375]), matched.distance.values
    )
    nptest.assert_allclose(np.array([0, 1, 1, 2, 3]), matched.matched_data)


def test_matching():
    """
    test matching function
    """
    data = np.arange(5.0)
    data[3] = np.nan

    ref_df = pd.DataFrame(
        {"data": data},
        index=pd.date_range(datetime(2007, 1, 1, 0), "2007-01-05", freq="D"),
    )
    match_df = pd.DataFrame(
        {"matched_data": np.arange(5)},
        index=[
            datetime(2007, 1, 1, 9),
            datetime(2007, 1, 2, 9),
            datetime(2007, 1, 3, 9),
            datetime(2007, 1, 4, 9),
            datetime(2007, 1, 5, 9),
        ],
    )
    with pytest.deprecated_call():
        matched = tmatching.matching(ref_df, match_df)

    nptest.assert_allclose(np.array([0, 1, 2, 4]), matched.matched_data)
    assert len(matched) == 4


def test_matching_series():
    """
    test matching function with pd.Series as input
    """
    data = np.arange(5.0)
    data[3] = np.nan

    ref_ser = pd.Series(
        data,
        index=pd.date_range(datetime(2007, 1, 1, 0), "2007-01-05", freq="D"),
    )
    match_ser = pd.Series(
        np.arange(5),
        index=[
            datetime(2007, 1, 1, 9),
            datetime(2007, 1, 2, 9),
            datetime(2007, 1, 3, 9),
            datetime(2007, 1, 4, 9),
            datetime(2007, 1, 5, 9),
        ],
        name="matched_data",
    )

    with pytest.deprecated_call():
        matched = tmatching.matching(ref_ser, match_ser)

    nptest.assert_allclose(np.array([0, 1, 2, 4]), matched.matched_data)
    assert len(matched) == 4


#############################################################################
# Tests for new implementation
#############################################################################


@pytest.fixture
def test_data():
    """
    Test data for temporal matching.

    The test frames have modified time indices:
    - shifted by 3 hours
    - shifted by 7 hours
    - shifted by 3 hours, and in a timezone such that displayed numbers are >6
      hours apart
    - shifted by 7 hours, and in a timezone such that displayed numbers are <6
      hours apart
    - randomly shifted by a value between -12h and 12h
    - same as above, but with some dropped values
    - shifted by 3 hours, with duplicates

    Returns
    -------
    ref_frame : pd.DataFrame
        Reference data frame
    test_frames : dict of pd.DataFrame
        Dictionary of data frames, keys are: "shifted_3", "shifted_7",
        "shifted_3_asia", "shifted_7_us", "random_shift", "duplicates".
    expected_nan : dict of np.ndarray
        Dictionary with same keywords as `test_frames`, each entry is a mask
        indicating where NaNs are expected (i.e. no matching was taking place)
    """
    # the reference date range
    ref_dr = pd.date_range("1970", "2020", freq="D", tz="UTC")

    test_dr = {}
    test_dr["shifted_3"] = ref_dr + pd.Timedelta(3, "H")
    test_dr["shifted_7"] = ref_dr + pd.Timedelta(7, "H")
    test_dr["shifted_3_asia"] = test_dr["shifted_3"].tz_convert(
        "Asia/Yekaterinburg"
    )
    test_dr["shifted_7_us"] = test_dr["shifted_7"].tz_convert("US/Eastern")

    # random shifts
    random_hours = np.random.uniform(-12.0, 12.0, len(ref_dr))
    random_mask = np.abs(random_hours) > 6
    dr_random_shift = ref_dr + pd.to_timedelta(random_hours, "H")
    test_dr["random_shift"] = dr_random_shift

    # missing data
    drop_mask = np.zeros(len(ref_dr), dtype=bool)
    drop_mask[100:200] = True
    dr_random_shift = dr_random_shift[~drop_mask]
    test_dr["missing"] = dr_random_shift
    missing_mask = random_mask | drop_mask

    # with duplicates
    test_dr["duplicates"] = deepcopy(test_dr["shifted_3"])
    duplicates_mask = np.zeros(len(ref_dr), dtype=bool)
    for idx in np.random.randint(0, len(test_dr["duplicates"]) - 1, 5):
        test_dr["duplicates"].values[idx] = test_dr["duplicates"].values[
            idx + 1
        ]
        duplicates_mask[idx] = True

    # setting up dataframes
    test_frames = {
        key: pd.DataFrame(
            np.random.randn(len(test_dr[key]), 3), index=test_dr[key]
        )
        for key in test_dr
    }
    ref_frame = pd.DataFrame(np.random.randn(len(ref_dr), 3), index=ref_dr)

    # mask for where we expect nans in the output
    all_nan = np.ones(len(ref_dr), dtype=bool)
    expected_nan = {
        "shifted_3": ~all_nan,
        "shifted_7": all_nan,
        "shifted_3_asia": ~all_nan,
        "shifted_7_us": all_nan,
        "random_shift": random_mask,
        "missing": missing_mask,
        "duplicates": duplicates_mask,
    }
    return ref_frame, test_frames, expected_nan


def setup_data(data, key):
    """Returns only relevant data of test_data for given key"""
    return data[0], data[1][key], data[2][key]


def compare_with_nan(a, b):
    return (a == b) | (np.isnan(a) & np.isnan(b))


def assert_equal_except_nan(res, ref, nan_mask, index_shifted=False):
    expected_nan_idx = nan_mask.nonzero()[0]
    expected_nonan_idx = (~nan_mask).nonzero()[0]
    # using column zero here, all should be the same
    nan_idx = np.isnan(res.iloc[:, 0].values).nonzero()[0]
    nonan_idx = (~np.isnan(res.iloc[:, 0].values)).nonzero()[0]
    assert len(expected_nan_idx) == len(nan_idx)
    if len(nan_idx) > 0:
        assert np.all(nan_idx == expected_nan_idx)
    if len(nonan_idx) > 0 and not index_shifted:
        assert np.all(nonan_idx == expected_nonan_idx)
        assert np.all(
            res.iloc[nonan_idx, 0].values == ref.iloc[nonan_idx, 0].values
        )


@pytest.mark.parametrize(
    "key",
    [
        "shifted_3",
        "shifted_7",
        "shifted_7_us",
        "shifted_3_asia",
        "random_shift",
    ],
)
def test_collocation_nearest_neighbour(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)
    res = tmatching.temporal_collocation(
        ref_frame, test_frame, pd.Timedelta(6, "H")
    )
    assert_equal_except_nan(res, test_frame, expected_nan)


@pytest.mark.parametrize("key", ["missing", "duplicates"])
def test_collocation_missing_duplicates(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)
    res = tmatching.temporal_collocation(
        ref_frame,
        test_frame,
        pd.Timedelta(6, "H"),
    )
    # indices of test_frame are shifted w.r.t expected_nan, therefore we can't
    # compare values
    assert_equal_except_nan(res, test_frame, expected_nan, index_shifted=True)


@pytest.mark.parametrize("key", ["shifted_3"])
def test_collocation_window(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)
    res = tmatching.temporal_collocation(
        ref_frame, test_frame, 6 / 24, dropduplicates=True
    )
    assert_equal_except_nan(res, test_frame, expected_nan, index_shifted=True)


@pytest.mark.parametrize("key", ["shifted_3"])
def test_collocation_input(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)

    no_timezone = pd.date_range("1970", "2020", freq="D")
    # test with series and index:
    for ref in [ref_frame[0], ref_frame.index, no_timezone]:
        res = tmatching.temporal_collocation(
            ref, test_frame, pd.Timedelta(6, "H")
        )
        assert_equal_except_nan(res, test_frame, expected_nan)


@pytest.mark.parametrize(
    "key",
    [
        "shifted_3",
        "shifted_7",
        "shifted_7_us",
        "shifted_3_asia",
        "random_shift",
    ],
)
def test_collocation_dropna(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)
    res = tmatching.temporal_collocation(
        ref_frame, test_frame, pd.Timedelta(6, "H"), dropna=True
    )
    expected_nonan_idx = (~expected_nan).nonzero()[0]
    assert np.all(test_frame.iloc[expected_nonan_idx, :].values == res.values)


@pytest.mark.parametrize(
    "key",
    [
        "shifted_3",
        "shifted_7",
        "shifted_7_us",
        "shifted_3_asia",
        "random_shift",
    ],
)
def test_collocation_flag(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)
    flag = np.random.choice([True, False], len(ref_frame))

    # with array
    res = tmatching.temporal_collocation(
        ref_frame,
        test_frame,
        pd.Timedelta(6, "H"),
        flag=flag,
    )

    compare_with_nan(
        res.iloc[:, 0].values[~flag], test_frame.iloc[:, 0].values[~flag]
    )
    assert np.all(np.isnan(res.values[:, 0][flag]))

    # with array, using invalid as replacement
    res = tmatching.temporal_collocation(
        ref_frame,
        test_frame,
        pd.Timedelta(6, "H"),
        flag=flag,
        use_invalid=True,
    )
    compare_with_nan(res.iloc[:, 0].values, test_frame.iloc[:, 0].values)

    # with dataframe
    test_frame["flag"] = flag
    res = tmatching.temporal_collocation(
        ref_frame,
        test_frame,
        pd.Timedelta(6, "H"),
        flag="flag",
    )
    compare_with_nan(
        res.iloc[:, 0].values[~flag], test_frame.iloc[:, 0].values[~flag]
    )
    assert np.all(np.isnan(res.iloc[:, 0].values[flag]))


# using only shifted_3, because comparison won't work when there are nans
@pytest.mark.parametrize("key", ["shifted_3"])
def test_return_index(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)
    res = tmatching.temporal_collocation(
        ref_frame, test_frame, pd.Timedelta(6, "H"), return_index=True
    )
    assert_equal_except_nan(res, test_frame, expected_nan)
    assert np.all(test_frame.index.values == res["index_other"].values)


# using only shifted_3, because comparison won't work when there are nans
@pytest.mark.parametrize("key", ["shifted_3", "shifted_7"])
def test_return_distance(test_data, key):
    ref_frame, test_frame, expected_nan = setup_data(test_data, key)
    res = tmatching.temporal_collocation(
        ref_frame, test_frame, pd.Timedelta(6, "H"), return_distance=True
    )
    assert_equal_except_nan(res, test_frame, expected_nan)
    if key == "shifted_3":
        assert np.all(res["distance_other"] == pd.Timedelta(3, "H"))
    if key == "shifted_7":
        assert np.all(np.isnan(res["distance_other"]))


def test_timezone_handling():
    # Issue #150
    data = np.arange(5.0)
    data[3] = np.nan

    match_df = pd.DataFrame(
        {"matched_data": data},
        index=pd.date_range(
            datetime(2007, 1, 1, 0), "2007-01-05", freq="D", tz="UTC"
        ),
    )
    index = pd.DatetimeIndex([
        datetime(2007, 1, 1, 9),
        datetime(2007, 1, 2, 9),
        datetime(2007, 1, 3, 9),
        datetime(2007, 1, 4, 9),
        datetime(2007, 1, 5, 9),
    ]).tz_localize("utc")
    ref_df = pd.DataFrame({"data": np.arange(5)}, index=index)
    matched = tmatching.temporal_collocation(
        ref_df, match_df, pd.Timedelta(12, "H"), dropna=True,
    )

    nptest.assert_allclose(np.array([0, 1, 2, 4]), matched.matched_data)
    assert len(matched) == 4


def test_warning_on_no_match(test_data):
    # Issue #152
    ref_frame, test_frame, expected_nan = setup_data(test_data, "shifted_7")
    with pytest.warns(UserWarning):
        tmatching.temporal_collocation(
            ref_frame, test_frame, pd.Timedelta(6, "H"), checkna=True
        )
