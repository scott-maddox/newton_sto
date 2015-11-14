# Copyright (c) 2015, Scott J Maddox. All rights reserved.
# Use of this source code is governed by the BSD-3-Clause
# license that can be found in the LICENSE file.

# Make sure we import the local package
import os
import sys
sys.path.insert(0,
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from newton_sto import app

if len(sys.argv) > 1 and sys.argv[1] == 'debug':
    app.run(debug=True)
else:
    app.run()
