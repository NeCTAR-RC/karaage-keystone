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

from karaage.datastores import base

from keystoneclient import client
from keystoneclient import exceptions

logger = logging.getLogger('kgkeystone.datastore')


def person_uuid(person):
    return person.account_set.filter().foreign_id


def account_to_os(account):
    data = {'name': account.username,
            'domain': 'default',
            'email': account.person.email,
            'enabled': not account.person.is_locked()}
    if account.default_project and account.default_project.group.foreign_id:
        default_project_id = account.default_project.group.foreign_id
        data['default_project'] = default_project_id
    return data


def project_to_os(project):
    ks_name = project.group.extra_data.get('keystone_name', None)
    return {'name': ks_name or project.group.name,
            'domain': 'default',
            'description': project.description,
            'enabled': project.is_active}


class AccountDataStore(base.BaseDataStore):
    """Keystone enabled datastores."""

    def __init__(self, config):
        self.config = config
        self._endpoint = config['ENDPOINT']
        self._token = config['TOKEN']
        self._version = config.get('VERSION', None)
        self._leader_role_name = config['LEADER_ROLE']
        self._member_role_name = config['MEMBER_ROLE']

        self.keystone = client.Client(
            version=self._version,
            token=self._token,
            endpoint=self._endpoint)

    def _get_role(self, name):
        for role in self.keystone.roles.list():
            if role.name == name:
                return role

    def _member_role(self):
        return self._get_role(self._member_role_name)

    def _leader_role(self):
        return self._get_role(self._leader_role_name)

    ##########
    # PERSON #
    ##########

    def save_person(self, person):
        pass

    def delete_person(self, person):
        """Person was deleted."""
        return

    def set_person_password(self, person, raw_password):
        """Person's password was changed."""
        return

    def set_person_username(self, person, old_username, new_username):
        """Person's username was changed."""
        return

    def add_person_to_group(self, person, group):
        """Add person to group."""
        return

    def remove_person_from_group(self, person, group):
        """Remove person from group."""
        return

    def add_person_to_project(self, person, project):
        """Add person to project."""
        return

    def remove_person_from_project(self, person, project):
        """Remove person from project."""
        return

    def add_person_to_institute(self, person, institute):
        """Add person to institute."""
        return

    def remove_person_from_institute(self, person, institute):
        """Remove person from institute."""
        return

    def add_person_to_software(self, person, software):
        """Add person to software."""
        # this is a no-op, keystone doesn't support this
        return

    def remove_person_from_software(self, person, software):
        """Remove person from software."""
        # this is a no-op, keystone doesn't support this
        return

    def get_person_details(self, person):
        """Get person's details."""
        try:
            user = self.keystone.users.get(person.account.foreign_id)
        except exceptions.NotFound:
            return {}
        return user._info

    def person_exists(self, username):
        """Does the person exist?"""
        try:
            self.keystone.users.find(name=username)
        except exceptions.NotFound:
            return False
        return True


    ###########
    # ACCOUNT #
    ###########

    def edit_form(self, account):
        """Return the edit form for this account type."""
        from kgkeystone.forms import AccountDetails
        return AccountDetails(account)

    def save_account(self, account):
        """Account was saved."""
        person_data = account_to_os(account)
        if account.foreign_id:
            try:
                user = self.keystone.users.get(account.foreign_id)
            except exceptions.NotFound:
                logger.warning("User Not Found: %s" % person_data)
            else:
                logger.debug("Updating User: %s" % person_data)
                self.keystone.users.update(user, **person_data)
                return
        logger.debug("Creating User: %s" % person_data)
        self.keystone.users.create(**person_data)

    def delete_account(self, account):
        """Account was deleted."""
        user = self.keystone.users.get(account.foreign_id)
        logger.debug("Deleting User: %s" % user)
        self.keystone.users.delete(user)

    def set_account_password(self, account, raw_password):
        """Account's password was changed."""
        logger.debug("Backend doesn't support setting a password.")

    def set_account_username(self, account, old_username, new_username):
        """Account's username was changed."""
        user = self.keystone.users.get(account.foreign_id)
        logger.debug("Updating User's username: %s" % person_data)
        self.keystone.users.update(user, **person_to_os(person))

    def add_account_to_group(self, account, group):
        """Add account to group."""
        logger.debug("Backend doesn't support adding an account to a group.")

    def remove_account_from_group(self, account, group):
        """Remove account from group."""
        logger.debug("Backend doesn't support removing an account to a group.")

    def add_account_to_project(self, account, project):
        """Add account to project."""
        roles = [self._member_role()]
        if project.leaders.filter(id=account.person.id).exists():
            roles.append(self._leader_role())

        for role in roles:
            logger.info("Granting User %s role %s in %s" % (account, role, project))
            self.keystone.roles.grant(role, user=account.foreign_id,
                                      project=project.group.foreign_id)

    def remove_account_from_project(self, account, project):
        """Remove account from project."""
        roles = [self._member_role()]
        if project.leaders.filter(id=account.person.id).exists():
            roles.append(self._leader_role())

        for role in roles:
            logger.info("Revoking User %s role %s in %s" % (account, role, project))
            self.keystone.roles.revoke(role, user=account.foreign_id,
                                      project=project.group.foreign_id)

    def add_account_to_institute(self, account, institute):
        """Add account to institute."""
        return

    def remove_account_from_institute(self, account, institute):
        """Remove account from institute."""
        return

    def add_account_to_software(self, account, software):
        """Add account to software."""
        return

    def remove_account_from_software(self, account, software):
        """Remove account from software."""
        return

    def account_exists(self, username):
        """Does the account exist?"""
        for user in self.keystone.users.list():
            if user.name == username:
                return True
        return False

    def get_account_details(self, account):
        """Get the account details"""
        try:
            user = self.keystone.users.get(person.account.foreign_id)
        except exceptions.NotFound:
            logger.warning("Account Not Found: %s" % account)
            return {}
        return user._info


    #########
    # GROUP #
    #########

    def save_group(self, group):
        """Group was saved."""
        logger.debug("Backend doesn't support saving a group.")

    def delete_group(self, group):
        """Group was deleted."""
        logger.debug("Backend doesn't support deleting a group.")

    def set_group_name(self, group, old_name, new_name):
        """Group was renamed."""
        logger.debug("Backend doesn't support setting a group name.")

    def get_group_details(self, group):
        """Get the group details."""
        logger.debug("Backend doesn't support getting group details.")
        return {}


    ###########
    # PROJECT #
    ###########

    def add_leader_to_project(self, person, project):
        """Add account to project."""
        pass

    def remove_leader_from_project(self, person, project):
        """Remove account from project."""
        pass

    def save_project(self, project):
        """Project was saved."""
        project_data = project_to_os(project)
        if project.group.foreign_id:
            try:
                proj = self.keystone.projects.get(project.group.foreign_id)
            except exceptions.NotFound:
                logger.warning("Project Not Found: %s" % project_data)
            else:
                logger.debug("Updating project: %s" % project_data)
                self.keystone.projects.update(proj, **project_data)
                return
        logger.debug("Creating project: %s" % project_data)
        self.keystone.projects.create(**project_data)

    def delete_project(self, project):
        """Project was deleted."""
        try:
            proj = self.keystone.projects.get(project.group.foreign_id)
        except exceptions.NotFound:
            logger.warning("Project Not Found: %s" % project)
            return False
        logger.debug("Deleting project: %s" % project)
        self.keystone.projects.delete(proj)

    def get_project_details(self, project):
        """Get project's details."""
        try:
            project = self.keystone.projects.get(project.group.foreign_id)
        except exceptions.NotFound:
            logger.warning("Project Not Found: %s" % project)
            return {}
        return project._info


    #############
    # INSTITUTE #
    #############

    def save_institute(self, institute):
        """Institute was saved."""
        logger.debug("Backend doesn't support saving an institute.")

    def delete_institute(self, institute):
        """Institute was deleted."""
        logger.debug("Backend doesn't support deleting an institute.")

    def get_institute_details(self, institute):
        """Get institute's details."""
        logger.debug("Backend doesn't support getting institute details.")
        return {}


    ############
    # SOFTWARE #
    ############

    def save_software(self, software):
        """Software was saved."""
        logger.debug("Backend doesn't support saving software.")

    def delete_software(self, software):
        """Software was deleted."""
        logger.debug("Backend doesn't support deleting software.")

    def get_software_details(self, software):
        """Get software's details."""
        logger.debug("Backend doesn't support getting software details.")
        return {}