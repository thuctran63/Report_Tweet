import json
import random
import string
import time
import requests
import yaml

max_report_times = 3
max_scroll_times = 5
time_report_per_link = 5
key = "chudai"

def load_settings_from_yml(file_path):
    global max_report_times, max_scroll_times, time_report_per_link, key
    with open(file_path, 'r', encoding='utf-8') as file:
        settings = yaml.safe_load(file)
        # Truy cập vào mục 'setting' trong YAML
        setting = settings.get('setting', {})
        max_report_times = setting.get('max_report_times', 3)
        max_scroll_times = setting.get('max_scroll_times', 5)
        time_report_per_link = setting.get('time_report_per_link', 5)
        key = setting.get('key', 'chudai')

def generate_random_string():
    # Generate random hexadecimal segments
    segment1 = ''.join(random.choices(string.hexdigits.lower(), k=8))
    segment2 = ''.join(random.choices(string.hexdigits.lower(), k=4))
    segment3 = ''.join(random.choices(string.hexdigits.lower(), k=4))
    segment4 = ''.join(random.choices(string.hexdigits.lower(), k=3))
    segment5 = ''.join(random.choices(string.hexdigits.lower(), k=12))
    
    # Combine into the desired format
    result = f"{segment1}-{segment2}-{segment3}-{segment4}-{segment5}"
    return result

def convert_twitter_to_x(url):
    # Tách các phần của URL
    parts = url.split("/")
    
    # Kiểm tra xem URL có đủ các phần cần thiết
    if len(parts) > 5:
        # Tạo URL mới với domain x.com và bỏ phần video/1
        new_url = f"https://x.com/{parts[3]}/status/{parts[5]}"
        return new_url
    else:
        return "URL không hợp lệ"
    
def find_objects_with_cursor(data, target_key = "cursorType", target_value = "Bottom"):
    results = []
    if isinstance(data, dict):  # If the data is a dictionary
        for key, value in data.items():
            if key == target_key and value == target_value:
                results.append(data)
            else:
                results.extend(find_objects_with_cursor(value, target_key, target_value))
    elif isinstance(data, list):  # If the data is a list
        for item in data:
            results.extend(find_objects_with_cursor(item, target_key, target_value))
    return results

