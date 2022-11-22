from setuptools import find_packages, setup

setup(
    name="isar_robot",
    description="Integration and Supervisory control of Autonomous Robots - Open source robot implementation",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Equinor ASA",
    author_email="fg_robots_dev@equinor.com",
    url="https://github.com/equinor/isar-robot",
    license="EPL-2.0",
    classifiers=[
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
        "Topic :: Software Development :: Libraries",
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "isar_robot": [
            "example_images/for-science-you-monster.jpg",
            "example_images/wheatley-remain-calm.jpg",
        ]
    },
    include_package_data=True,
    install_requires=["alitra", "isar"],
    setup_requires=[
        "wheel",
    ],
    extras_require={
        "dev": [
            "black",
            "mypy",
            "pytest",
            "pre-commit",
        ]
    },
    python_requires=">=3.8",
    tests_require=["pytest"],
)
