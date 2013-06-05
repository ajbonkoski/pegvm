from setuptools import setup

setup(name='pegvm',
      version='0.1',
      description='A PEG-parser engine (VM) that can support dynamic run-time-generated grammars',
      url='https://bitbucket.org/abonkosk/pegvm',
      author='Anthony J Bonkoski',
      author_email='ajbonkoski@gmail.com',
      packages=['pegvm'],
      scripts=["bin/pegvm_parse", "bin/pegvmc"],
      zip_safe=False)