def report_tweet(reported_tweet_id, reported_user_id, list_acc_check, time_report_per_link = 5):
    global max_report_times, max_scroll_times
    url = "https://x.com/i/api/1.1/report/flow.json?flow_name=report-flow"
    # Kiểm tra xem có tài khoản nào còn có thể report không
    times = 0
    list_acc_had_reported = []
    while times < time_report_per_link:
        while True:
            # chọn random một tài khoản
            if len(list_acc_check) == 0:
                print("All accounts have reached the maximum number of reports.")
                return
            acc_check = random.choice(list_acc_check)
            if acc_check["report_times"] < max_report_times and acc_check not in list_acc_had_reported:
                list_acc_had_reported.append(acc_check)
                acc_check["report_times"] += 1
                break
            else:
                list_acc_check.remove(acc_check)

        # Headers (đảm bảo rằng bạn có xác thực nếu cần)
        headers = {
                    "Content-Type": "application/json",
                    "Authorization": acc_check["bearer_token"],  # Bearer token từ tài khoản
                    "x-csrf-token": acc_check["csrf_token"],    # CSRF token từ tài khoản
                    "Cookie": acc_check["cookie"]                # Cookie từ tài khoản
                    }
        
        report_flow_id = generate_random_string()
        # Payload data
        payload = {
        "input_flow_data": {
            "requested_variant": "{\"client_app_id\":\"3033300\",\"client_location\":\"search:search_filter_top:result\",\"client_referer\":\"/search\",\"is_media\":true,\"is_promoted\":false,\"report_flow_id\":\"{report_flow_id}\",\"reported_tweet_id\":\"{reported_tweet_id}\",\"reported_user_id\":\"{reported_user_id}\",\"source\":\"reporttweet\"}",
            "flow_context": {
                "debug_overrides": {},
                "start_location": {
                    "location": "search",
                    "search": {
                        "query": key,
                        "social_filter": "all",
                        "near": "anywhere"
                    }
                }
            }
        },
        "subtask_versions": {
            "action_list": 2,
            "alert_dialog": 1,
            "app_download_cta": 1,
            "check_logged_in_account": 1,
            "choice_selection": 3,
            "contacts_live_sync_permission_prompt": 0,
            "cta": 7,
            "email_verification": 2,
            "end_flow": 1,
            "enter_date": 1,
            "enter_email": 2,
            "enter_password": 5,
            "enter_phone": 2,
            "enter_recaptcha": 1,
            "enter_text": 5,
            "enter_username": 2,
            "generic_urt": 3,
            "in_app_notification": 1,
            "interest_picker": 3,
            "js_instrumentation": 1,
            "menu_dialog": 1,
            "notifications_permission_prompt": 2,
            "open_account": 2,
            "open_home_timeline": 1,
            "open_link": 1,
            "phone_verification": 4,
            "privacy_options": 1,
            "security_key": 3,
            "select_avatar": 4,
            "select_banner": 2,
            "settings_list": 7,
            "show_code": 1,
            "sign_up": 2,
            "sign_up_review": 4,
            "tweet_selection_urt": 1,
            "update_users": 1,
            "upload_media": 1,
            "user_recommendations_list": 4,
            "user_recommendations_urt": 1,
            "wait_spinner": 3,
            "web_modal": 1
            }
        }

        # Thay thế {report_flow_id} trong requested_variant
        payload["input_flow_data"]["requested_variant"] = payload["input_flow_data"]["requested_variant"].replace("{report_flow_id}", report_flow_id)
        # Thay thế {reported_tweet_id} trong requested_variant
        payload["input_flow_data"]["requested_variant"] = payload["input_flow_data"]["requested_variant"].replace("{reported_tweet_id}", reported_tweet_id)
        # Thay thế {reported_user_id} trong requested_variant
        payload["input_flow_data"]["requested_variant"] = payload["input_flow_data"]["requested_variant"].replace("{reported_user_id}", reported_user_id)

        # Send POST request
        response = requests.post(url, headers=headers, json=payload)
        flow_token = None
        # Output response
        if response.status_code == 200:
            print("Request flow 1 successful!")
            # lấy ra flow_token từ response
            response_json = response.json()
            flow_token = response_json["flow_token"]
        else:
            print("Failed to send request.")
            print(f"Status Code: {response.status_code}")
            print(response.text)
        
        url = "https://x.com/i/api/1.1/report/flow.json"
        payload = {
            "flow_token": "{flow_token}",
            "subtask_inputs": [
                {
                    "subtask_id": "single-selection",
                    "choice_selection": {
                        "link": "next_link",
                        "selected_choices": [
                            "SpammedOption"
                        ]
                    }
                }
            ]
        }

        # Thay thế {flow_token} trong payload
        payload["flow_token"] = flow_token

        response = requests.post(url, headers=headers, json=payload)

        # Output response
        if response.status_code == 200:
            print(f"Report spam post id {reported_tweet_id} successfully. Số lần report: {times + 1}")
        else:
            print("Failed to send request.")
            print(f"Status Code: {response.status_code}")
            print(response.text)

