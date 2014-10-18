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

from math import floor

from models.utils import print_scores, filter_approvals, print_patch_stats
import params


class Owner(object):
    def __init__(self, email):
        self.email = email
        self.query = ''
        self.team = ''
        self.code_review = []
        self.content_check = []
        self.verify = []
        self.submitted = []
        self.manual_testing = []
        self.projects = {}
        self.branches = {}
        self.reviewer_list = []
        self.merged_reviews = []
        self.abandoned_reviews = []

    def fetch_data(self, reviews_list):
        for r in reviews_list:
            if r.status == 'MERGED':
                self.merged_reviews.append(r)

                for patch in r.patch_list:
                    for approval in patch.approvals:
                        # print(approval)
                        if 'email' in approval['by']:
                            if approval['by']['email'] not in self.reviewer_list:
                                self.reviewer_list.append(approval['by']['email'])
                            if approval['type'] == params.CODE_REVIEW:
                                self.code_review.append(approval)
                            elif approval['type'] == params.CONTENT_CHECK:
                                self.content_check.append(approval)
                            elif approval['type'] == params.VERIFIED:
                                self.verify.append(approval)
                            elif approval['type'] == params.SUBMITTED:
                                self.submitted.append(approval)
                            elif approval['type'] == params.MANUAL_TESTING:
                                self.manual_testing.append(approval)

                self.projects.setdefault(r.project, list()).append(r.id)
                self.branches.setdefault(r.project + ' ' + r.branch, list()).append(r.id)

            elif r.status == 'ABANDONED':
                self.abandoned_reviews.append(r)

    def print_project_branch_stats(self):
        print("\nProjects in merged " + str(len(self.projects)))
        for p, lst in sorted(self.projects.items(), key=lambda x: len(x[1]), reverse=True):
            print("    " + p + ": " + str(len(lst)))

        print("\nBranches in merged " + str(len(self.branches)))
        for b, lst in sorted(self.branches.items(), key=lambda x: len(x[1]), reverse=True):
            print("    " + b + ": " + str(len(lst)), '(' + str(floor(
                len(lst) / len(self.merged_reviews) * 100)) + '%)')

    def print_approval_scores(self):
        humans_filter = list(params.ROBOTS)
        humans_filter.append(self.email)
        # print(ROBOTS.append(self.email))
        humans_crw = filter_approvals(self.code_review, humans_filter, inverse=True)
        humans_c = filter_approvals(self.content_check, humans_filter, inverse=True)
        humans_v = filter_approvals(self.verify, humans_filter, inverse=True)
        humans_t = filter_approvals(self.manual_testing, humans_filter, inverse=True)
        humans_s = filter_approvals(self.submitted, humans_filter, inverse=True)

        humans = []
        for d in (humans_crw, humans_t):
            for email in d.keys():
                if email not in humans and email != self.email:
                    humans.append(email)

        print("\nHuman reviewers " + str(len(humans)))
        print_scores("    code_reviews:" + ' ' * 4, humans_crw)
        print_scores("    content_checks:" + ' ' * 2, humans_c)
        print_scores("    verify:" + ' ' * 10, humans_v, len(self.verify))
        print_scores("    manual_testing:" + ' ' * 2, humans_t)
        print_scores("    submitted:" + ' ' * 7, humans_s)

        self_crw = filter_approvals(self.code_review, self.email)
        self_c = filter_approvals(self.content_check, self.email)
        self_v = filter_approvals(self.verify, self.email)
        self_t = filter_approvals(self.manual_testing, self.email)
        self_s = filter_approvals(self.submitted, self.email)

        print("\nSelf ")
        print_scores("    code_reviews:" + ' ' * 4, self_crw, len(self.code_review))
        print_scores("    content_checks:" + ' ' * 2, self_c, len(self.content_check))
        print_scores("    verify:" + ' ' * 10, self_v, len(self.verify))
        print_scores("    manual_testing:" + ' ' * 2, self_t, len(self.manual_testing))
        print_scores("    submitted:" + ' ' * 7, self_s, len(self.submitted))

        robots_crw = filter_approvals(self.code_review, params.ROBOTS)
        robots_c = filter_approvals(self.content_check, params.ROBOTS)
        robots_v = filter_approvals(self.verify, params.ROBOTS)
        robots_t = filter_approvals(self.manual_testing, params.ROBOTS)
        robots_s = filter_approvals(self.submitted, params.ROBOTS)

        print("\nRobots ")
        print_scores("    code_reviews:" + ' ' * 4, robots_crw)
        print_scores("    content_checks:" + ' ' * 2, robots_c)
        print_scores("    verify:" + ' ' * 10, robots_v, len(self.verify))
        print_scores("    manual_testing:" + ' ' * 2, robots_t)
        print_scores("    submitted:" + ' ' * 7, robots_s)

    def print_review_count(self):
        merged = len(self.merged_reviews)
        abandoned = len(self.abandoned_reviews)
        total = merged + abandoned
        if total:
            print("\nMerged reviews:", merged, "(" + str(floor(merged / total * 100)) + "%)", "+ abandoned:",
                  abandoned, "(" + str(floor(abandoned / total * 100)) + "%)", "=", total, )

    def gerrit_query(self, prefix, days):
        self.query = "{} owner:{} -- -age:{}d".format(prefix, self.email, days)

    def print(self):
        header = "Owner: {}".format(self.email)
        print("\n" + header + "\n" + str(len(header) * '='))
        self.print_review_count()
        print_patch_stats(self.merged_reviews, self.abandoned_reviews)
        self.print_project_branch_stats()
        self.print_approval_scores()
        print("\n")
