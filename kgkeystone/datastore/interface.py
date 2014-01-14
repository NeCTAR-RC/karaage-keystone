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

from karaage.datastores import _get_all_names, _get_datastores_for_name


def add_leader_to_project(person, project):
    """Add person to institute."""
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            if hasattr(datastore, 'add_leader_to_project'):
                datastore.add_leader_to_project(person, institute)

def remove_leader_from_project(person, project):
    """Remove leader from project. """
    for name in _get_all_names():
        for datastore in _get_datastores_for_name(name):
            if hasattr(datastore, 'remove_leader_from_project'):
                datastore.remove_leader_from_project(person, institute)
