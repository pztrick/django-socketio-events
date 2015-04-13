from setuptools import setup, find_packages
import os
import sys
import subprocess
from distutils.errors import DistutilsPlatformError, DistutilsInternalError
from setuptools.command.install import install

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('django-socketio-events')

npm_global_dependencies = {
    "node-gyp": "*"
}
# local dependencies defined in django-socketio-events/package.json


class custom_install(install):
    def run_npm_global(self):
        """ h/t https://github.com/elbaschid/virtual-node/blob/master/setup.py """
        for name, version in npm_global_dependencies.items():
            # packages are installed globally to make sure that they are
            # installed in the virtualenv rather than the current directory.
            # it is also necessary for packages containing scripts, e.g. less
            dep_name = '%s@%s' % (name, version)
            self.run_cmd(['npm', 'install', '-g', dep_name])

    def run_npm_local(self):
        self.run_cmd(['npm', 'install'], 'django-socketio-events')

    def run_cmd(self, cmd, cwd=None, extra_env=None):
        """ h/t https://github.com/elbaschid/virtual-node/blob/master/setup.py """
        all_output = []
        cmd_parts = []

        for part in cmd:
            if len(part) > 45:
                part = part[:20] + "..." + part[-20:]
            if ' ' in part or '\n' in part or '"' in part or "'" in part:
                part = '"%s"' % part.replace('"', '\\"')
            cmd_parts.append(part)
        cmd_desc = ' '.join(cmd_parts)
        logger.debug(" ** Running command %s" % cmd_desc)

        # output
        stdout = subprocess.PIPE

        # env
        if extra_env:
            env = os.environ.copy()
            if extra_env:
                env.update(extra_env)
        else:
            env = None

        # execute
        try:
            proc = subprocess.Popen(
                [' '.join(cmd)], stderr=subprocess.STDOUT, stdin=None, stdout=stdout,
                cwd=cwd, env=env, shell=True)
        except Exception:
            e = sys.exc_info()[1]
            logger.error("Error %s while executing command %s" % (e, cmd_desc))
            raise

        stdout = proc.stdout
        while stdout:
            line = stdout.readline()
            if not line:
                break
            line = line.rstrip()
            all_output.append(line)
            logger.info(line)
        proc.wait()

        # error handler
        if proc.returncode:
            for s in all_output:
                logger.critical(s)
            raise OSError("Command %s failed with error code %s"
                % (cmd_desc, proc.returncode))

        return proc.returncode, all_output

    def run(self):
        if not os.environ.get('VIRTUAL_ENV', None):
            raise DistutilsPlatformError('You must install django-socketio-events into a virtualenv. Aborting.')

        # print "* * * 1) Do egg install"
        # hack: i have to do this twice to ensure node is available
        # for npm install
        # install.do_egg_install(self)

        # 1) Install npm depencies into virtualenv/virtual-node
        print "* * * \t 2) installing npm dependencies"
        self.run_npm_global()
        self.run_npm_local()

        print "* * * 3) Re-do egg install with npm dependencies intact"
        install.do_egg_install(self)


setup(
    cmdclass={'install': custom_install},
    name='django-socketio-events',
    version='0.1.2',
    author='Patrick Paul',
    author_email='pztrick44@gmail.com',
    packages=find_packages() + ['nodjango.node_modules'],
    include_package_data=True,
    scripts=[],
    url='https://github.com/pztrick/django-socketio-events/',
    license='MIT-LICENSE.txt',
    description='Django package for socket.io via nodejs',
    long_description=open('README.md').read(),
    install_requires=[
        "Django >= 1.7.0",
        "virtual-node == 0.1.0",
        "socketIO-client == 0.6.1"
    ],
)
