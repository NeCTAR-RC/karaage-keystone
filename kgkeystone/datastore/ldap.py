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

import logging

from karaage.datastores.ldap import AccountDataStore as BaseAccountDataStore, _str_or_none
from kgkeystone.hasher import django_to_passlib

from keystoneclient import client
from keystoneclient import exceptions

logger = logging.getLogger('kgkeystone.datastore')


class AccountDataStore(BaseAccountDataStore):
    """LDAP Account datastore."""

    def save_account(self, account):
        """ Account was saved. """
        person = account.person
        if self._primary_group == 'institute':
            lgroup = self._groups().get(cn=person.institute.group.name)
        elif self._primary_group == 'default_project':
            if account.default_project is None:
                lgroup = self._groups().get(cn=self._default_primary_group)
            else:
                lgroup = self._groups().get(
                    cn=account.default_project.group.name)
        else:
            raise RuntimeError("Unknown value of PRIMARY_GROUP.")

        if account.default_project is None:
            default_project = "none"
        else:
            default_project = account.default_project.pid

        try:
            luser = self._accounts().get(uid=account.username)
            luser.gidNumber = lgroup.gidNumber
            luser.givenName = person.first_name
            luser.sn = person.last_name
            luser.fullName = person.full_name
            luser.telephoneNumber = _str_or_none(person.telephone)
            luser.mail = _str_or_none(person.email)
            luser.title = _str_or_none(person.title)
            luser.o = person.institute.name
            luser.gidNumber = lgroup.gidNumber
            luser.userPassword = '{crypt}' + django_to_passlib(person.password).encode('latin1')
            print luser.userPassword
            luser.homeDirectory = self._home_directory % {
                'default_project': default_project,
                'uid': person.username }
            if account.is_locked():
                luser.loginShell = self._locked_shell
                luser.lock()
            else:
                luser.loginShell = account.shell
                luser.unlock()
            luser.save()
        except self._account.DoesNotExist:
            luser = self._create_account()
            luser.uid = person.username
            luser.givenName = person.first_name
            luser.sn = person.last_name
            luser.fullName = person.full_name
            luser.telephoneNumber = _str_or_none(person.telephone)
            luser.mail = _str_or_none(person.email)
            luser.title = _str_or_none(person.title)
            luser.o = person.institute.name
            luser.gidNumber = lgroup.gidNumber
            luser.userPassword = '{crypt}' + django_to_passlib(person.password).encode('latin1')
            luser.homeDirectory = self._home_directory % {
                'default_project': default_project,
                'uid': person.username }
            if account.is_locked():
                luser.loginShell = self._locked_shell
                luser.lock()
            else:
                luser.loginShell = account.shell
                luser.unlock()
            luser.save()

            # add all groups
            for group in account.person.groups.all():
                self.add_account_to_group(account, group)
