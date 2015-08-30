#!/usr/bin/env python

from distutils.core import setup

setup(name='easyselenium',
      version='0.2',
      description='Easy Selenium - small Selenium-based Test Automation Framework',
      author='Kirill Strelkov',
      url='https://github.com/kirillstrelkov/easyselenium',
      packages=['easyselenium',
                'easyselenium.ui',
                'easyselenium.ui.editor',
                'easyselenium.ui.generator',
                'easyselenium.ui.image',
                'easyselenium.ui.parser'],
      scripts=['easyselenium/scripts/easy_selenium_cli.py',
               'easyselenium/scripts/easy_selenium_ui.py'], requires=['selenium', 'nose'])
