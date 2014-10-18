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

from models.utils import percentage
import params


class Reviewer(object):
    def __init__(self, email):
        self.avg_review_time = 0
        self.branches = {}
        self.code_review = []
        self.content_check = []
        self.email = email
        self.ignored_ids = []
        self.manual_testing = []
        self.projects = {}
        self.project_list = []
        self.query = ''
        self.review_times_lst = []
        self.reviewed_owners = {}
        self.reviewed_ids = []
        self.submitted = []
        self.team = ''
        self.verify = []

    def fetch_data(self, reviews_list):
        for r in reviews_list:
            ignored = True
            for patch in r.patch_list:
                for approval in patch.approvals:
                    if 'email' in approval['by']:
                        if approval['by']['email'] == self.email and approval['type'] != params.SUBMITTED:
                            ignored = False
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

                            delta = approval['grantedOn'] - patch.createdOn
                            if delta < 0:
                                pass
                            else:
                                self.review_times_lst.append(delta)
            if ignored:
                self.ignored_ids.append(r.id)
            else:
                self.reviewed_ids.append(r.id)
                if r.project not in self.project_list:
                    self.project_list.append(r.project)
                self.projects.setdefault(r.project, list()).append(r.id)
                self.reviewed_owners.setdefault(r.owner['email'], list()).append(r.id)
                self.branches.setdefault(r.project + ' ' + r.branch, list()).append(r.id)

    def print_review_count(self):
        reviewed = len(self.reviewed_ids)
        ignored = len(self.ignored_ids)
        total = reviewed + ignored
        if total:
            print("reviewed : {} ({}%) + ignored: {} ({}%) = {}"
                  .format(reviewed, floor(reviewed / total * 100), ignored, floor(ignored / total * 100), total))

    def print_reviews_scores(self):
        def count(num, lst):
            amount = 0
            for a in lst:
                if a['value'] == num:
                    amount += 1
            return percentage(amount, len(lst))

        def get_scores(l):
            return count('-2', l), count('-1', l), count('1', l), count('2', l)

        print("review scores:")

        if len(self.code_review):
            scores = get_scores(self.code_review)
            print("{:>15}:{:>8} => -2: {} -1: {} 1: {} 2: {}"
                  .format('code_review', (len(self.code_review)), scores[0], scores[1], scores[2], scores[3]))

        if len(self.content_check):
            scores = get_scores(self.content_check)
            print("{:>17}: {:>5} => -1: {} 1: {}"
                  .format('content_check', (len(self.content_check)), scores[1], scores[2]))

        if len(self.verify):
            scores = get_scores(self.verify)
            print("{:>10}: {:>12} => -1: {} 1: {}"
                  .format('verify', (len(self.verify)), scores[1], scores[2]))

        if len(self.manual_testing):
            scores = get_scores(self.manual_testing)
            print("{:>18}: {:>4} => -1: {} 1: {}"
                  .format('manual_testing', (len(self.manual_testing)), scores[1], scores[2]))

    def print_ignored_reviews_info(self):
        if len(self.reviewed_ids):
            ignored = len(self.ignored_ids)
            total = len(self.reviewed_ids) + ignored
            print("\nIgnored reviews:  {} ({}%) out of total {} where added as reviewer"
                  .format(ignored, floor(ignored) / total * 100, total))

    def print_average_review_time(self):
        if self.review_times_lst:
            # heuristic normalization of distribution, cut the min/max 3% at edges
            # formula: sum of patch approval times (approval score timestamp - patch creation time) divided by reviews
            # amount
            cut_the_edge = round(len(self.review_times_lst) * 0.03)
            if cut_the_edge:
                new_list = sorted(self.review_times_lst)[cut_the_edge: -cut_the_edge]
            else:
                new_list = self.review_times_lst
            self.avg_review_time = int(sum(new_list) / len(new_list))

            print("\nAverage review time is {} hours, the distribution of times is normalised"
                  .format(round(self.avg_review_time / 3600)))

    def print_project_branch_stats(self):
        print("\nProjects {}, reviews {}".format(len(self.projects), len(self.reviewed_ids)))
        for p, lst in sorted(self.projects.items(), key=lambda x: len(x[1]), reverse=True):
            print("    " + p + ": " + str(len(lst)))

        print("\nBranches {}, reviews {}".format(len(self.branches), len(self.reviewed_ids)))
        for b, lst in sorted(self.branches.items(), key=lambda x: len(x[1]), reverse=True):
            print("    {}: {} ({}%)".format(b, len(lst), floor(len(lst) / len(self.reviewed_ids) * 100)))

    def print_reviewed_owners(self):
        print("\nReviewed owners", len(self.reviewed_owners))
        for e, lst in sorted(self.reviewed_owners.items(), key=lambda x: len(x[1]), reverse=True):
            print("    {}: {} ({}%)".
                  format(e, len(lst), floor(len(lst) / len(self.reviewed_ids) * 100)))

    def gerrit_query(self, prefix, days):
        self.query = "{0} reviewer:{1} -- -age:{2}d -owner:{1}".format(prefix, self.email, days)

    def print(self):
        header = "Reviewer: {}".format(self.email)
        print("\n" + header + "\n" + str(len(header) * '='))
        self.print_review_count()
        self.print_reviews_scores()
        self.print_ignored_reviews_info()
        self.print_average_review_time()
        self.print_project_branch_stats()
        self.print_reviewed_owners()
        print("\n")
