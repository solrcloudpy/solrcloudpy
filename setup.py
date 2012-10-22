try:
    from setuptools import setup, find_packages
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages
    
    setup(
        name = "solrcloudpy",
        version = "1.0",
        description = "Solr4.0 client",
        author = 'Didier Deshommes',
        author_email = 'dfdeshom@gmail.com',
        packages=find_packages(exclude=['ez_setup']),
        classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search'
        ],
        
        install_requires = ['requests','kazoo']
        )
