Domain Crawler
=============

A command line utility to crawl a single domain. When invoked from the console, it prints the site map as a digraph in the form of a sequence of 
vertices and edges. 

###Usage:
To use the crawler:

* Clone this repository: 
* Create a virtualenv if need be
* Change to the directory. Then change to the src directory.
* Either in the global python environment or in the virtual env, run the following command : pip install -r requirements.txt
* set the library path : export PYTHONPATH=$PWD:$PYTHONPATH
* Run the following command to start crawling a domain : python domaincrawl/crawler_init.py --log_conf ../conf/logging.conf --url http://localhost:8000/
* Alternatively, invoke the script with the -h option to see the following help message:

>usage: crawler_init.py [-h] [--alt_conf_path ALT_CONF_PATH] --log_conf
>                       LOG_CONF --url URL
>
>Crawl a single domain
>
>optional arguments:

>  -h, --help            show this help message and exit

>  --alt_conf_path ALT_CONF_PATH
                        Path to a python config (without sections) that may be
                        used to override config defaults

>  --log_conf LOG_CONF   The location of the logging configuration file in the
                         python logging config format

>  --url URL             The base url with the domain name of the site to be
                         crawled. (e.g. http://acme.com)


###Limitations and Enhancements:
Refer to [this page](https://github.com/planBrk/domaincrawler/wiki/Current-limitations-&-Pending-enhancements) for details.
