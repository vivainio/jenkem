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
        #print "ji", job_info
        lastIdx = job_info['lastBuild']['number']
        firsIdx = max(lastIdx - 3, 1)
        for idx in range(lastIdx, firsIdx -1, -1):
            build_info = j().get_build_info(self.name, idx,1)
            print "  " + build_summary(build_info)

    def log(self):
        job_info = self.info()
        lastIdx = job_info['lastBuild']['number']
        text = j().get_build_console_output(self.name, lastIdx)
        print text

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


def main():
    args.init()
    c = args.sub('jobs', jobs_c)
    c.arg('jobpattern')

    c = args.sub('builds', builds_c)
    c.arg('job')

    c = args.sub('log', log_c)
    c.arg('jobname', nargs='?')

    c.arg('build', type=int, nargs='?')

    c = args.sub('set', set_c)
    c.arg('variable')
    c.arg('value')

    c = args.sub('sync', sync_c)

    c  = args.sub('fav', fav_c)
    c.arg('jobname')

    c = args.sub('favs', favs_c)

    args.parse()


main()

