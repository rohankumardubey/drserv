# Copyright (c) 2015 Spotify AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import os
import urlparse
from crtauth import ssh
from crtauth import client
import requests


def _authenticate(base_url, username, private_key_filename):

    with open(private_key_filename) as f:
        signer = ssh.SingleKeySigner(f.read())

    challenge = _auth_get(
        base_url, 'request:%s' % client.create_request(username))
    hostname = urlparse.urlparse(base_url).netloc
    if hostname.index(':') != -1:
        # netloc might contain port information as well
        hostname = hostname[:hostname.index(':')]
    response = client.create_response(challenge, hostname, signer)
    return _auth_get(base_url, 'response:' + response)


def _auth_get(base_url, value):
    response = requests.get("%s/_auth" % base_url,
                            headers={"X-CHAP": value})
    if not response.ok:
        raise Exception("Authentication request failed with status %d: %s"
                        % (response.status_code, response.text))
    return response.headers["X-CHAP"].split(":")[1]


def main():
    parser = argparse.ArgumentParser(
        'drserv-client',
        description='Deploy a package onto a drserv service'
    )
    parser.add_argument('--url', action='store', required=True,
                        help='the base url of the drserv service')

    parser.add_argument('--key-file', action='store',
                        help='the rsa private key used to authenticate')
    parser.add_argument('--auth-user', action='store',
                        help='the username to authenticate as')

    parser.add_argument('--major-dist', action='store', required=True)
    parser.add_argument('--minor-dist', action='store', required=True)
    parser.add_argument('--component', action='store', required=True)

    parser.add_argument('package_filename')

    args = parser.parse_args()
    token = _authenticate(args.url, args.auth_user, args.key_file)
    url = ('%s/v1/publish/%s/%s/%s/%s' %
           (args.url, args.major_dist, args.minor_dist, args.component,
            os.path.basename(args.package_filename)))
    with open(args.package_filename) as f:
        response = requests.post(url, data=f,
                                 headers={'Authorization': 'chap:' + token})
        if response.ok:
            print 'Upload succeeded'
        else:
            print 'Fail: %d: %s' % (response.status_code, response.text)


if __name__ == '__main__':
    main()