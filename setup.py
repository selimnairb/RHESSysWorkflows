from setuptools import setup

def readme():
    with open('README.txt') as f:
        return f.read()

setup(name='rhessysworkflows',
      version='0.9',
      description='Libraries and command-line scripts for performing RHESSys data preparation workflows.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
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
      packages=[],
      install_requires=[
        'ecohydroworkflowlib'
      ],
      scripts=['bin/DelineateWatershed.py',
               'bin/GenerateSoilTextureMap.py',
               'bin/ImportDEMIntoNewGRASSLocation.py',
               'bin/GenerateLandcoverMaps.py'
      ],
      data_files=[(directory, [file1, file2]),
                  (directory), [file1, file2]
      ],
      zip_safe=False)
