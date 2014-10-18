"""
 Copyright (c) 2014, Maxim Abrosimov
 All rights reserved.

 Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

 1. Redistributions of source code must retain the above copyright notice,
 this list of conditions and the following disclaimer.

 2. Redistributions in binary form must reproduce the above copyright notice,
 this list of conditions and the following disclaimer in the documentation and/or other materials
 provided with the distribution.

 3. Neither the name of the copyright holder nor the names of its contributors may be used to
 endorse or promote products derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR
 IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
 FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
 OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
 OF SUCH DAMAGE.
"""

from datetime import datetime

import params


class Review(object):
    class Patch(object):
        def __init__(self, patch_js):
            self.number = patch_js['number']
            self.revision = patch_js['revision']
            self.ref = patch_js['ref']
            self.uploader = patch_js['uploader']
            self.createdOn = patch_js['createdOn']

            if "approvals" in patch_js.keys():
                self.approvals = patch_js['approvals']
            else:
                self.approvals = []

    def __init__(self, js):
        self.branch = js['branch']
        self.createdOn = js['createdOn']
        self.id = js['id']
        self.lastUpdated = js['lastUpdated']
        self.number = js['number']
        self.open = js['open']
        self.owner = js['owner']
        self.project = js['project']
        self.sortKey = js['sortKey']
        self.status = js['status']
        self.subject = js['subject']
        self.subm_date = None
        self.subm_isocalendar = None
        self.subm_week_of_year = None
        self.team_name = ''
        self.topic = ''
        self.url = js['url']

        if 'topic' in js.keys():
            self.topic = js['topic']

        self.patch_list = list()
        for patch_js in js['patchSets']:
            self.patch_list.append(self.Patch(patch_js))

        for p in self.patch_list:
            for a in p.approvals:
                if a['type'] == params.SUBMITTED:
                    self.subm_date = (datetime.fromtimestamp(a['grantedOn'])).date()
                    self.subm_isocalendar = (datetime.fromtimestamp(a['grantedOn'])).isocalendar()
                    self.subm_week_of_year = str(self.subm_isocalendar[0])[2:] + 'w' + str(self.subm_isocalendar[1])

        # some gerrit users like robots have no email, only username
        if 'email' not in self.owner.keys():
            if 'username' in self.owner.keys():
                self.owner['email'] = self.owner['username']
            else:
                self.owner['email'] = 'john_doe'
