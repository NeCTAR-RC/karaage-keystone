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

from django.db import models

class RCUser(models.Model):
    persistent_id = models.CharField(unique=True, max_length=250)
    displayname = models.CharField(max_length=250, blank=True)
    email = models.CharField(max_length=250, blank=True)
    terms = models.DateTimeField(blank=True, null=True)
    shibboleth_attributes = models.TextField(blank=True)
    id = models.IntegerField(primary_key=True)
    user_id = models.CharField(max_length=64, blank=True)
    state = models.CharField(max_length=10, blank=True)
    class Meta:
        managed = False
        db_table = 'user'
