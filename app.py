import time
import requests
from huawei_lte_api.Connection import Connection
from huawei_lte_api.Client import Client
from huawei_lte_api.enums.client import ResponseEnum

class HuaweiLte:
    def __init__(self, device_ip, username=None, password=None):
        if username and password:
            self.url = f"http://{username}:{password}@{device_ip}/"
        else:
            self.url = f"http://{device_ip}/"
        self.username = username
        self.password = password
        self._connection = None
        self._client = None

    def connect(self):
        self._connection = Connection(self.url, username=self.username, password=self.password)
        self._client = Client(self._connection)

    def send_sms(self, recipient_number: str, message: str) -> bool:
        if self._client is None:
            raise RuntimeError("Not connected")
        status = self._client.sms.send_sms([recipient_number], message)
        return status == ResponseEnum.OK.value


def get_broadcast_message():
    response = requests.get('https://baao-disaster-link.vercel.app/api/get-broadcast')  # Replace with actual URL
    if response.status_code == 200:
        data = response.json()
        return data.get("broadcastData", "")
    return ""


def get_all_mobiles():
    response = requests.get('https://baao-disaster-link.vercel.app/api/get-all-mobiles')
    if response.status_code == 200:
        data = response.json()
        return data.get("mobileNumbers", [])
    return []


def update_broadcast_message():
    data = {'broadcastData': ""}
    response = requests.post('https://baao-disaster-link.vercel.app/api/update-broadcast', json=data)  # Replace with actual URL
    return response.status_code == 200


def main():
    device_ip = "192.168.8.1"
    username = "admin"
    password = "admin"

    lte = HuaweiLte(device_ip, username, password)
    lte.connect()

    while True:
        # Step 1: Check for broadcast message
        broadcast_message = get_broadcast_message()

        if broadcast_message:  # Only proceed if the broadcast message is not empty
            print("Broadcast message found. Sending to mobile numbers...")

            # Step 2: Get all active mobile numbers and replace "09" with "+63"
            mobile_numbers = get_all_mobiles()
            valid_numbers = [
                num if num.startswith("+639") else f"+63{num[1:]}" if num.startswith("09") else num
                for num in mobile_numbers
            ]

            # Step 3: Send broadcast message to each mobile number with 1-second delay
            for number in valid_numbers:
                if lte.send_sms(number, broadcast_message):
                    print(f"SMS sent successfully to {number}")
                else:
                    print(f"Failed to send SMS to {number}")

                print(f"SMS sent successfully to {number}")
                time.sleep(1)  # 1-second delay between each message

            # Step 4: After sending, clear the broadcast message
            if update_broadcast_message():
                print("Broadcast message cleared.")
            else:
                print("Failed to clear the broadcast message.")

        else:
            print("No broadcast message found.")

        # Step 5: Wait for 60 seconds before checking again
        print("Waiting for 60 seconds before checking again...")
        time.sleep(60)


if __name__ == "__main__":
    main()

