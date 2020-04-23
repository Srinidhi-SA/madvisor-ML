
from unittest import TextTestRunner

from bi.tests import suite

TextTestRunner(verbosity=2).run(suite())