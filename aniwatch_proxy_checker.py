import requests
import threading
import sys

"""Usage: python aniwatch_proxy_checker.py proxy_file max_timeout"""


def check_proxy(proxy, timeout):
    global good_proxies
    try:
        with requests.get("https://aniwatch.me", proxies={"https": proxy}, timeout=timeout) as r:
            if "The owner of this website (aniwatch.me) has banned the autonomous system number (ASN)" in r.text:
                return
        good_proxies.append(proxy)
        return
    except Exception:
        return


if __name__ == "__main__":
    good_proxies = []
    threads = []
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        lol = [x.replace("\n", "") for x in f.readlines()]
    for proxy in lol:
        threads.append(threading.Thread(target=check_proxy, args=(proxy, int(sys.argv[2]),)))
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    with open("aniwatch.proxies.txt", "w+") as f:
        f.write("".join(f"{x}\n" for x in good_proxies))

    print("".join(f"{x}\n" for x in good_proxies))
