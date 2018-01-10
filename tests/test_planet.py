#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pytest
import requests
from configparser import ConfigParser

@pytest.fixture
def config(ini):
    parser = ConfigParser()
    parser.read(ini)
    return parser

@pytest.mark.unit
def test_200(config):
    url = config['Planet']['link']
    response = requests.get(url)
    assert response.status_code == 200
