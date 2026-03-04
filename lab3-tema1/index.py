import requests
import time
import matplotlib.pyplot as plt
import urllib
import argparse
import json
import os
from collections import defaultdict

BASE_URL = "https://jsonplaceholder.typicode.com"
STATS_FILE = "stats.json"

stats = {
    "total_requests": 0,
    "per_endpoint": defaultdict(int),
    "per_method": defaultdict(int),
    "status_codes": defaultdict(int),
    "response_times": []
}

def load_stats():
    global stats
    if os.path.exists(STATS_FILE):
        with open(STATS_FILE, "r") as f:
            data = json.load(f)
            stats["total_requests"] = data.get("total_requests", 0)
            stats["per_endpoint"] = defaultdict(int, data.get("per_endpoint", {}))
            stats["per_method"] = defaultdict(int, data.get("per_method", {}))
            stats["status_codes"] = defaultdict(int, data.get("status_codes", {}))
            stats["response_times"] = data.get("response_times", [])

def save_stats():
    with open(STATS_FILE, "w") as f:
        json.dump({
            "total_requests": stats["total_requests"],
            "per_endpoint": dict(stats["per_endpoint"]),
            "per_method": dict(stats["per_method"]),
            "status_codes": dict(stats["status_codes"]),
            "response_times": stats["response_times"]
        }, f, indent=2)

def tracked_request(method, url, **kwargs):
    start = time.time()
    response = requests.request(method, url, **kwargs)
    elapsed = time.time() - start

    stats["total_requests"] += 1
    stats["per_endpoint"][url.split("?")[0]] += 1
    stats["per_method"][method] += 1
    stats["status_codes"][str(response.status_code // 100)] += 1
    stats["response_times"].append(elapsed)
    save_stats()

    return response

#Ex1
def users_by_city(city):
    response = tracked_request("GET", f"{BASE_URL}/users?address.city={urllib.parse.quote(city)}")
    users = response.json()

    print("\nUsers in city:", city)
    if len(users) < 1:
        print("No users found.")
        return

    for user in users:
        print(f'{user["name"]} - {user["email"]}')

#Ex2
def create_post():
    try:
        user_id = int(input("User ID: "))
    except ValueError:
        print("Invalid input. Please enter a numeric User ID.")
        return create_post()
    
    while True:
        title = input("Title: ")
        response = tracked_request("GET", f"{BASE_URL}/posts?title={urllib.parse.quote(title)}")
        existing_posts = response.json()
        if not existing_posts:
            break
        print("Title already exists. Choose another.")

    body = input("Body: ")

    response = tracked_request(
        "POST",
        f"{BASE_URL}/posts",
        json={"userId": user_id, "title": title, "body": body}
    )

    print("Created post:", response.json())

#Ex3
def update_post():
    try:
        post_id = int(input("Post ID to update: "))
    except ValueError:
        print("Invalid input. Please enter a numeric Post ID.")
        return update_post()

    choice = input("Update (title/body/both): ").lower()

    data = {}
    if choice in ("title", "both"):
        data["title"] = input("New title: ")
    if choice in ("body", "both"):
        data["body"] = input("New body: ")

    if not data:
        print("Invalid choice. Please enter 'title', 'body' or 'both'.")
        return update_post()

    headers = {"Authorization": "fake-token-12345"}

    response = tracked_request(
        "PATCH",
        f"{BASE_URL}/posts/{post_id}",
        json=data,
        headers=headers
    )

    print("Updated post:", response.json())

#Ex4
def delete_post():
    while True:
        try:
            post_id = int(input("Post ID to delete: "))
        except ValueError:
            print("Invalid input. Please enter a numeric Post ID.")
            delete_post()
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

#Ex5
def show_statistics():
    times = stats["response_times"]

    if not times:
        print("No statistics available yet. Make at least one request first.")
        return

    fig = plt.figure(figsize=(10, 6))
    
    ax_text = plt.subplot(2, 1, 1)
    ax_text.axis('off')
    
    stats_text = f"""=== STATISTICS ===
    Total requests: {stats['total_requests']}
    Per endpoint: {', '.join(f"{k.replace('https://jsonplaceholder.typicode.com', '')} ({v})" for k, v in stats['per_endpoint'].items())}
    2xx: {stats['status_codes'].get('2', 0)}
    4xx: {stats['status_codes'].get('4', 0)}
    5xx: {stats['status_codes'].get('5', 0)}
    Avg response time: {sum(times) / len(times):.3f}s, out of {len(times)} requests
    Fastest: {min(times):.3f}s
    Slowest: {max(times):.3f}s"""
    
    ax_text.text(0.05, 0.95, stats_text, transform=ax_text.transAxes,
                 fontfamily='monospace', fontsize=9, verticalalignment='top',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax_chart = plt.subplot(2, 1, 2)
    bars = ax_chart.bar(stats["per_method"].keys(), stats["per_method"].values())
    ax_chart.set_title("Requests per HTTP Method")
    ax_chart.set_xlabel("HTTP Method")
    ax_chart.set_ylabel("Number of requests")
    ax_chart.grid(axis="y", alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax_chart.text(bar.get_x() + bar.get_width()/2., height,
                     f'{int(height)}',
                     ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    load_stats()
    
    parser = argparse.ArgumentParser(description="API interaction tool for JSONPlaceholder")
    parser.add_argument("--city", type=str, help="City name to filter users")
    parser.add_argument("--create-post", action="store_true", help="Create a new post")
    parser.add_argument("--update-post", action="store_true", help="Update an existing post")
    parser.add_argument("--delete-post", action="store_true", help="Delete a post")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
    else:
        if args.city:
            users_by_city(args.city)
        
        if args.create_post:
            create_post()
        
        if args.update_post:
            update_post()
        
        if args.delete_post:
            delete_post()
        
        if args.stats:
            show_statistics()