from setuptools import setup, find_packages
setup(name='diaspy',
      version='0.1.0',
      author='Moritz Kiefer',
      author_email='moritz.kiefer@gmail.com',
      url='https://github.com/Javafant/diaspora-api',
      description='A python api to the social network diaspora',
      packages=find_packages(),
      install_requires=['requests']
      )
