from setuptools import setup, find_packages

version = '1.0'
shortdesc = "g24 elements"
longdesc = """"""

setup(name='g24.elements',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
            'Environment :: Web Environment',
            'Framework :: Zope2',
            'License :: OSI Approved :: GNU General Public License (GPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='',
      author='',
      author_email='',
      url='http://github.com/g24at/g24.elements',
      license='General Public Licence',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      namespace_packages=['g24',],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.app.event[dexterity]',
          'yafowil.plone',
          'yafowil.yaml',
          'yafowil.widget.datetime',
          'plone.app.jquery>=1.7'
      ],
      )
