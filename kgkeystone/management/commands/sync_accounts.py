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

from datetime import datetime
from optparse import make_option
import cPickle
import pprint

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction, IntegrityError

from karaage.projects import models as proj_models
from karaage.people import models as peop_models
from karaage.institutes import models as inst_models
from karaage.machines import models as mach_models
from kgterms import models as terms_models
from kgkeystone import keystone_models
from kgkeystone import rcshib_models
from kgkeystone import models

IDP_MAPPING = {
    'https://aaf-login.uts.edu.au/idp/shibboleth': 'University of Technology, Sydney',
    'https://aaf.latrobe.edu.au/idp/shibboleth': 'La Trobe University',
    'https://aaf.unsw.edu.au/idp/shibboleth': 'The University of New South Wales',
    'https://aaf1-idp.its.utas.edu.au/idp/shibboleth': 'University of Tasmania',
    'https://federation.sydney.edu.au/idp/shibboleth': 'The University of Sydney',
    'https://fidp.usc.edu.au/idp/shibboleth': 'University of the Sunshine Coast',
    'https://idp-aaf.usq.edu.au/idp/shibboleth': 'The University of Southern Queensland',
    'https://idp.arcs.org.au/idp/shibboleth': 'Australian Research Collaboration Service',
    'https://idp.ballarat.edu.au/idp/shibboleth': 'The University of Ballarat',
    'https://idp.cc.swin.edu.au/idp/shibboleth': 'Swinburne University of Technology',
    'https://idp.cdu.edu.au/idp/shibboleth': 'Charles Darwin University',
    'https://idp.cqu.edu.au/idp/shibboleth': 'CQUniversity',
    'https://idp.flinders.edu.au/idp/shibboleth': 'Flinders University',
    'https://idp.murdoch.edu.au/idp/shibboleth': 'Murdoch University',
    'https://idp.newcastle.edu.au/idp/shibboleth': 'The University of Newcastle',
    'https://idp.qut.edu.au/idp/shibboleth': 'Queensland University of Technology',
    'https://idp.une.edu.au/idp/shibboleth': 'University of New England',
    'https://idp.uow.edu.au/idp/shibboleth': 'University of Wollongong',
    'https://idp.uws.edu.au/idp/shibboleth': 'University of Western Sydney',
    'https://idp2.anu.edu.au/idp/shibboleth': 'The Australian National University',
    'https://shib-idp.acu.edu.au/idp/shibboleth': 'Australian Catholic University',
    'https://shibboleth.aarnet.edu.au/idp/shibboleth': 'Australia\'s Academic and Research Network',
    'https://signon.deakin.edu.au/idp/shibboleth': 'Deakin University',
    'https://sso-shibboleth.rmit.edu.au/idp/shibboleth': 'RMIT University',
    'https://unisa.edu.au/idp/shibboleth': 'University of South Australia',
    'http://iam.auckland.ac.nz/idp': 'The University of Auckland',
    'https://idp.auckland.ac.nz/idp/shibboleth': 'The University of Auckland (Old)',
    'https://idp.aims.gov.au/idp/shibboleth': 'Australian Institute of Marine Science',
    'https://aafidp2.csiro.au/idp/shibboleth': 'The Commonwealth Scientific and Industrial Research Organisation',
    'https://shibidp.ecu.edu.au/idp/shibboleth': 'Edith Cowan University',
    'https://idpp1.curtin.edu.au/idp/shibboleth': 'Curtin University Australia',
    'https://idp1.griffith.edu.au/idp/shibboleth': 'Griffith University',
    'idp.fake.nectar.org.au': 'NeCTAR Test',
    'https://idp.intersect.org.au/idp/shibboleth': 'INTERSECT',
    'https://vho.aaf.edu.au/idp/shibboleth': 'Australian Access Federation VHO',
    'https://idp.monash.edu.au/idp/shibboleth': 'Monash University',
    'https://idp.jcu.edu.au/idp/shibboleth': 'James Cook University',
    'https://idp.sf.utas.edu.au/idp/shibboleth': 'Tasmanian Partnership for Advanced Computing',
    'https://idp.uwa.edu.au/idp/shibboleth': 'The University of Western Australia',
    'https://idp.unimelb.edu.au/idp/shibboleth': 'The University of Melbourne',
    'urn:mace:federation.org.au:testfed:au-idp.adelaide.edu.au': 'The University of Adelaide',
    'urn:mace:federation.org.au:testfed:mq.edu.au': 'Macquarie University',
    'urn:mace:federation.org.au:testfed:uq.edu.au': 'The University of Queensland',
    'https://idp.csu.edu.au/idp/shibboleth': 'Charles Sturt University',
    'https://idp.nicta.com.au/idp/shibboleth': 'NICTA',
    'https://idpweb1.vu.edu.au/idp/shibboleth': 'Victoria University',
    'https://idp.canberra.edu.au/idp/shibboleth': 'University of Canberra',
    'https://idp-prod.bond.edu.au/idp/shibboleth': 'Bond University',
    'https://idp.scu.edu.au/idp/shibboleth': 'Southern Cross University',
}

