# Bill Tracker
Let's publish Colorado State bills.

## How to manage the site

### At the start of a legislative session
1. Turn on the cron jobs.
2. Update the README to reference the year of the current session.
3. Update the lines in the repo marked with `***HC` to reference or include the current session.

### At the end of a legislative session
1. Turn off the cron jobs.

## Relevant links:
- List of Senate bills: http://www.leg.state.co.us/CLICS/CLICS2015A/csl.nsf/BillFoldersSenate?openFrameset
- How they present PDFs: http://www.leg.state.co.us/clics/clics2015a/csl.nsf/fsbillcont3/BED55652BAA579B987257D9000780984?Open&file=SB002_00.pdf

## How to use this code
legquery.py expects an environment variable named `SUNLIGHT_API_KEY` set with your sunlight foundation API key in it. You can get a key at http://sunlightfoundation.com/api/accounts/register/

About the Sunlight API: https://sunlightlabs.github.io/openstates-api/bills.html

About the python bindings for the Sunlight API: http://python-sunlight.readthedocs.org/en/latest/services/openstates.html

See how the Sunlight foundation publishes this data: http://openstates.org/co/

### Setting up a dev environment
Here's the third draft of instructions:

1. Check out / update the repo.
2. Create a virtual environtment, activate it.
3. Download the project requirements: `pip install -r requirements.txt`
4. Download all the bills: `python legquery.py --verbose`
5. Download the bill details for the current session: `python legquery.py --session 2016a --details`
6. Open a new terminal window, cd to the project, activate the virtualenv
7. `python runserver.py`, then open up http://localhost:5000/
8. To get previous legislative sessions to work, you'll need the bill details for the prior sessions. `for s in "2015a" "2014a" "2013a" "2012b" "2012a" "2011a"; do python legquery.py --session $s --details --verbose; done` should do that for you.

#### Deploying

Note: `--freeze` takes a snapshot of the current templates. If you haven't made any template- or data-level changes since the last time you froze, you don't need to `--freeze`.

* Deploy everything: `python deploy.py --freeze --ftp`
* Deploy the homepage `python deploy.py --nosession --freeze --ftp`
* Deploy the current session's files `python deploy.py --session 2016a --freeze --ftp`
* Deploy a previous session's files `python deploy.py --session 2012a --freeze --ftp`

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
