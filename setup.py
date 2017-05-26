from distutils.core import setup
import os,sys
import os.path

sys.path.insert(0, os.path.abspath('lib'))
try:
    from setuptools import setup, Extension,find_packages
except ImportError:
    print("sshgo needs setuptools in order to build. Install it using"
            " your package manager (usually python-setuptools) or via pip (pip"
            " install setuptools).")
    sys.exit(1)

try:
    from Cython.Build import cythonize
except ImportError:
    print("sshgo needs Cython in order to build. Install it using"
            " your package manager (usually python-setuptools) or via pip (pip"
            " install cython).")
    sys.exit(1)

with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()
    if not install_requirements:
        print("Unable to read requirements from the requirements.txt file"
                "That indicates this copy of the source code is incomplete.")
        sys.exit(2)

with open('VERSION') as version_file:
    __version__ = version_file.read().splitlines()[0]
    #print(__version__)
    if not __version__:
        print("Unable to read version from the VERSION file"
                "That indicates this copy of the source code is incomplete.")
        sys.exit(2)



#pkgs = find_packages('lib',exclude=['tests'])


setup(
    name='sshgo',
    ext_modules=[Extension('Vulcan', cythonize("lib/Vulcan.py")[0].sources )],
    version=__version__,
    url='https://github.com/ninghaoyu/sshgo',
    license='MIT',
    author='NingHaoYu',
    author_email='ninghaoyu@360.cn',
    description='auto ssh to remote unix like host',
    install_requires=install_requirements,
    package_dir={ '': 'lib' },
    packages=find_packages('lib',exclude=['tests']),
    scripts=['bin/sshgo'],
    data_files=[],
    long_description=open('README.md').read(),
    zip_safe=False,
    setup_requires=['cython'],
    test_suite=''
)
