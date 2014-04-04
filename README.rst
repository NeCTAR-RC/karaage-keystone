Kgkeystone
==========

Add the following sippets to your global_setting.py file for karaage::

   INSTALLED_APPS = INSTALLED_APPS + ('kgkeystone', 'kgterms')

Example datastore configuration::

   DATASTORES['keystone'] =
        [{
            'DESCRIPTION': 'Keystone datastore',
            'ENGINE': 'kgkeystone.datastore.keystone.AccountDataStore',
            'VERSION': 'v3',
            'ENDPOINT': 'http://localhost:35357/v3/',
            'TOKEN': 'ADMIN',

            'LEADER_ROLE': 'TenantManager',
            'MEMBER_ROLE': 'Member',
        }]


Karaage should also be forced to use the crypt password hasher::

          
   PASSWORD_HASHERS = (
       'kgkeystone.hasher.SHA512CryptPasswordHasher',
   )



Running tests
=============

Install dependencies::

    apt-get install python-dev libldap2-dev libsasl2-dev libssl-dev python-matplot
    apt-get install keystone python-memcache
    apt-get install python-tox

Tox may need to be pip-installed on Ubuntu Precise.

Run tox::

    tox
