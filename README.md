# Bill Tracker
Let's publish Colorado State bills.

# Relevant links:
- List of Senate bills: http://www.leg.state.co.us/CLICS/CLICS2015A/csl.nsf/BillFoldersSenate?openFrameset
- How they present PDFs: http://www.leg.state.co.us/clics/clics2015a/csl.nsf/fsbillcont3/BED55652BAA579B987257D9000780984?Open&file=SB002_00.pdf

# How to use this
legquery.py expects an environment variable named `NAME_OF_VAR` set with your sunlight foundation API key in it. You can get a key at http://sunlightfoundation.com/api/accounts/register/

About the Sunlight API: https://sunlightlabs.github.io/openstates-api/bills.html

About the python bindings for the Sunlight API: http://python-sunlight.readthedocs.org/en/latest/services/openstates.html

## Setting up a dev environment
Here's the first draft of instructions:

1. Check out / update the repo.
2. Create a virtual environtment.
3. Download the project requirements, `pip install -r requirements.txt`
4. Download all the bills, `python legquery.py --limit 4000`
5. Open a new terminal window, cd to the project, activate the virtualenv
6. `python runserver.py`, then open up http://localhost:5000/

# License
Copyright © 2015-2016 The Denver Post

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
