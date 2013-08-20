from setuptools import setup, find_packages
setup(name='diaspy',
      version='0.3.1',
      author='Moritz Kiefer',
      author_email='moritz.kiefer@gmail.com',
      url='https://github.com/Javafant/diaspora-api',
      description='A Python API to the social network Diaspora*',
      packages=find_packages(),
      install_requires=['requests']
      )
