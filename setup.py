from setuptools import setup

version = "0.0.1"

setup(name='pyseek',
      version=version,
      zip_safe=True,
      description='library for control of seek thermal camera',
      url='https://github.com/Fry-kun/pyseek',
      author='Fry Kun',
      classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering'],
      license='MIT',
      packages=['pyseek',
                'pyseek.lib'],
      install_requires=['pyusb',
                        'numpy',
                        'scipy']
    )
