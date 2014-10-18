mGerritStats
============

**mGerritStats is a collection of scripts written in Python3,<br>which helps to sort out, analyze and visualize [Gerrit] data off-line.**

* the scripts:
   * pull_reviews.py - Download data from gerrit server for off-line processing <br>
   * gerrit_stats.py - Read data from json file and print various statistics for **owners**, **reviewers**, **teams**
   * ...


<br>

##### Sample output for Team of gerrit users
```
Team: Team1
===========
merged reviews: 1253 (100%) + abandoned: 0 (0%) = 1253

Patch sets: 2330, average: 1.9 per review
    in merged: 2330, average: 1.9 per review, distribution: 1:52.8% 2:26.0% 3:12.3% 4:4.5% 5:2.5% 6:0.9% 7:0.5% 8:0.2% 10:0.2% 11:0.2% 9:0.1%

Reviewers 87
    code_reviews:     maxim.abrosimov@host 44.8% (1198/2673); username1@host 15.5% (415/2673); ...
        showstopper => -2 : 0.2% (5/2673); maxim.abrosimov@host 40.0% (2/5); username14@host 40.0% (2/5); ...
        don't like  => -1 : 3.2% (86/2673); username1@host 31.4% (27/86); maxim.abrosimov@host 30.2% (26/86); ...
        looks good  =>  1 : 42.1% (1124/2673); username1@host 18.2% (205/1124); username16@host 17.3% (195/1124); ...
        go-go-go    =>  2 : 54.5% (1458/2673); maxim.abrosimov@host 77.8% (1134/1458); username1@host 12.5% (182/1458); ...

    content_checks:   maxim.abrosimov@host 77.1% (346/449); username15@host 12.9% (58/449); ...
        don't like  => -1 : 0.2% (1/449); username14@host 100.0% (1/1);
        looks good  =>  1 : 99.8% (448/449); maxim.abrosimov@host 77.2% (346/448); username15@host 12.9% (58/448); ...

    verify:           username1@host 0.3% (5/1940); maxim.abrosimov@host 0.2% (3/1940); ...
        looks good  =>  1 : 100.0% (14/14); username1@host 35.7% (5/14); ...

    manual_testing:   username8@host 34.7% (427/1231); username9@host 32.6% (401/1231); ...
        don't like  => -1 : 3.8% (47/1231); username9@host 34.0% (16/47); username8@host 27.7% (13/47); ...
        looks good  =>  1 : 96.2% (1184/1231); username8@host 35.0% (414/1184); username9@host 32.5% (385/1184); ...

    submitted:        maxim.abrosimov@host 31.7% (399/1259); username11@host 14.5% (183/1259); ...
        looks good  =>  1 : 100.0% (1259/1259); maxim.abrosimov@host 31.7% (399/1259); username11@host 14.5% (183/1259); ...

Authors 9; average 139.2
    username11@host: 20.9% (262/1253);
    username2@host: 15.8% (198/1253);
    username1@host: 13.9% (174/1253);
    username12@host: 13.2% (165/1253);
    username14@host: 10.2% (128/1253);
    maxim.abrosimov@host: 9.2% (115/1253);
    ...

Projects in merged 54
    project1: 337
    project6: 151
    project7: 98
    project2: 86
    ...

Branches in merged 126
    project1 branch1: 215 (17%)
    project6 branch1: 83 (6%)
    project7 branch1: 71 (5%)
    project1 branch2: 66 (5%)
    ...

```

##### Sample output for gerrit Owner
```
Owner: maxim.abrosimov@host
===========================
Merged reviews: 115 (100%) + abandoned: 0 (0%) = 115

Patch sets: 198, average: 1.7 per review
    in merged: 198, average: 1.7 per review, distribution: 1:51.3% 2:33.9% 3:7.8% 4:5.2% 5:1.7%

Projects in merged 16
    project1: 48
    project2: 29
    project3: 9
    project4: 9
    ...

Branches in merged 31
    project1 branch1: 30 (26%)
    project2 branch1: 13 (11%)
    project1 branch2: 12 (10%)
    project2 branch2: 10 (8%)
    ...

Human reviewers 43
    code_reviews:     username1@host 31.8% (57/179); username2@host 15.1% (27/179); ...
        don't like  => -1 : 3.4% (6/179); username1@host 50.0% (3/6); username3@host 16.7% (1/6); ...
        looks good  =>  1 : 76.0% (136/179); username1@host 27.2% (37/136); username2@host 18.4% (25/136); ...
        go-go-go    =>  2 : 20.7% (37/179); username1@host 45.9% (17/37); username4@host 10.8% (4/37); ...
    content_checks:   username5@host 71.4% (5/7); username6@host 28.6% (2/7);
        looks good  =>  1 : 100.0% (7/7); username5@host 71.4% (5/7); username6@host 28.6% (2/7);
    verify:           username7@host 1.1% (2/185);
        looks good  =>  1 : 100.0% (2/2); username7@host 100.0% (2/2);
    manual_testing:   username8@host 50.9% (29/57); username9@host 19.3% (11/57); username10@host 5.3% (3/57); ...
        looks good  =>  1 : 100.0% (57/57); username8@host 50.9% (29/57); username9@host 19.3% (11/57); ...
    submitted:        username7@host 66.7% (2/3); ...
        looks good  =>  1 : 100.0% (3/3); username7@host 66.7% (2/3); ...

Self
    submitted:        maxim.abrosimov@host 97.4% (112/115);
        looks good  =>  1 : 100.0% (112/112); maxim.abrosimov@host 100.0% (112/112);

Robots
    verify:           robot1@host 97.3% (180/185);
        don't like  => -1 : 13.9% (25/180); robot1@host 100.0% (25/25);
        looks good  =>  1 : 86.1% (155/180); robot1@host 100.0% (155/155);


```

##### Sample output for gerrit Reviewer
```
Reviewer: maxim.abrosimov@host
==============================
reviewed : 1758 (99%) + ignored: 15 (0%) = 1773
review scores:
    code_review:    1661 => -2: 0.2% (4/1661); -1: 3.0% (49/1661); 1: 7.8% (130/1661); 2: 89.0% (1478/1661);
    content_check:   759 => -1: 0.9% (7/759); 1: 99.1% (752/759);
    verify:            4 => -1: 0.0% (0/4); 1: 100.0% (4/4);
    manual_testing:   92 => -1: 2.2% (2/92); 1: 97.8% (90/92);

Ignored reviews:  15 (0.84%) out of total 1773 where added as reviewer

Average review time is 7 hours, the distribution of times is normalised

Projects 93, reviews 1758
    project1: 421
    project6: 185
    project2: 152
    project7: 119
    ...

Branches 195, reviews 1758
    project1 branch1: 243 (13%)
    project6 branch1: 104 (5%)
    project1 branch4: 87 (4%)
    project1 branch2: 83 (4%)
    ...

Reviewed owners 129
    username11@host: 252 (14%)
    username1@host: 160 (9%)
    username2@host: 156 (8%)
    username12@host: 154 (8%)
    ...

```




[Gerrit]:http://en.wikipedia.org/wiki/Gerrit_%28software%29
