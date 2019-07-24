from setuptools import setup

def readme():
    with open("README.md") as f:
        return f.read()

setup(
    name='imgur_upload',
    version='0.9',
    description='Upload images to Imgur.',
    url='https://github.com/jacob-c-bickel/imgur-upload',
    author='Jacob Bickel',
    author_email='jacob.c.bickel@gmail.com',
    license='MIT',
    include_package_data=True,
    packages=['imgur_upload'],
    install_requires=[
        'imgurpython',
    ],
    entry_points={
        'console_scripts': ['imgur-upload=imgur_upload.app:main']
    }
    zip_safe=False
)