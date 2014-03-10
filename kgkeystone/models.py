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

import logging

from django.db import models

from karaage.people.models import _add_person_to_group, _remove_person_from_group
from karaage.projects import models as proj_models

logger = logging.getLogger('kgkeystone.datastore')

def _leaders_changed(sender, instance, action, reverse, model, pk_set, **kwargs):
    if action == "post_add":
        if not reverse:
            group = instance.group
            for person in model.objects.filter(pk__in=pk_set):
                logger.debug("Added leader %s to project %s" % (person, group))
                _add_person_to_group(person, group)
        else:
            person = instance
            for group  in model.objects.filter(pk__in=pk_set):
                logger.debug("Added leader %s to group  %s" % (person, group))
                _add_person_to_group(person, group)
    elif action == "post_remove":
        if not reverse:
            group = instance.group
            for person in model.objects.filter(pk__in=pk_set):
                logger.debug("Removed leader %s from group  %s" % (person, group))
                _remove_person_from_group(person, group)
        else:
            person = instance
            for group  in model.objects.filter(pk__in=pk_set):
                logger.debug("Removed leader %s from group  %s" % (person, group))
                _remove_person_from_group(person, group)
    elif action == "pre_clear":
        if not reverse:
            group = instance
            for person in group.members.all():
                logger.debug("Removed leader %s from group  %s" % (person, group))
                _remove_person_from_group(person, group)
        else:
            group = instance
            for group  in person.groups.all():
                logger.debug("Removed leader %s from group  %s" % (person, group))
                _remove_person_from_group(person, group)

models.signals.m2m_changed.connect(_leaders_changed, sender=proj_models.Project.leaders.through)


class ProjectRenamed(models.Model):
    project = models.ForeignKey(proj_models.Project, related_name='has_been_renamed')
    renamed = models.BooleanField(default=False)
