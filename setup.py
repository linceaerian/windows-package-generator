from setuptools import setup, find_packages

setup(name='windows-package-generator',
      version='0.1',
      description='Python app to create windows .msi package',
      url='https://github.com/wallforfry/windows-package-generator',
      author='Wallerand DELEVACQ',
      author_email='wallforfry@gmail.com',
      license='GNU GPLv3',
      packages=find_packages(),
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'windows-package-generator = windows_package_generator.generator:main'
          ]
      }, install_requires=['xmltodict', 'pyCLI'])
