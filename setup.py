from distutils.core import setup

setup(name='Netease Music Cloud Lover Crawler',
      version='1.0',
      description='A tool that collects the number of lovers of a song',
      author='Null Harry',
      url='https://github.com/abc612008',
      license="MIT",
      author_email='harryyunull@gmail.com',
      packages=['.'],
      install_requires=["requests","pycrypto"]
     )