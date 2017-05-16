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


pkgs = find_packages('lib',exclude=['tests'])

print(pkgs)

os._exit(0)



setup(
    name='sshgo',
    ext_modules=[Extension('Vulcan', cythonize("lib/Vulcan.py")[0].sources )],
    version='0.1',
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
    setup_requires=[],
    test_suite=''
)
