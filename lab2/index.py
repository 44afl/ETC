import requests
import time
import matplotlib.pyplot as plt
import urllib
from collections import defaultdict

BASE_URL = "https://jsonplaceholder.typicode.com"

stats = {
    "total_requests": 0,
    "per_endpoint": defaultdict(int),
    "per_method": defaultdict(int),
    "status_codes": defaultdict(int),
    "response_times": []
}

def tracked_request(method, url, **kwargs):
    start = time.time()
    response = requests.request(method, url, **kwargs)
    elapsed = time.time() - start

    stats["total_requests"] += 1
    stats["per_endpoint"][url] += 1
    stats["per_method"][method] += 1
    stats["status_codes"][response.status_code // 100] += 1
    stats["response_times"].append(elapsed)

    return response

def users_by_city(city):
    response = tracked_request("GET", f"{BASE_URL}/users?address.city={urllib.parse.quote(city)}")
    users = response.json()

    print("\nUsers in city:", city)
    if len(users) < 1:
        print("No users found.")
        return

    for user in users:
        print(f'{user["name"]} - {user["email"]}')

def create_post():
    posts = tracked_request("GET", f"{BASE_URL}/posts").json()
    existing_titles = {p["title"] for p in posts}

    user_id = int(input("User ID: "))
    while True:
        title = input("Title: ")
        if title not in existing_titles:
            break
        print("Title already exists. Choose another.")

    body = input("Body: ")

    response = tracked_request(
        "POST",
        f"{BASE_URL}/posts",
        json={"userId": user_id, "title": title, "body": body}
    )

    print("Created post:", response.json())

def update_post():
    post_id = int(input("Post ID to update: "))
    choice = input("Update (title/body/both): ").lower()

    data = {}
    if choice in ("title", "both"):
        data["title"] = input("New title: ")
    if choice in ("body", "both"):
        data["body"] = input("New body: ")

    headers = {"Authorization": "fake-token-12345"}

    response = tracked_request(
        "PATCH",
        f"{BASE_URL}/posts/{post_id}",
        json=data,
        headers=headers
    )

    print("Updated post:", response.json())

def delete_post():
    while True:
        post_id = int(input("Post ID to delete (type 0 to skip): "))
        if post_id == 0:
            print("Skipping delete operation.")
            break
        response = tracked_request(
            "DELETE",
            f"{BASE_URL}/posts/{post_id}"
        )

        if response.status_code == 200:
            print("Post deleted successfully.")
            break
        else:
            print("Delete failed. Try again.")

def show_statistics():
    times = stats["response_times"]

    print("\n=== STATISTICS ===")
    print("Total requests:", stats["total_requests"])
    print("Requests per endpoint:", dict(stats["per_endpoint"]))
    print("Requests per method:", dict(stats["per_method"]))
    print("2xx:", stats["status_codes"].get(2, 0))
    print("4xx:", stats["status_codes"].get(4, 0))
    print("5xx:", stats["status_codes"].get(5, 0))
    print("Avg response time:", sum(times) / len(times))
    print("Fastest:", min(times))
    print("Slowest:", max(times))

    plt.figure()
    plt.bar(stats["per_method"].keys(), stats["per_method"].values())
    plt.title("Requests per HTTP Method")
    plt.show()

    plt.figure()
    plt.hist(times, bins=10)
    plt.title("Response Time Distribution")
    plt.show()

if __name__ == "__main__":
    users_by_city(str(input("Enter city name to filter users: ")))
    create_post()
    update_post()
    delete_post()
    show_statistics()