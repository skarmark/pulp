#!/usr/bin/python
#
# Copyright (c) 2011 Red Hat, Inc.
#
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

# Python
import mock
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/../common/")
import mock_plugins
import testutil

from pulp.server.content.conduits._base import BaseDistributorConduit, DistributorConduitException
import pulp.server.content.types.database as types_database
from pulp.server.db.model.gc_repository import Repo
import pulp.server.managers.factory as manager_factory
from pulp.server.managers.repo.cud import RepoManager
from pulp.server.managers.repo.distributor import RepoDistributorManager

# -- test cases ---------------------------------------------------------------

class BaseDistributorConduitTests(testutil.PulpTest):

    def clean(self):
        super(BaseDistributorConduitTests, self).clean()
        types_database.clean()

        Repo.get_collection().remove()

    def setUp(self):
        super(BaseDistributorConduitTests, self).setUp()
        mock_plugins.install()

        self.repo_manager = RepoManager()
        self.distributor_manager = RepoDistributorManager()

        self.repo_manager.create_repo('repo-1')
        self.distributor_manager.add_distributor('repo-1', 'mock-distributor', {}, True, distributor_id='test-distributor')

        self.conduit = BaseDistributorConduit('repo-1', 'test-distributor')

    def tearDown(self):
        super(BaseDistributorConduitTests, self).tearDown()
        manager_factory.reset()

    def test_get_set_scratchpad(self):
        """
        Tests scratchpad calls.
        """

        # Test - get no scratchpad
        self.assertTrue(self.conduit.get_scratchpad() is None)

        # Test - set scrathpad
        value = 'dragon'
        self.conduit.set_scratchpad(value)

        # Test - get updated value
        self.assertEqual(value, self.conduit.get_scratchpad())

    def test_scratchpad_with_error(self):
        # Setup
        mock_distributor_manager = mock.Mock()
        mock_distributor_manager.get_distributor_scratchpad.side_effect = Exception()
        mock_distributor_manager.set_distributor_scratchpad.side_effect = Exception()

        manager_factory._INSTANCES[manager_factory.TYPE_REPO_DISTRIBUTOR] = mock_distributor_manager

        # Test
        self.assertRaises(DistributorConduitException, self.conduit.get_scratchpad)
        self.assertRaises(DistributorConduitException, self.conduit.set_scratchpad, 'foo')