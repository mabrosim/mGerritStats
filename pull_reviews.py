#!/usr/bin/python3

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

import json
import os
from subprocess import PIPE, Popen, TimeoutExpired
from collections import OrderedDict
from optparse import OptionParser

try:
    import params

    DAYS = params.DAYS
    QUERY_COMMON_PREFIX = params.QUERY_COMMON_PREFIX
    GERRIT_URL = params.GERRIT_URL
except ImportError:
    params = None
    DAYS = '14'
    GERRIT_URL = 'user@gerrit-review.example.com'
    QUERY_COMMON_PREFIX = 'ssh -p 29418 ' + GERRIT_URL + ' gerrit query --format=JSON --all-approvals'


def out_path(output_dir, fname):
    output_dir = os.path.join('out', output_dir)
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    return os.path.join(output_dir, fname + '.txt')


def ask_gerrit(query):
    proc = Popen(query.split(), stdout=PIPE)
    try:
        outs = proc.communicate(timeout=60)[0]
        return outs.decode().split('\n')[:-1]
    except TimeoutExpired:
        print("Communication timeout expired -> exit()")
        proc.kill()
        exit()


def pull_reviews(status):
    days = DAYS
    query = QUERY_COMMON_PREFIX + ' -- -age:' + days + 'd' + ' status:' + status

    json_strings = []
    query_init = query

    path = out_path('reviews', GERRIT_URL + '_' + str(days) + '_' + status)

    with open(path, "w", encoding='utf-8') as f:
        while query:
            print(query)
            raw = ask_gerrit(query)
            for review_json_str in raw:
                try:
                    json_object = json.loads(review_json_str, object_pairs_hook=OrderedDict)
                except ValueError:
                    print('Parse json error:' + review_json_str)
                    continue

                if 'type' not in json_object.keys():
                    json_strings.append(review_json_str)
                    f.write(review_json_str + '\n')
                else:
                    print(review_json_str)
                    if json_object['rowCount'] > 0:
                        # last but one item holds the sortkey
                        json_object = json.loads(raw[-2], object_pairs_hook=OrderedDict)
                    if 'sortKey' in json_object.keys():
                        query = query_init + ' resume_sortkey:' + json_object['sortKey']
                    else:
                        query = False
    return path


def cat_files(*files):
    fstr = ' '.join(files)
    cmd = 'cat ' + fstr + ' > ' + out_path('reviews', 'total_' + DAYS)
    os.system(cmd)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-d", "--days", dest="days", action="store",
                      help="query n days of data from gerrit server", metavar="n")
    parser.add_option("-L", "--url", dest="url", action="store",
                      help="specify gerrit server", metavar="URL")

    options, args = parser.parse_args()

    if options.days:
        DAYS = options.days
    if options.url:
        GERRIT_URL = options.url
        QUERY_COMMON_PREFIX = 'ssh -p 29418 ' + options.url + ' gerrit query --format=JSON --all-approvals'

    filepath_merged = ''
    filepath_abandoned = ''
    filepath_new = ''

    filepath_merged = pull_reviews('merged')
    # filepath_abandoned = pull_reviews('abandoned')
    # filepath_new = pull_reviews('new')
    cat_files(filepath_merged, filepath_abandoned, filepath_new)
    print("DONE!")
