from setuptools import setup

def readme():
    with open('README.txt') as f:
        return f.read()

setup(name='rhessysworkflows',
      version='1.0',
      description='Libraries and command-line scripts for performing RHESSys data preparation workflows.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Topic :: Scientific/Engineering :: GIS'        
      ],
      url='https://github.com/selimnairb/RHESSysWorkflows',
      author='Brian Miles',
      author_email='brian_miles@unc.edu',
      license='BSD',
      packages=['rhessysworkflows',
                'rhessysworkflows.tests'
                ],
      install_requires=[
        'ecohydrolib'
      ],
      scripts=['bin/CreateFlowtable.py',
               'bin/CreateGRASSLocationFromDEM.py',
               'bin/CreateWorldfile.py',
               'bin/DelineateWatershed.py',
               'bin/GenerateCustomSoilDefinitions.py',
               'bin/GenerateLandcoverMaps.py',
               'bin/GeneratePatchMap.py',
               'bin/GenerateSoilTextureMap.py',
               'bin/ImportClimateData.py',
               'bin/ImportRHESSysSource.py',
               'bin/ImportRasterMapIntoGRASS.py',
               'bin/RegisterCustomSoilReclassRules.py',
               'bin/RegisterLandcoverReclassRules.py',
               'bin/RunLAIRead.py'
      ],
      package_data = {
                      'etc/NLCD2006': ['*.rule'],
                      },
      zip_safe=False)
