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
import os
import shutil
import socket
import string
import subprocess
import tempfile
import time
import urllib2
from StringIO import StringIO
from os import path

from django.test import TestCase
import karaage.datastores  # NOQA: prevent circular import

from kgkeystone.datastore.keystone import (MachineCategoryDataStore,
                                           GlobalDataStore)


LOG = logging.getLogger("kgkeystone.test.keystone")
BASE_PATH = path.dirname(__file__)


def which(name, flags=os.X_OK):
    result = []
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return []
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            result.append(p)
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                result.append(pext)
    return result


def is_port_open(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', int(port)))
    if result == 0:
        return True
    return False


class Keystone():
    public_port = '10334'
    admin_port = '10335'

    def __init__(self):

        if is_port_open(self.public_port):
            raise Exception('Port %s is already in use' % self.public_port)
        if is_port_open(self.admin_port):
            raise Exception('Port %s is already in use' % self.admin_port)
        self.base_dir = tempfile.mkdtemp()
        self.config_dir = path.join(self.base_dir, 'config')
        os.mkdir(self.config_dir)
        self.working_dir = path.join(self.base_dir, 'working')
        os.mkdir(self.working_dir)
        self.log_dir = path.join(self.base_dir, 'log')
        os.mkdir(self.log_dir)
        self.output = StringIO()

        self._copy_config()
        self._write_config()

    def _cleanup(self):
        shutil.rmtree(self.base_dir)

    def _copy_config(self):
        source_path = path.join(BASE_PATH, 'config')
        for filename in os.listdir(source_path):
            abs_name = path.join(source_path, filename)
            shutil.copyfile(abs_name, path.join(self.config_dir, filename))

    def _write_config(self):
        tmpl_filename = path.join(BASE_PATH, 'config', 'keystone.conf')
        tmpl = string.Template(open(tmpl_filename).read())
        fd = open(path.join(self.config_dir, 'keystone.conf'), "w")
        fd.write(tmpl.substitute(config_dir=self.config_dir,
                                 log_dir=self.log_dir,
                                 working_dir=self.working_dir,
                                 public_port=self.public_port,
                                 admin_port=self.admin_port))

    def _wait_to_start(self):
        count = 0
        while True:
            try:
                urllib2.urlopen('http://127.0.0.1:10335/v3/')
                break
            except urllib2.URLError:
                if count > 10:
                    raise
            count += 1
            time.sleep(0.2)

    def start(self):
        LOG.info('starting Keystone')

        FNULL = open(os.devnull, 'w')
        command = [
            which('keystone-manage')[0],
            '--config-dir',
            self.config_dir,
            'db_sync',
        ]
        LOG.debug('Creating Keystone DB: %s', ' '.join(command))
        proc = subprocess.Popen(command, stdout=FNULL, stderr=FNULL)
        out, err = proc.communicate()
        if proc.returncode != 0:
            print out
            print err
            self._cleanup()
            raise Exception('Failed to run db_sync')

        command = [which('keystone-all')[0], '--config-dir', self.config_dir]
        LOG.debug('Starting Keystone: %s', ' '.join(command))
        try:
            self._process = subprocess.Popen(command,
                                             stdout=FNULL, stderr=FNULL)
            self._wait_to_start()
        except:
            self.stop()
            raise
        LOG.info('Keystone running')

    def stop(self):
        if self._process is not None:
            LOG.debug("stopping Keystone")
            self._process.terminate()
            self._process.wait()
            if self._process.returncode is None:
                self._process.kill()
            self._cleanup()


KEYSTONE_CONFIG = {
    'DESCRIPTION': 'Keystone datastore',
    'ENGINE': 'kgkeystone.datastore.keystone.AccountDataStore',
    'VERSION': 'v3',
    'ENDPOINT': 'http://127.0.0.1:10335/v3/',
    'TOKEN': 'ADMIN',

    'LEADER_ROLE': 'TenantManager',
    'MEMBER_ROLE': 'Member',

    'HOST': '127.0.0.1',
    'PORT': '10335',
    'PROTOCOL': 'http',
    'PROJECT_NAME': 'admin',
    'USERNAME': 'karaage',
    'PASSWORD': 'test',
}


class IntegrationTestCase(TestCase):
    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.keystone = Keystone()
        self.keystone.start()
        self.mc_datastore = MachineCategoryDataStore(KEYSTONE_CONFIG)
        self.g_datastore = GlobalDataStore(KEYSTONE_CONFIG)
        self.keystone_client = self.mc_datastore.keystone
        config = KEYSTONE_CONFIG
        self._endpoint = config['ENDPOINT']
        self._token = config['TOKEN']
        self._version = config.get('VERSION', None)
        self._leader_role_name = config['LEADER_ROLE']
        self._member_role_name = config['MEMBER_ROLE']

    def tearDown(self):
        super(IntegrationTestCase, self).tearDown()
        self.keystone.stop()
