from setuptools import setup

setup(
    name="doh",
    version="0.1",
    description="Download and reformat Discourse documentation for offline use.",
    url="https://github.com/s-makin/discourse-offline-helper",
    download_url=("https://github.com/s-makin/discourse-offline-helper" + "tarball/main"),
    license="GNU General Public License v3 or later",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3 :: Only",
    ],
    packages=["doh"],
    entry_points={"console_scripts": ["doh=doh.doh:main"]},
    install_requires=["alive-progress"],
    zip_safe=False,
)