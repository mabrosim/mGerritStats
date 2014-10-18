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
from os import path
from optparse import OptionParser

from models.utils import print_patch_stats
import params
from models.owner import Owner
from models.reviewer import Reviewer
from models.review import Review
from models.team import Team


def read_from_file(filename):
    with open(filename, "r", encoding='utf-8') as f:
        review_list = f.readlines()
    return review_list


def get_reviews_from_file(filename):
    def heuristic_filter(r):
        def review_filter(key, filters, custom_type=0):
            if custom_type == 0:
                if key in filters:
                    return False
            elif custom_type == 1:
                for t in params.TOPIC_FILTER:
                    if key.find(t) >= 0:
                        return False
            elif custom_type == 2:
                if key.find('Merge remote-tracking branch') != -1:
                    return False
            return True

        return \
            review_filter(r.subject, None, custom_type=2) and \
            review_filter(r.branch, params.BRANCH_FILTER) and \
            review_filter(r.project, params.PROJECT_FILTER) and \
            review_filter(r.topic, params.TOPIC_FILTER, custom_type=1) and \
            review_filter(r.owner['email'], params.EMAIL_FILTER)

    return {review.id: review for review in
            filter(heuristic_filter, map(lambda r: Review(json.loads(r)),
                                         read_from_file(filename)))}


def reviewer_stats(email, reviews):
    def reviewer_filter(patch_list):
        for p in patch_list:
            for a in p.approvals:
                if 'email' in a['by'].keys():
                    if a['by']['email'] == email:
                        return True
        return False

    reviewer = Reviewer(email)
    reviewer.fetch_data(list(filter(lambda r: reviewer_filter(r.patch_list), reviews.values())))
    reviewer.gerrit_query(params.QUERY_COMMON_PREFIX, params.DAYS)
    return reviewer


def owner_stats(email, reviews):
    owner = Owner(email)
    owner.fetch_data(list(filter(lambda r: r.owner['email'] == email, reviews.values())))
    owner.gerrit_query(params.QUERY_COMMON_PREFIX, params.DAYS)
    return owner


def team_stats(_name, team_emails, reviews):
    def team_filter(r):
        if r.owner['email'] in team_emails:
            r.team_name = _name
            return True
        return False

    team = Team(_name, team_emails)
    team.fetch_data(list(filter(lambda r: team_filter(r), reviews.values())))
    return team


def all_stats(reviews):
    team = Team('all', list())
    team.fetch_data(reviews.values())
    team.print()


def parser_options():
    parser = OptionParser()
    parser.add_option("-R", "--Reviewers", dest="reviewers", action="append",
                      help="reviewers list", metavar="REVIEWERS")
    parser.add_option("-O", "--Owners", dest="owners", action="append",
                      help="owners list", metavar="OWNERS")
    parser.add_option("-T", "--Teams", dest="teams", action="append",
                      help="teams list", metavar="TEAMS")
    parser.add_option("-d", "--days", dest="days",
                      help="fetch n days of data", metavar="DAYS")
    parser.add_option("-f", "--file", dest="file",
                      help="data file path", metavar="FILE")

    options, args = parser.parse_args()

    if options.days:
        params.DAYS = options.days
    if options.owners:
        params.OWNERS = options.owners
    if options.reviewers:
        params.REVIEWERS = options.reviewers
    if options.teams:
        params.TEAMS = options.teams
    return options


def main():
    options = parser_options()
    if options.file:
        file = options.file
    else:
        file = path.join('out', 'reviews', 'total_' + params.DAYS + '.txt')

    reviews_dict = get_reviews_from_file(file)

    print_patch_stats(list(filter(lambda review: review.status == 'MERGED', reviews_dict.values())),
                      list(filter(lambda review: review.status == 'ABANDONED', reviews_dict.values())))

    # all_stats(reviews_dict)
    # exit()

    owners = []
    for email in params.OWNERS:
        owners.append(owner_stats(email, reviews_dict))
        pass

    reviewers = []
    for email in params.REVIEWERS:
        reviewers.append(reviewer_stats(email, reviews_dict))
        pass

    teams = []
    for name, emails in params.TEAMS.items():
        teams.append(team_stats(name, emails, reviews_dict))
        pass

    for o in owners:
        o.print()
        pass
    for r in reviewers:
        r.print()
        pass
    for t in teams:
        t.print()
        pass


if __name__ == '__main__':
    main()
