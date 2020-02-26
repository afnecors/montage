
from __future__ import print_function

import json
import urllib
import urlparse

from werkzeug.test import Client
from lithoxyl import DEBUG, INFO

from montage import utils
from montage.log import script_log
from montage.app import create_app


class ClasticTestClient(Client):
    def __init__(self, app):
        super(ClasticTestClient, self).__init__(app, app.response_type)


# TODO: could use clastic to route-match based on URL to determine
# "role" of current route being tested
class MontageTestClient(object):
    def __init__(self, app, default_role='public'):
        self.default_role = default_role
        self._test_client = ClasticTestClient(app)
        # TODO: default user?

    def fetch_url(self, url, data=None, act=None, **kw):
        # hyperlinkify url
        su_to = kw.get('su_to')
        if su_to:
            url_su_to = urllib.quote_plus(su_to.encode('utf8'))
            if '?' in url:
                url += '&su_to=' + url_su_to
            else:
                url += '?su_to=' + url_su_to
        if act:
            act['url'] = url
        c = self._test_client
        if data is None:
            res = c.get(url)
        else:
            res = c.post(url, data=data,
                         content_type=kw.get('content_type', 'application/json'))

        if res.status_code != 200:
            error_code = kw.get('error_code')
            if error_code and error_code == res.status_code:
                return res
            print('!! ', res.get_data())
            print()
            import pdb;pdb.set_trace()
            raise AssertionError('got error code %s when fetching %s' % (res.status_code, url))
        return res

    def fetch(self, role_action, url, data=None, **kw):
        if not url.startswith('/'):
            raise ValueError('expected url starting with "/", not: %r' % url)
        role, sep, action = role_action.partition(':')
        role, action = (role, action) if sep else (self.default_role, role)
        print('>>', action, 'as', role)
        as_user = kw.pop('as_user', None)
        if as_user:
            print('(%s)' % as_user)
        else:
            print()

        log_level = kw.pop('log_level', INFO)
        error_code = kw.pop('error_code', None)
        if kw:
            raise TypeError('unexpected kwargs: %r' % kw.keys())

        with script_log.action(log_level, 'fetch_url') as act:
            resp = self.fetch_url(url,
                                  data=data,
                                  su_to=as_user,
                                  error_code=error_code,
                                  act=act)
        # TODO: the following should be replaced with an internal
        # assert (along with the coupled status code check in
        # fetch_url)
        if error_code and resp is True:
            return True
        if resp.content_type != 'application/json':
            return resp
        data_dict = json.loads(resp.get_data())
        try:
            assert data_dict['status'] == 'success'
        except AssertionError:
            print('!! did not successfully load %s' % url)
            print('  got: ', data_dict)
            import pdb;pdb.set_trace()
        return data_dict


def _create_schema(db_url, echo=True):
    from sqlalchemy import create_engine
    from montage.rdb import Base

    engine = create_engine(db_url, echo=echo)
    Base.metadata.create_all(engine)

    return


def test_home_client():
    base_url = ''
    config = utils.load_env_config(env_name='devtest')
    db_url = config.get('db_url')
    _create_schema(db_url=db_url)

    app = create_app('devtest')

    client = MontageTestClient(app)
    client._test_client.set_cookie('', 'clastic_cookie', value=config['dev_local_cookie_value'], path='/')
    fetch = client.fetch

    fetch('organizer: home', '/')

    base_api_url = base_url + '/v1/'
    client = MontageTestClient(app)  # TODO
