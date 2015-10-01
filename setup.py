from distutils.core import setup

setup(name='jenkem',
      version='0.1.2',
      description='A command line interface for jenkins',
      author='Ville Vainio',
      author_email='vivainio@gmail.com',
      url='https://github.com/vivainio/jenkem',
      packages=['jenq'],
      install_requires='pickleshare',
      entry_points = {
        'console_scripts': [
            'jenkem = jenq.jenq:main',
        ]
      }
     )
