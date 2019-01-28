try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

INSTALL_REQUIRE = []
with open('requirements/prod.txt') as fd:
     for line in fd.readlines():
        INSTALL_REQUIRE.append(line.replace(' ', ''))



setup(
    name='outbrain',
    version='0.0.1',
    author='Mate Bendeguz Kovacs',
    author_email='k.mate555@gmail.com',
    url='https://github.com/kmb5/python-adform',
    packages=['adform'],
    license='LGPL 2.1 or later',
    description='Wrapper for the AdForm API',
    install_requires=INSTALL_REQUIRE,
    keywords=['adform','api'],
    classifiers=['Intended Audience :: Developers']
)
