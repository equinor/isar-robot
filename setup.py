from setuptools import find_packages, setup

setup(
    name="isar_robot",
    description="Integration and Supervisory control of Autonomous Robots - Open source robot implementation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    version="1.0.2",
    author="Equinor ASA",
    author_email="fg_robots@equinor.com",
    url="https://github.com/equinor/isar_robot",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries",
    ],
    include_package_data=True,
    setup_requires=["wheel"],
    python_requires=">=3.8",
    tests_require=["pytest"],
)
