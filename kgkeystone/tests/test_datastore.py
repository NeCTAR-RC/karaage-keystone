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
from factory import fuzzy

from kgkeystone.tests.integration import IntegrationTestCase


class MachineCategoryDataStoreTestCase(IntegrationTestCase):

    def _create_account(self, use_datastore=True):
        account = fixtures.AccountFactory()
        account.foreign_id = None
        if use_datastore:
            self.mc_datastore.save_account(account)
        return account

    def _create_project(self, use_datastore=True):
        project = fixtures.ProjectFactory()
        project.group.foreign_id = None
        if use_datastore:
            self.mc_datastore.save_project(project)
        return project

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

    def test_update_account(self):
        account = self._create_account()

        account.person.email = ('%s@example.com' %
                                fuzzy.FuzzyText().fuzz())
        account.username = fuzzy.FuzzyText().fuzz()
        account.login_enabled = False
        self.mc_datastore.save_account(account)
        k_account = self.keystone_client.users.get(account.foreign_id)
        person = account.person

        self.assertEqual(k_account.email, person.email)
        self.assertEqual(k_account.name, account.username)
        self.assertEqual(k_account.id, account.foreign_id)
        self.assertFalse(k_account.enabled)

    def test_disable_account(self):
        account = self._create_account()

        # Check enabled
        self.mc_datastore.save_account(account)
        k_account = self.keystone_client.users.get(account.foreign_id)
        self.assertTrue(k_account.enabled)

        # Check disable
        account.login_enabled = False
        self.mc_datastore.save_account(account)
        k_account = self.keystone_client.users.get(account.foreign_id)
        self.assertFalse(k_account.enabled)

    def test_lock_person(self):
        account = self._create_account()

        # Check enabled
        self.mc_datastore.save_account(account)
        k_account = self.keystone_client.users.get(account.foreign_id)
        self.assertTrue(k_account.enabled)

        # Check disable
        account.person.lock()
        self.mc_datastore.save_account(account)
        k_account = self.keystone_client.users.get(account.foreign_id)
        self.assertFalse(k_account.enabled)

    def test_account_details(self):
        account = self._create_account()
        get_account_details = self.mc_datastore.get_account_details
        result = get_account_details(account)
        # At the moment we don't care about the links
        del result['links']
        self.assertEqual(result,
                         {'name': account.username,
                          'id': account.foreign_id,
                          'email': ('%s@example.com' %
                                    account.person.username),
                          'domain_id': 'default',
                          'enabled': True})

    def test_account_exists(self):
        account = self._create_account()
        account_exists = self.mc_datastore.account_exists

        self.assertTrue(account_exists(account.username))

        self.assertFalse(account_exists(account.username + "1"))

    def test_delete_account(self):
        account = self._create_account()
        account_exists = self.mc_datastore.account_exists
        delete_account = self.mc_datastore.delete_account

        self.assertTrue(account_exists(account.username))
        delete_account(account)
        self.assertFalse(account_exists(account.username))

    def test_delete_nonexistant_account(self):
        account = fixtures.AccountFactory()
        delete_account = self.mc_datastore.delete_account
        delete_account(account)

    def test_save_project(self):
        project = self._create_project()

        k_project = self.keystone_client.projects.get(project.group.foreign_id)
        self.assertEqual(k_project.domain_id, 'default')
        self.assertEqual(k_project.enabled, project.is_active)
        self.assertEqual(k_project.id, project.group.foreign_id)
        self.assertEqual(k_project.name, project.pid)
