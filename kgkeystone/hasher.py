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

from django.contrib.auth import hashers
import passlib.hash

def django_to_passlib(password):
    # Convert Keystone style password to Django password.
    algr, round, salt, hash = password.split('$')
    passwd = "$6$rounds=%s$%s$%s" % (round, salt, hash.replace('+', '.').rstrip('='))
    return passwd

class SHA512CryptPasswordHasher(hashers.BasePasswordHasher):
    """
    The default passlib hashing
    """
    algorithm = "sha512_crypt"
    iterations = 40000

    def encode(self, password, salt):
        assert password
        assert salt and '$' not in salt
        hasher = passlib.hash.sha512_crypt(salt=salt, rounds=self.iterations)
        pwhash = hasher.encrypt(password)
        nul, nul, round, salt, hash = pwhash.split('$')
        iterations = round.split('=')[1]
        return "%s$%s$%s$%s" % (self.algorithm, iterations, salt, hash.replace('.', '+'))

    def verify(self, password, encoded):
        return passlib.hash.sha512_crypt.verify(
            password,
            django_to_passlib(encoded))

    def safe_summary(self, encoded):
        algorithm, salt, hash = encoded.split('$', 2)
        assert algorithm == self.algorithm
        return SortedDict([
            (_('algorithm'), algorithm),
            (_('salt'), mask_hash(salt, show=2)),
            (_('hash'), mask_hash(hash)),
        ])
