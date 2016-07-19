# -*- coding: utf-8 -*-

from __future__ import unicode_literals, absolute_import

import unittest
import tometa


class TestToMeta(unittest.TestCase):

    def setUp(self):
        self.app = tometa.App()

    def test_first_qs(self):
        qsl = [("x", 1), ("y", 2), ("z", 3), ("y", 4)]
        self.assertEqual(self.app.first_qs(qsl, "y"), 2)
        self.assertEqual(self.app.first_qs(qsl, "a"), None)

    def test_getname(self):
        qsl = [("name", "\"'Üü"), ("name", "noo")]
        self.assertEqual(self.app.getname(qsl), '"&quot;\'Üü"')
        try:
            self.app.getname([])
        except ValueError:
            pass
        else:
            self.fail()

    def test_getsize(self):
        qst = [("size", '30000000000000000570425344')]
        self.assertEqual(self.app.getsize(
            qst), "<size>30000000000000000570425344</size>")
        self.assertEqual(self.app.getsize([]), "")


if __name__ == "__main__":
    unittest.main()