IDP_SHORTNAME_MAPPING = {
    'https://aaf-login.uts.edu.au/idp/shibboleth': 'uts',
    'https://aaf.latrobe.edu.au/idp/shibboleth': 'latrobe',
    'https://aaf.unsw.edu.au/idp/shibboleth': 'unsw',
    'https://aaf1-idp.its.utas.edu.au/idp/shibboleth': 'utas',
    'https://federation.sydney.edu.au/idp/shibboleth': 'sydney',
    'https://fidp.usc.edu.au/idp/shibboleth': 'usc',
    'https://idp-aaf.usq.edu.au/idp/shibboleth': 'usq',
    'https://idp.arcs.org.au/idp/shibboleth': 'arcs',
    'https://idp.ballarat.edu.au/idp/shibboleth': 'ballarat',
    'https://idp.cc.swin.edu.au/idp/shibboleth': 'swin',
    'https://idp.cdu.edu.au/idp/shibboleth': 'cdu',
    'https://idp.cqu.edu.au/idp/shibboleth': 'cqu',
    'https://idp.flinders.edu.au/idp/shibboleth': 'flinders',
    'https://idp.murdoch.edu.au/idp/shibboleth': 'murdoch',
    'https://idp.newcastle.edu.au/idp/shibboleth': 'newcastle',
    'https://idp.qut.edu.au/idp/shibboleth': 'qut',
    'https://idp.une.edu.au/idp/shibboleth': 'une',
    'https://idp.uow.edu.au/idp/shibboleth': 'uow',
    'https://idp.uws.edu.au/idp/shibboleth': 'uws',
    'https://idp2.anu.edu.au/idp/shibboleth': 'anu',
    'https://shib-idp.acu.edu.au/idp/shibboleth': 'acu',
    'https://shibboleth.aarnet.edu.au/idp/shibboleth': 'arrnet',
    'https://signon.deakin.edu.au/idp/shibboleth': 'deakin',
    'https://sso-shibboleth.rmit.edu.au/idp/shibboleth': 'rmit',
    'https://unisa.edu.au/idp/shibboleth': 'unisa',
    'https://idp.auckland.ac.nz/idp/shibboleth': 'auckland-old',
    'http://iam.auckland.ac.nz/idp': 'auckland',
    'https://idp.aims.gov.au/idp/shibboleth': 'aims',
    'https://aafidp2.csiro.au/idp/shibboleth': 'csiro',
    'https://shibidp.ecu.edu.au/idp/shibboleth': 'ecu',
    'https://idpp1.curtin.edu.au/idp/shibboleth': 'curtin',
    'https://idp1.griffith.edu.au/idp/shibboleth': 'griffith',
    'idp.fake.nectar.org.au': 'nectar-test',
    'https://idp.intersect.org.au/idp/shibboleth': 'intersect',
    'https://vho.aaf.edu.au/idp/shibboleth': 'aaf-vho',
    'https://idp.monash.edu.au/idp/shibboleth': 'monash',
    'https://idp.jcu.edu.au/idp/shibboleth': 'jcu',
    'https://idp.sf.utas.edu.au/idp/shibboleth': 'tpac',
    'https://idp.uwa.edu.au/idp/shibboleth': 'uwa',
    'https://idp.unimelb.edu.au/idp/shibboleth': 'unimelb',
    'urn:mace:federation.org.au:testfed:au-idp.adelaide.edu.au': 'adelaide',
    'urn:mace:federation.org.au:testfed:mq.edu.au': 'mq',
    'urn:mace:federation.org.au:testfed:uq.edu.au': 'uq',
    'https://idp.csu.edu.au/idp/shibboleth': 'csu',
    'https://idp.nicta.com.au/idp/shibboleth': 'nicta',
    'https://idpweb1.vu.edu.au/idp/shibboleth': 'vu',
    'https://idp.canberra.edu.au/idp/shibboleth': 'canberra',
    'https://idp-prod.bond.edu.au/idp/shibboleth': 'bond',
    'https://idp.scu.edu.au/idp/shibboleth': 'scu',
}

class MockRole(object):
    id = "unknown role"


