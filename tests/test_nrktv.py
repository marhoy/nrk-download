# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import nrkdownload.nrktv as nrktv


def test_search():

    series = nrktv.search("pompel og pilt", "series")
    titles = [serie.title for serie in series]
    assert "Pompel og pilt - Reparatørene kommer" in titles

    programs = nrktv.search("nils og blåmann", "program")
    titles = [program.title for program in programs]
    assert "Nils og Blåmann" in titles
