from setuptools import setup, find_packages

setup(
    name="musiclib",
    version="0.0.1",
    author="Victor G",
    description="A music library organizer",
    packages=find_packages(),
    python_requires="~=3.6",
    entry_points={"console_scripts": "musiclib=musiclib._main:main"},
    install_requires=["eyeD3", "attrs"],
    extras_require={
        'download': ['youtube-dl']
    }
)
