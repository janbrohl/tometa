# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import unittest
import tometa


class TestToMeta(unittest.TestCase):

    def setUp(self):
        self.app = tometa.App()

    def test_firts_qst(self):
        qst = [("x", 1), ("y", 2), ("z", 3), ("y", 4)]
        self.assertEqual(self.app.first_qst(qst, "y"), 2)
        self.assertEqual(self.app.first_qst(qst, "a"), None)

    def test_getname(self):
        qst = [("name", "\"'Üü"), ("name", "noo")]
        self.assertEqual(self.app.getname(qst), '"&quot;\'Üü"')
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
