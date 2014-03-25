# Copyright 2014 The University of Melbourne
#
# This file is part of karaage-keystone.
#
# karaage-keystone is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# karaage-keystone is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with karaage-keystone If not, see
# <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

from karaage.tests import fixtures

from kgkeystone.tests.integration import IntegrationTestCase


class MachineCategoryDataStoreTestCase(IntegrationTestCase):

    def _create_account(self, use_datastore=True):
        account = fixtures.AccountFactory()
        account.foreign_id = None
        if use_datastore:
            self.mc_datastore.save_account(account)
        return account


    ###########
    # ACCOUNT #
    ###########

    def test_account_create(self):
        account = self._create_account()
        person = account.person

        k_account = self.keystone_client.users.get(account.foreign_id)
        self.assertEqual(person.email, k_account.email)
        self.assertEqual(account.username, k_account.name)
        self.assertEqual(account.foreign_id, k_account.id)
        self.assertTrue(k_account.enabled)
