import jenkins
import args
import pprint
import textwrap
from datetime import datetime
from pickleshare import PickleShareDB
import sys
import pprint
import fnmatch
import tempfile
from subprocess import Popen, PIPE
import os
import webbrowser

db = PickleShareDB("~/jenkem")

def require_var(varname):
    val = db.get("config/" + varname)
    if val is None:
        print "Required variable missing. Run 'jenq set %s <somevalue>' to set it" % varname
        sys.exit(1)
    return val

_j = None

def j():
    global _j

    if _j is None:
        _j = jenkins.Jenkins(require_var("repository"))

    return _j

def runpeco(input):
    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.write(input)
    tf.close()
    p = Popen(['peco', tf.name], stdout = PIPE)
    out = p.stdout.read()
    os.unlink(tf.name)
    return out


class Job:
    def __init__(self, name):
        self.name = name

    def info(self):
        return j().get_job_info(self.name)

    def builds(self):
        job_info = self.info()
        pprint.pprint(job_info)
        ##print "ji", job_info
        lastIdx = job_info['lastBuild']['number']
        firsIdx = max(lastIdx - 3, 1)
        for idx in range(lastIdx, firsIdx -1, -1):
            try:
                build_info = j().get_build_info(self.name, idx,1)
                #pprint.pprint(build_info)
                print "  " + build_summary(build_info)
            except jenkins.NotFoundException:
                print "NOTFOUND #%d" % idx

    def log(self):
        job_info = self.info()
        lastIdx = job_info['lastBuild']['number']
        text = j().get_build_console_output(self.name, lastIdx)
        print text

    @staticmethod
    def find(jobname):
        n = find_job_or_pick(jobname)
        j = Job(n)
        return j

def jobs_c(args):
    jobs = find_jobs("*" + args.jobpattern+ "*")
    for j in jobs:
        print j


def job_summary(job_info):
	res = textwrap.dedent("""\
		{name} {color}
	""").format(**job_info).strip()
	return res

def build_summary(build_info):
	build_info['_guilty'] = [c['id'] for c in build_info['culprits']]
	res = textwrap.dedent("""\
		{id} {result} {_guilty}
	""").strip().format(**build_info)
	return res



def recent_builds(job_info):
    name = job_info['name']
    lastIdx = job_info['lastBuild']['number']
    firsIdx = max(lastIdx - 3, 1)
    for idx in range(lastIdx, firsIdx -1, -1):

        build_info = j.get_build_info(name, idx,1)
        print "  " + build_summary(build_info)
        #pprint.pprint(buildInfo)

def builds_c(args):
    job = Job(args.job)
    #pat = args.jobpattern
    job.builds()



def log_c(args):
    jobname = find_job_or_pick(args.jobname)
    job = Job(jobname)
    job.log()

def set_c(args):
    print "Setting", args
    db['config/' + args.variable] = args.value

def sync_c(args):
    jobs = j().get_jobs()
    db['jobs'] = jobs

def match_pat(s, pat):
    #print "match", s, "with",pat
    return fnmatch.fnmatch(s,pat)

def find_jobs(pat):
    jobs = db['jobs']
    return [ j['name'] for j in jobs if match_pat(j['name'], pat)]

def find_job_or_pick(jobname):
    aliased = db.get('alias', {}).get(jobname)
    if aliased:
        return aliased

    jobs = db['jobs']
    if jobname is None:
        inp = "\n".join(j['name'] for j in jobs)
        out = runpeco(inp)
        return out.strip()

    return jobname


def fav_c(args):
    n = args.jobname
    jobs = find_job_or_pick(n)

    if not n in jobs:
        print "No such job, did you mean:"
        print "\n".join(jobs)
        return
    favs = db.get('favs', set())
    favs.add(n)
    db['favs'] = favs

def favs_c(args):
    favs = db['favs']
    for job in [Job(n) for n in favs]:
        print job.name
        job.builds()

def alias_c(args):

    aliases = db.get('alias', {})
    if args.shortname is None:
        pprint.pprint(aliases)
        return
    jobname = find_job_or_pick(args.jobname)
    aliases[args.shortname] = jobname
    db['alias'] = aliases

def find_job_info(jobname):
    n = find_job_or_pick(args.jobname)
    j = Job(n)
    inf = j.info()
    return inf, j


def job_c(args):
    j = Job.find(args.jobname)
    j.builds()
    pprint.pprint(j.info())

def go_c(args):
    j = Job.find(args.jobname)
    inf = j.info()
    pprint.pprint(inf)
    url = inf['lastBuild']['url']
    webbrowser.open(url)

def main():
    args.init()
    c = args.sub('jobs', jobs_c, help="List all jobs matching JOBPATTERN")
    c.arg('jobpattern', metavar="JOBPATTERN")

    c = args.sub('builds', builds_c, help="Show recent builds for JOB")
    c.arg('job', metavar="JOB")

    c = args.sub('log', log_c, help="Show console output for JOB, build# BUILD (or latest)")
    c.arg('jobname', nargs='?', metavar="JOB")

    c.arg('build', type=int, nargs='?', metavar="BUILD")

    c = args.sub('set', set_c, help="Set permanent config variable (e.g. 'jenq set repository http://foo-jenkins.busyware.com')")
    c.arg('variable', metavar="VARIABLE")
    c.arg('value', metavar="VALUE")

    c = args.sub('sync', sync_c, help="Fetch list of jobs from repository to local cache")

    c  = args.sub('fav', fav_c, help="Favorite a job")
    c.arg('jobname', nargs='?', metavar="JOB")

    c = args.sub('favs', favs_c, help="Show recent builds for all favorited jobs")

    c = args.sub('alias', alias_c, help="Create convenient alias for JOB")
    c.arg('shortname', nargs='?', metavar="SHORTNAME")
    c.arg('jobname', nargs='?', metavar="JOB")

    c = args.sub('jobinfo', job_c, help="Display raw job info (json)")
    c.arg('jobname', nargs='?', metavar="JOB")

    c = args.sub('go', go_c, help="Open newest build for JOB in browser")
    c.arg('jobname', nargs='?', metavar="JOB")

    args.parse()


if __name__ == "__main__":
    main()

