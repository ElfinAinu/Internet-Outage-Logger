import requests
import logging
from datetime import time, datetime, date
import time
import csv
import os

logging.basicConfig(level=logging.INFO)
file_path = r""
# ^place your file path for output data csv here, example: r"E:\Files\MyStuff\Repositories\Output.csv" ^


def check_internet_connection(url="https://www.google.com", timeout=5):
    logging.info(
        f"Checking internet connection to {url} with a timeout of {timeout} seconds."
    )
    try:
        response = requests.get(url, timeout=timeout)
        logging.info(
            f"Internet connection established. Status code: {response.status_code}"
        )
        return True
    except requests.ConnectionError:
        logging.error("No internet connection could be established.")
        return False
    except requests.Timeout:
        logging.error(
            "The request timed out. This might indicate a slow or unstable internet connection."
        )
        return False
    except requests.RequestException as e:
        logging.error(f"An error occurred while checking internet connection: {e}")


def main():
    logging.info(
        f"Initiating internet connection check at {datetime.now()}. Logging outages to {file_path}."
    )
    defaultTime = datetime.now()
    data = {
        "Date": date.today(),
        "DropTime": defaultTime,
        "ReupTime": defaultTime,
        "Duration": defaultTime,
        "PreviousReup": defaultTime,
        "TimeFromLast": defaultTime,
    }
    outage = False
    while True:
        if outage == False:
            if check_internet_connection() == True:
                time.sleep(30)
                continue
            elif check_internet_connection() == False:
                outage = True
                data["DropTime"] = datetime.now()
                time.sleep(30)
                continue

        elif outage == True:
            if check_internet_connection() == True:
                outage = False
                data["Date"] = date.today()
                data["ReupTime"] = datetime.now()
                data["Duration"] = data["ReupTime"] - data["DropTime"]
                data["TimeFromLast"] = data["ReupTime"] - data["PreviousReup"]
                data["PreviousReup"] = data["ReupTime"]
                log_data(data, file_path)
                time.sleep(30)
                continue
            elif check_internet_connection() == False:
                time.sleep(30)
                continue

        else:
            print("Error: Checking internet connection failed.")
            time.sleep(30)


def get_last_reup_time(file_path):
    try:
        if not os.path.isfile(file_path) or os.stat(file_path).st_size == 0:
            return None
        with open(file_path, mode="r", newline="") as file:
            last_line = None
            for last_line in csv.reader(file):
                pass  # Iterate to the last line
            if last_line and len(last_line) > 2:  # Assuming 'ReupTime' is at least the third column
                return datetime.strptime(last_line[2], "%Y-%m-%d %H:%M:%S.%f")
    except Exception as e:
        print(f"Error reading last ReupTime from CSV: {e}")
    return None

def log_data(data: dict, file_path: str):
    previous_reup = get_last_reup_time(file_path)
    if previous_reup:
        data["PreviousReup"] = previous_reup

    selected_keys = ["Date", "DropTime", "ReupTime", "Duration", "TimeFromLast", "PreviousReup"]
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=selected_keys)
        if not file_exists:
            writer.writeheader()
        writer.writerow({key: data.get(key, "") for key in selected_keys})


if __name__ == "__main__":
    main()
    