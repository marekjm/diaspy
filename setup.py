from setuptools import setup, find_packages
setup(name='diaspy',
      version='0.4.2',
      author='Marek Marecki',
      author_email='hi@ozro.pw',
      url='https://github.com/marekjm/diaspy',
      description='Unofficial Python API to the social network Diaspora*',
      packages=find_packages(),
      install_requires=['requests']
      )