def get_info_tweet_reports(list_acc_check):
    global max_report_times, max_scroll_times
    # URL endpoint
    url = "https://x.com/i/api/graphql/UN1i3zUiCWa-6r-Uaho4fw/SearchTimeline"

    # Các tham số variables (được mã hóa dưới dạng JSON)
    variables = {
        "rawQuery": 'chudai' ,       # Từ khóa tìm kiếm
        "count": 100,          # Số kết quả muốn lấy
        "querySource": "typed_query",  # Nguồn tìm kiếm, có thể là "typed_query" hoặc khác
        "product": "Top"       # Loại sản phẩm tìm kiếm
    }
    info_reports = {}
    # Các tính năng bổ sung trong API request
    features = {
        "rweb_tipjar_consumption_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "communities_web_enable_tweet_community_results_fetch": True,
        "c9s_tweet_anatomy_moderator_badge_enabled": True,
        "articles_preview_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "creator_subscriptions_quote_tweet_preview_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "rweb_video_timestamps_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_enhance_cards_enabled": False
    }

    global list_user
    
    acc_check = random.choice(list_acc_check)
    # Tham số cho request (bao gồm variables và features)
    params = {
        "variables": json.dumps(variables),
        "features": json.dumps(features)
    }
    cursor_bottom = None
    i = 0
    while True:
        headers = {
            "Content-Type": "application/json",
            "Authorization": acc_check["bearer_token"],  # Bearer token từ tài khoản
                "x-csrf-token": acc_check["csrf_token"],    # CSRF token từ tài khoản
            "Cookie": acc_check["cookie"]                # Cookie từ tài khoản
        }
        if(cursor_bottom != None):
            params["cursor"] = cursor_bottom
        # Gửi request
        response = requests.get(url, headers=headers, params=params)
        
        # Kiểm tra xem request có thành công không
        if response.status_code == 200:
            data = response.json()
            try:
                data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"][0]["entries"]
            except:
                print(f"Lỗi ck, đang chuyển sang acc khác...")
                list_acc_check.remove(acc_check)
                # chọn ngẫu nhiên 1 acc khác
                acc_check = random.choice(list_acc_check)
                print(f"Đang sử dụng tài khoản ngẫu nhiên để check...")
                continue
            for entry in data["data"]["search_by_raw_query"]["search_timeline"]["timeline"]["instructions"][0]["entries"]:
                try:
                    #content itemContent tweet_results result core user_results result legacy screen_name 
                    username = entry["content"]["itemContent"]["tweet_results"]['result']["core"]["user_results"]["result"]['legacy']['screen_name']
                    print(username)
                    if username in list_user:
                        print(f"{username} nằm trong danh sách user, bỏ qua...")
                        continue
                    tweet_id = entry["content"]["itemContent"]["tweet_results"]['result']['legacy']['id_str']
                    user_id_reports = entry["content"]["itemContent"]["tweet_results"]['result']['legacy']['user_id_str']
                    if user_id_reports not in info_reports.keys():
                        info_reports[user_id_reports] = set()
                    info_reports[user_id_reports].add(tweet_id)
                except:
                    continue
            try:
                cursor_bottom = find_objects_with_cursor(response.json())[0]["value"]
            except:
                # nếu như không còn cursor thì break
                break
            i += 1
            time.sleep(3)
            if i == max_scroll_times:
                break
        else:
            print(f"Lỗi ck, đang chuyển sang acc khác...")
            list_acc_check.remove(acc_check)
            # chọn ngẫu nhiên 1 acc khác
            acc_check = random.choice(list_acc_check)
            cursor_bottom = None
            print(f"Đang sử dụng tài khoản ngẫu nhiên để check...")

    return info_reports

load_settings_from_yml("settings.yml")

with open('acc_check.json', 'r') as file:
    list_acc_check = json.load(file)

with open('user.txt', 'r') as file:
    list_user = file.readlines()

for acc_check in list_acc_check:
    acc_check["report_times"] = 0

print("Đang lấy thông tin các tweet cần report...")
info_reports = get_info_tweet_reports(list_acc_check)
print("Đã lấy xong thông tin các tweet cần report...")
print("Đang report các tweet...")
for reported_user_id, reported_tweet_ids in info_reports.items():
    for reported_tweet_id in reported_tweet_ids:
        report_tweet(reported_tweet_id, reported_user_id, list_acc_check, time_report_per_link)

