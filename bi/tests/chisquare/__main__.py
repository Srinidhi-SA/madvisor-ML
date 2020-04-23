
from unittest import TextTestRunner

from bi.tests.chisquare import suite

TextTestRunner(verbosity=2).run(suite())