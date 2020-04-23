
from unittest import TextTestRunner

from bi.tests.common import suite

TextTestRunner(verbosity=2).run(suite())