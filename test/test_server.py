# coding=utf-8
# Copyright (c) 2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import pytest
from drserv import server


@pytest.fixture
def cls():
    return server.DrservServer


class TestServerParsePath(object):
    def test_part_splitting(self, cls):
        major, minor, component, filename = cls.parse_path(
            '/v1/publish/squeeze/stable/non-free/some-package_1.deb'
        )
        assert major == 'squeeze'
        assert minor == 'stable'
        assert component == 'non-free'
        assert filename == 'some-package_1.deb'

    # TODO thiderman: All of these are raising the same exception. It's
    # probably okay, but if we want to know exactly what's going on we would
    # need to differentiate them more.
    def test_invalid_numeric_path(self, cls):
        with pytest.raises(ValueError):
            cls.parse_path(42)

    def test_invalid_unicode_path(self, cls):
        with pytest.raises(ValueError):
            cls.parse_path(u'€')

    def test_control_characters_disallowed(self, cls):
        with pytest.raises(ValueError):
            cls.parse_path('\x00')

    def test_relative_paths_disallowed(self, cls):
        with pytest.raises(ValueError):
            cls.parse_path('/v1/publish/../../../some-package_1.deb')

    def test_deb_file_suffix_is_required(self, cls):
        with pytest.raises(ValueError):
            cls.parse_path('/v1/publish/squeeze/stable/non-free/foo')

    def test_wrong_number_of_path_arguments(self, cls):
        with pytest.raises(server.HttpException):
            cls.parse_path('/v1/publish/squeeze/stable/foo.deb')
