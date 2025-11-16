from setuptools import setup, find_packages

def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Remove comments and empty lines
    lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
    return lines

requirements = parse_requirements('requirements.txt')

setup(
    name='futureself-backend',
    version='0.1.0',
    description='Backend for the FutureSelf project.',
    author='Your Name',  # Please change this
    author_email='your.email@example.com',  # Please change this
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
