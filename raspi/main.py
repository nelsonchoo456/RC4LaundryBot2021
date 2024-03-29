import json
import logging
import socket
from datetime import datetime
from os import mkdir
from os.path import isdir, join
from time import sleep

import requests
from sensor import Machine

FLOOR = 4  # TODO: Shift to settings.json


def main() -> None:
    logging.info("Initializing script, hello world!")

    with open("settings.json", "r") as f:
        settings: dict = json.load(f)

    timeout: int = settings["timeout"]

    # Prepend the endpoint with "http://" if necessary
    endpoint: str = settings["endpoint"]
    endpoint = endpoint if endpoint.startswith("http://") else "http://" + endpoint

    # Create all the class instances
    machines = [
        Machine(x["pin"], x["id"], endpoint, http_timeout=timeout)
        for x in settings["machines"]
    ]

    while True:
        update_rpi_ip(endpoint, timeout)
        for m in machines:
            m.update()
        sleep(60)


# Following code is taken from https://stackoverflow.com/a/28950776
def get_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP


def update_rpi_ip(endpoint: str, http_timeout: int) -> None:
    ip: str = get_ip()
    try:
        requests.put(endpoint, {"floor": FLOOR, "ip_addr": ip}, timeout=http_timeout)
        logging.debug("Successfully updated RPi IP to backend.")
    except (requests.ConnectionError, Exception) as e:
        logging.error(
            f"Error while trying to update RPi IP to backend. Error trace: {e}"
        )


if __name__ == "__main__":
    # Set up basic logging
    if not isdir("logs"):
        mkdir("logs")
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%d/%m/%Y %I:%M:%S %p",
        handlers=[
            # Send to both stderr and file at the same time
            logging.FileHandler(join("logs", f"{datetime.today().date()}.log")),
            logging.StreamHandler(),
        ],
    )
    main()
