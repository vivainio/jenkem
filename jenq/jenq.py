import jenkins
import args
import pprint
import textwrap
from datetime import datetime
from pickleshare import PickleShareDB
import sys
import pprint

db = PickleShareDB("~/jenkem")


def require_var(varname):
    val = db.get("config/" + varname)
    if val is None:
        print "Required variable missing. Run 'jenq set %s <somevalue>' to set it" % varname
        sys.exit(1)
    return val

#j = jenkins.Jenkins('http://alusta-jenkins.basware.com')

_j = None

def j():
    global _j

    if _j is None:
        _j = jenkins.Jenkins(require_var("repository"))
        # 'http://alusta-jenkins.basware.com')

    return _j

class Job:
    def __init__(self, name):
        self.name = name

    def info(self):
        return j().get_job_info(self.name)

    def builds(self):
        job_info = self.info()
        lastIdx = job_info['lastBuild']['number']
        firsIdx = max(lastIdx - 3, 1)
        for idx in range(lastIdx, firsIdx -1, -1):
            build_info = j().get_build_info(self.name, idx,1)
            print "  " + build_summary(build_info)


def find_jobs(pat):
    jobs = j().get_job_info_regex(pat)
    for job in jobs:
        yield job


def jobs_c(args):
    jobs = db['jobs']
    for j in jobs:
        if args.jobpattern in j['name']:
            print job_summary(j)


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
	name = args.jobname;
	builds = args.builds[0]
	job_info = j().get_job_info(name)
	pprint.pprint(job_info)

def set_c(args):
    print "Setting", args
    db['config/' + args.variable] = args.value

def sync_c(args):
    jobs = j().get_jobs()
    db['jobs'] = jobs

def main():
    args.init()
    c = args.sub('jobs', jobs_c)
    c.arg('jobpattern')

    c = args.sub('builds', builds_c)
    c.arg('job')

    c = args.sub('log', log_c)
    c.arg('jobname', type=str)
    c.arg('build', type=int, nargs='?')

    c = args.sub('set', set_c)
    c.arg('variable')
    c.arg('value')

    c = args.sub('sync', sync_c)


    args.parse()

main()

