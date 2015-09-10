# Personalized jenkins experience

Jenkins web ui can be slow to navigate, if you have lots of jobs. This app is faster, as it
maintains job listing offline.

Uses [Peco](https://github.com/peco/peco) for searching jobs interactively in text console.
Commands that take job name as argument launch peco if no job name is provided.

Installation:

(soon to appear in PyPi, but in the meantime...)
```
$ choco install peco
$ git clone https://github.com/vivainio/jenkem.git
$ cd jenkem
$ pip install -r requirements.txt
$ cd jenq
$ python jenq.py set repository http://address-to-my-jenkins

$ python .\jenq.py -h
usage: jenq.py [-h] {jobs,builds,log,set,sync,fav,favs,alias,jobinfo,go} ...

positional arguments:
  {jobs,builds,log,set,sync,fav,favs,alias,jobinfo,go}
    jobs                List all jobs matching JOBPATTERN
    builds              Show recent builds for JOB
    log                 Show console output for JOB, build# BUILD (or latest)
    set                 Set permanent config variable (e.g. 'jenq set
                        repository http://foo-jenkins.busyware.com')
    sync                Fetch list of jobs from repository to local cache
    fav                 Favorite a job
    favs                Show recent builds for all favorited jobs
    alias               Create convenient alias for JOB
    jobinfo             Display raw job info (json)
    go                  Open newest build for JOB in browser

optional arguments:
  -h, --help            show this help message and exit
```

TODO:

- Angular 2 Web UI (coming later)
- Grepping console output for common error patterns
