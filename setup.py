from setuptools import setup, find_packages

setup(
    name='diaspy-api',
    version='0.5.1',
    author='Marek Marecki',
    author_email='marekjm@ozro.pw',
    url='https://github.com/marekjm/diaspy',
    license='GNU GPL v3',
    description='Unofficial Python API for Diaspora*',
    keywords='diaspy diaspora social network api',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
    install_requires=['requests']
)
