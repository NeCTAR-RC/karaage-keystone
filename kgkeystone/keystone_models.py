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

from json_field import JSONField


class KCredential(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    user_id = models.CharField(max_length=64L)
    project_id = models.CharField(max_length=64L, blank=True)
    blob = models.TextField()
    type = models.CharField(max_length=255L)
    extra = JSONField()
    class Meta:
        db_table = 'credential'

class KDomain(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    name = models.CharField(max_length=64L, unique=True)
    enabled = models.IntegerField()
    extra = JSONField()
    class Meta:
        db_table = 'domain'

class KEndpoint(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    legacy_endpoint_id = models.CharField(max_length=64L, blank=True)
    interface = models.CharField(max_length=8L)
    region = models.CharField(max_length=255L, blank=True)
    service = models.ForeignKey('KService')
    url = models.TextField()
    extra = JSONField()
    class Meta:
        db_table = 'endpoint'

class KGroup(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    domain = models.ForeignKey(KDomain)
    name = models.CharField(max_length=64L)
    description = models.TextField(blank=True)
    extra = models.TextField(blank=True)
    class Meta:
        db_table = 'group'

class KGroupDomainMetadata(models.Model):
    group_id = models.CharField(max_length=64L)
    domain = models.ForeignKey(KDomain)
    data = JSONField()
    class Meta:
        db_table = 'group_domain_metadata'

class KGroupProjectMetadata(models.Model):
    group_id = models.CharField(max_length=64L)
    project = models.ForeignKey('KProject')
    data = JSONField()
    class Meta:
        db_table = 'group_project_metadata'

class KMigrateVersion(models.Model):
    repository_id = models.CharField(max_length=250L, primary_key=True)
    repository_path = models.TextField(blank=True)
    version = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'migrate_version'

class KPolicy(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    type = models.CharField(max_length=255L)
    blob = models.TextField()
    extra = JSONField()
    class Meta:
        db_table = 'policy'

class KProject(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    name = models.CharField(max_length=64L)
    extra = JSONField()
    description = models.TextField(blank=True)
    enabled = models.IntegerField(null=True, blank=True)
    domain = models.ForeignKey(KDomain)
    class Meta:
        db_table = 'project'

class KRole(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    name = models.CharField(max_length=255L, unique=True, blank=True)
    extra = JSONField()
    class Meta:
        db_table = 'role'

class KService(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    type = models.CharField(max_length=255L, blank=True)
    extra = JSONField()
    class Meta:
        db_table = 'service'

class KToken(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    expires = models.DateTimeField(null=True, blank=True)
    extra = JSONField()
    valid = models.IntegerField()
    trust_id = models.CharField(max_length=64L, blank=True)
    user_id = models.CharField(max_length=64L, blank=True)
    class Meta:
        db_table = 'token'

class KTrust(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    trustor_user_id = models.CharField(max_length=64L)
    trustee_user_id = models.CharField(max_length=64L)
    project_id = models.CharField(max_length=64L, blank=True)
    impersonation = models.IntegerField()
    deleted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    extra = JSONField()
    class Meta:
        db_table = 'trust'

class KTrustRole(models.Model):
    trust_id = models.CharField(max_length=64L)
    role_id = models.CharField(max_length=64L)
    class Meta:
        db_table = 'trust_role'

class KUser(models.Model):
    id = models.CharField(max_length=64L, primary_key=True)
    name = models.CharField(max_length=255L)
    extra = JSONField()
    password = models.CharField(max_length=128L, blank=True)
    enabled = models.IntegerField(null=True, blank=True)
    domain = models.ForeignKey(KDomain)
    default_project_id = models.CharField(max_length=64L, blank=True)
    class Meta:
        db_table = 'user'

class KUserDomainMetadata(models.Model):
    user_id = models.CharField(max_length=64L, primary_key=True)
    domain = models.ForeignKey(KDomain, primary_key=True)
    data = JSONField()
    class Meta:
        db_table = 'user_domain_metadata'

class KUserGroupMembership(models.Model):
    user = models.ForeignKey(KUser, primary_key=True)
    group = models.ForeignKey(KGroup, primary_key=True)
    class Meta:
        db_table = 'user_group_membership'

class KUserProjectMetadata(models.Model):
    user_id = models.CharField(max_length=64L, primary_key=True)
    project = models.ForeignKey(KProject, primary_key=True)
    data = JSONField()
    class Meta:
        db_table = 'user_project_metadata'
