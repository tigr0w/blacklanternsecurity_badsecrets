# BadDNS
Check subdomains for for subdomain takeovers and other DNS tomfoolery

[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![License](https://img.shields.io/badge/license-GPLv3-f126ea.svg)
[![tests](https://github.com/blacklanternsecurity/baddns/actions/workflows/tests.yaml/badge.svg)](https://github.com/blacklanternsecurity/baddns/actions/workflows/tests.yaml)
[![codecov](https://codecov.io/gh/blacklanternsecurity/baddns/branch/main/graph/badge.svg)](https://codecov.io/gh/blacklanternsecurity/baddns)
[![Pypi Downloads](https://img.shields.io/pypi/dm/baddns)](https://pypi.org/project/baddns)

<p align="left"><img width="300" height="300" src="https://github.com/blacklanternsecurity/baddns/assets/24899338/2ca1fe25-e834-4df8-8b02-8bf8f60f6e31"></p>

BadDNS is a standalone tool and [BBOT](https://github.com/blacklanternsecurity/bbot) module for detecting domain/subdomain takeovers of all kinds, including other DNS issues like NSEC walks and Subdomain Takeovers. 

## Installation

We have a [pypi](https://pypi.org/project/baddns/) package, so you can just do `pip install badsecrets` to make use of the library.

## usage 

After installing with pip, you can just run `baddns` from the command line.

```
baddns [-h] [-n CUSTOM_NAMESERVERS] [-c CUSTOM_SIGNATURES] [-l] [-m MODULES] [-d] [target]

positional arguments:
  target                subdomain to analyze

options:
  -h, --help            show this help message and exit
  -n CUSTOM_NAMESERVERS, --custom-nameservers CUSTOM_NAMESERVERS
                        Provide a list of custom nameservers separated by comma.
  -c CUSTOM_SIGNATURES, --custom-signatures CUSTOM_SIGNATURES
                        Use an alternate directory for loading signatures
  -l, --list-modules    List available modules and their descriptions.
  -m MODULES, --modules MODULES
                        Comma separated list of module names to use. Ex: module1,module2,module3
  -d, --debug           Enable debug logging

```

## Examples

* Simple check
```
baddns subdomaintocheck.example.com
```
* Specify Module(s)
```
baddns -m CNAME subdomaintocheck.example.com
baddns -m CNAME,NS subdomaintocheck.example.com
```
* List available Modules
```
baddns -l
```
* Custom Nameservers
```
baddns -n 1.1.1.1 subdomaintocheck.example.com
```
## Documentation
Please visit our full [documentation](https://www.blacklanternsecurity.com/baddns) for many more details, including information about specific BadDNS modules.

### Acknowledgements
BadDNS signatures are primarily adapted from [Nuclei Templates](https://github.com/projectdiscovery/nuclei-templates) and from [dnsReaper](https://github.com/punk-security/dnsReaper) by [Punk Security](https://punksecurity.co.uk/), and based on community discussions taking place at [can-i-take-over-xyz](https://github.com/EdOverflow/can-i-take-over-xyz/issues).