def ks_to_django_passwd(password):
    # Convert Keystone style password to Django password.
    nul, nul, round, salt, hash = password.split('$')
    return "sha512_crypt$%s$%s$%s=" % (round.split('=')[1], salt,
                                       hash.replace('.', '+'))


class Command(BaseCommand):
    help = "Sync accounts from an existing keystone server."
    option_list = BaseCommand.option_list + (
        make_option('--rcshib_database',
                    dest='rcshib_database',
                    help='RCShibboleth DB to use'),
        make_option('--keystone_database',
                    dest='keystone_database',
                    help='Keystone DB to use'),
        )

    def handle(self, **options):
        verbose = int(options.get('verbosity', 0))
        rcshib_db = options.get('rcshib_database', None)
        keystone_db = options.get('keystone_database', None)
        if rcshib_db is None or keystone_db is None:
            if rcshib_db is None:
                print "--rcshib_database is required."
            if keystone_db is None:
                print "--keystone_database is required."
            return "Error"
        self.create_machine_category()
        self.sync_system_accounts(rcshib_db, keystone_db)
        # self.sync_users(rcshib_db, keystone_db)
        # self.sync_projects(keystone_db)
        # self.sync_permissions(keystone_db)

    def create_machine_category(self):
        self.mc, created = mach_models.MachineCategory.objects.get_or_create(
            name='Keystone',
            defaults={'datastore': 'keystone'})

    def project_members_by_role(self, keystone_db, project, role):
        try:
            krole = keystone_models.KRole.objects.using(keystone_db).get(name=role)
        except keystone_models.KRole.DoesNotExist:
            return
        for member in keystone_models.KUserProjectMetadata.objects.using(keystone_db)\
                                                                  .filter(project=project):
            for role in member.data.get('roles', {}):
                if role.get('id', None) == krole.id:
                    yield member

    def sync_system_accounts(self, rcshib_db, keystone_db):
        inst, created = inst_models.Institute.objects.get_or_create(name='NeCTAR')
        for k_user in keystone_models.KUser.objects.using(keystone_db).all():
            if rcshib_models.RCUser.objects.using(rcshib_db).filter(user_id=k_user.id).count() > 0:
                continue

            try:
                user = mach_models.Account.objects.get(foreign_id=k_user.id)
                if not user.person.is_systemuser:
                    continue
                user.person.username = k_user.name
                user.person.email = k_user.extra.get('email', None)
                user.person.password = ks_to_django_passwd(k_user.password)
                user.person.save()
            except mach_models.Account.DoesNotExist:
                username = k_user.name
                email = k_user.extra.get('email', None)
                person = peop_models.Person.objects.create(username=username,
                                                           short_name=username,
                                                           full_name=username,
                                                           email=email,
                                                           is_systemuser=True,
                                                           institute=inst,
                                                           password=k_user.password,
                                                           date_approved=datetime.now())
                user = mach_models.Account.objects.create(foreign_id=k_user.id,
                                                          date_created=datetime.now(),
                                                          machine_category=self.mc,
                                                          username=k_user.name,
                                                          person=person)

    def sync_projects(self, keystone_db):
        inst, created = inst_models.Institute.objects.get_or_create(name='NeCTAR')
        for k_project in keystone_models.KProject.objects.using(keystone_db).all():
            group, created = peop_models.Group.objects.get_or_create(
                name=k_project.name.lower(),
                defaults={'foreign_id': k_project.id,
                          'extra_data': {'keystone_name': k_project.name}})

            try:
                project = group.project_set.get()
            except proj_models.Project.DoesNotExist:
                pass
            else:
                continue
            # Use a project manager to get the institution.
            try:
                project_manager = self.project_members_by_role(
                    keystone_db, k_project, 'TenantManager').next()
            except StopIteration:
                try:
                    project_manager = self.project_members_by_role(
                        keystone_db, k_project, 'Member').next()
                except StopIteration:
                    group, created = peop_models.Group.objects.get_or_create(
                        name=k_project.name.lower(),
                        defaults={'foreign_id': k_project.id,
                                  'extra_data': {'keystone_name': k_project.name}})
                    project_data = {
                        'pid': k_project.name.lower(),
                        'institute': inst,
                        'group': group,
                        'description': k_project.description}
                    if not ('@' in k_project.name or 'pt-' in k_project.name):
                        project_data.update({'is_active': True,
                                             'date_approved': datetime.now()})

                    project, created = proj_models.Project.objects.get_or_create(
                        name=k_project.name,
                        defaults=project_data)
                    continue
            institute = mach_models.Account.objects.get(
                foreign_id=project_manager.user_id).person.institute
            project_data = {
                'pid': k_project.name.lower()[:50],
                'institute': institute,
                'is_active': True,
                'date_approved': datetime.now(),
                'group': group,
                'description': k_project.description}
            if k_project.name.startswith('pt-'):
                num = k_project.name.split('-')[1]
                project_data['name'] = 'Project trial %s' % num
                desc = k_project.description.strip(' personal tenancy.')
                project_data['description'] = '%s project trial.' % desc

            project, created = proj_models.Project.objects.get_or_create(
                name=k_project.name,
                defaults=project_data)

    def sync_users(self, rcshib_db, keystone_db):
        mc, created = mach_models.MachineCategory.objects.get_or_create(name='NeCTAR',
                                                               defaults={'datastore': 'dummy'})
        terms, created = terms_models.Terms.objects.get_or_create(title='Terms and Conditions',
                                                                  defaults={'machine': mc})

        for rc_user in rcshib_models.RCUser.objects.using(rcshib_db).all():
            try:
                shib_attrs = cPickle.loads(rc_user.shibboleth_attributes)
            except:
                print "User %s, never sent any shibboleth attributes." % rc_user.id
                continue
            if rc_user.state != 'created':
                print "User %s, never had an account created." % rc_user.id
                continue
            if not rc_user.user_id:
                print "User %s, never had an account created (and is in an invalid state)." % rc_user.id
                continue

            idp = shib_attrs.get('idp', None)
            try:
                institution = inst_models.Institute.objects.get(saml_entityid=idp)
                # NOTE: was used to updated existing institutes on
                # import but it slows down the import so it's not
                # being done anymore.

                # instition.name = IDP_MAPPING[idp]
                # instition.save()
                # instition.group.name = IDP_SHORTNAME_MAPPING[idp]
                # instition.group.description = IDP_MAPPING[idp]
                # instition.group.save()
            except inst_models.Institute.DoesNotExist:
                institution = inst_models.Institute.objects.create(
                    saml_entityid=idp,
                    name=IDP_MAPPING[idp])

            try:
                k_user = keystone_models.KUser.objects.using(keystone_db).get(id=rc_user.user_id)
            except:
                print "User %s, %s is missing from keystone." % (rc_user.id, rc_user.displayname)
                continue

            # Create the user
            user, person = self.create_user(rc_user, k_user, institution)

            # Add the terms and conditions if they don't exist
            aterms, created = terms_models.UserAgreed.objects.get_or_create(
                person=person, terms=terms, defaults={'when': rc_user.terms})

    def sync_permissions(self, keystone_db):
        # TODO this should use the value from the config file.
        member = keystone_models.KRole.objects.using(keystone_db).get(name='Member')
        try:
            manager = keystone_models.KRole.objects.using(keystone_db).get(name='TenantManager')
        except keystone_models.KRole.DoesNotExist:
            manager = MockRole()

        for permission in keystone_models.KUserProjectMetadata.objects.using(keystone_db).all():
            try:
                account = mach_models.Account.objects.get(foreign_id=permission.user_id)
            except models.User.DoesNotExist:
                print "skipping user permission %s" % permission.user_id
                continue

            try:
                group = peop_models.Group.objects.get(foreign_id=permission.project.id)
            except models.Project.DoesNotExist:
                print "skipping project permission %s" % permission.project.id
                continue
            for role in permission.data['roles']:
                role_id = role['id']
                if role_id == member.id:
                    group.members.add(account.person)
                elif role_id == manager.id:
                    group.project_set.get().leaders.add(account.person)


    def create_user(self, rc_user, k_user, institution):
        try:
            user = mach_models.Account.objects.get(foreign_id=rc_user.user_id)
            person = user.person
        except mach_models.Account.DoesNotExist:
            # Base username on Keystone username
            username = k_user.name
            shortname = rc_user.displayname.split(' ')[0]
            person = peop_models.Person.objects.create(username=username,
                                                       short_name=shortname,
                                                       full_name=rc_user.displayname,
                                                       email=rc_user.email,
                                                       institute=institution,
                                                       password=k_user.password,
                                                       saml_id=rc_user.persistent_id,
                                                       date_approved=rc_user.terms)
            user = mach_models.Account.objects.create(foreign_id=rc_user.user_id,
                                                      username=rc_user.email,
                                                      machine_category=self.mc,
                                                      date_created=rc_user.terms,
                                                      person=person)
        return user, person

    def trunc_username(self, username):
        if len(username) > 30:
            return username[:30]
        return username

    def unique_username(self, username, count=0):
        while True:
            u = username + str(count) if count > 0 else username

            try:
                peop_models.Person.objects.get(username=u)
                return self.unique_username(username, count + 1)
            except peop_models.Person.DoesNotExist:
                return u
