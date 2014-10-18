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


def percentage(a, b):
    if b > 0:
        return (str(round(a / b * 100, 1)) + '%') + ' (' + str(a) + '/' + str(b) + ');'
    else:
        return 0


def filter_approvals(approvals, emails, inverse=False):
    reviewers_in_emails = {}
    reviewers_not_in_emails = {}
    for a in approvals:
        # print(a, approvals)
        email = a['by']['email']
        if email in emails:
            if email not in reviewers_in_emails.keys():
                reviewers_in_emails[email] = list()
            reviewers_in_emails[email].append(a['value'])
        else:
            if email not in reviewers_not_in_emails.keys():
                reviewers_not_in_emails[email] = list()
            reviewers_not_in_emails[email].append(a['value'])

    if inverse:
        return reviewers_not_in_emails
    else:
        return reviewers_in_emails


def get_score_by(approvals, approvals_sum=False, score=None):
    summary = 0

    if approvals_sum:
        summary = approvals_sum
    else:
        for a in approvals.values():
            for i in a:
                if score:
                    if i == score:
                        summary += 1
                else:
                    summary += 1

    str_app = ''
    # print (r, lst2)
    if score:
        def scores_num(_lst, _score):
            scores_sum = 0
            for s in _lst:
                if s == _score:
                    scores_sum += 1
            return scores_sum

        for r, lst2 in sorted(approvals.items(), key=lambda x: scores_num(x[1], score), reverse=True):
            scores = scores_num(lst2, score)

            if scores > 0:
                str_app += ' ' + str(r) + ' ' + percentage(scores, summary)
                pass
    else:
        for r, lst2 in sorted(approvals.items(), key=lambda x: len(x[1]), reverse=True):
            str_app += ' ' + str(r) + ' ' + percentage(len(lst2), summary)
    return str_app


def count(num, lst):
    amount = 0
    for i in lst:
        if i == num:
            amount += 1
    return percentage(amount, len(lst))


def get_score(approvals, score):
    lst = []
    for a in approvals.values():
        for i in a:
            lst.append(i)
    str_app = ' => ' + '{:>2}'.format(str(score)) + ' : ' + '{:>4}'.format(count(str(score), lst))
    return str_app


def print_scores(prefix, approvals, approvals_sum=False):
    if approvals:
        scores_by = get_score_by(approvals, approvals_sum)
        # if prefix.find('code_reviews') != -1:
        # r_list = scores_by.split(';')
        # r_list = r_list[:-1]
        # if plot:
        #         for r in r_list:
        #             name, _, share = r.split()
        #             plot.append_reviewer((plot.get_username(name), str(share).strip('()').split('/')))
        #     pass
        print(prefix + scores_by)
        print_score("        showstopper", approvals, False, '-2')
        print_score("        don't like ", approvals, False, '-1')
        print_score("        looks good ", approvals, False, '1')
        print_score("        go-go-go   ", approvals, False, '2')


def print_score(prefix, approvals, approvals_sum=False, score='-2'):
    if approvals:
        score_str = get_score(approvals, score)
        if score_str.find(' 0.0%') < 0:
            print(prefix + get_score(approvals, score) + get_score_by(approvals, approvals_sum, score))


def print_patch_stats(merged_reviews=list(), abandoned_reviews=list()):
    def get_patchset_stats(reviews_list):
        review_patch_dict = {}
        for review in reviews_list:
            review_patch_dict.setdefault(len(review.patch_list), list()).append(review.id)
        return review_patch_dict

    patches_in_merged = 0
    patches_in_abandoned = 0

    for r in merged_reviews:
        patches_in_merged += len(r.patch_list)
    for r in abandoned_reviews:
        patches_in_abandoned += len(r.patch_list)

    total = patches_in_merged + patches_in_abandoned

    if total == 0:
        print("\nNo patchsets found")
        return

    print('\nPatch sets: {}, average: {} per review'.format
          (total, round(total / (len(merged_reviews) + len(abandoned_reviews)), 1)))

    if merged_reviews:
        patches_in_merged_dict = get_patchset_stats(merged_reviews)
        distribution = 'distribution: '
        for key, value in sorted(patches_in_merged_dict.items(), key=lambda x: len(x[1]), reverse=True):
            distribution += "{}:{}% ".format(key, round(len(value) / len(merged_reviews) * 100, 1))
        print('    in merged: {}, average: {} per review, {}'.format
              (patches_in_merged, round(patches_in_merged / len(merged_reviews), 1), distribution))

    if abandoned_reviews:
        patches_in_abandoned_dict = get_patchset_stats(abandoned_reviews)
        distribution = 'distribution: '
        for key, value in sorted(patches_in_abandoned_dict.items(), key=lambda x: len(x[1]), reverse=True):
            distribution += "{}:{}% ".format(key, round(len(value) / len(merged_reviews) * 100, 1))
        print('    in abandoned: {}, average: {} per review, {}'.format
              (patches_in_abandoned, round(patches_in_abandoned / len(abandoned_reviews), 1), distribution))

