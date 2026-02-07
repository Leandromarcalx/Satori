import json
import os

def load_json_data(file_path):
    """
    Load TikTok user data JSON.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error reading JSON: {e}")
        return None

from datetime import datetime, timedelta

def extract_links_from_json(data, target_chat_name=None, days_limit=None):
    """
    Extract video links from a specific chat in the JSON data.
    days_limit: If int, only include messages from the last N days.
    """
    try:
        # Navigate the JSON structure...
        chat_history = None
        
        # Try path 1
        if "Direct Message" in data and "ChatHistory" in data["Direct Message"]:
             chat_history = data["Direct Message"]["ChatHistory"]
             
        # Try path 2 (nested Direct Messages)
        elif "Direct Message" in data and "Direct Messages" in data["Direct Message"]:
             if "ChatHistory" in data["Direct Message"]["Direct Messages"]:
                 chat_history = data["Direct Message"]["Direct Messages"]["ChatHistory"]
        
        if not chat_history:
            print("Could not find ChatHistory in JSON.")
            return []
            
        # List available chats
        print(f"Found {len(chat_history)} chats.")
        chat_names = list(chat_history.keys())
        
        if not target_chat_name:
            chat_names.sort()
            if len(chat_names) > 50:
                print(f"There are {len(chat_names)} chats. Listing first 20...")
                for i, chat_name in enumerate(chat_names[:20]):
                    print(f"{i}: {chat_name}")
                print("...")
            else:
                print("Available chats:")
                for i, chat_name in enumerate(chat_names):
                    print(f"{i}: {chat_name}")
            
            selection = input("Enter the number, full name, or part of the name of the chat to process: ").strip()
            
            if selection.isdigit():
                idx = int(selection)
                if 0 <= idx < len(chat_names):
                    target_chat_name = chat_names[idx]
            else:
                if selection in chat_history:
                    target_chat_name = selection
                else:
                    matches = [name for name in chat_names if selection.lower() in name.lower()]
                    if len(matches) == 1:
                        target_chat_name = matches[0]
                    elif len(matches) > 1:
                        print(f"Multiple matches found for '{selection}':")
                        for i, m in enumerate(matches):
                            print(f"{i}: {m}")
                        sub_sel = input("Select index from matches (0): ") or "0"
                        if sub_sel.isdigit() and int(sub_sel) < len(matches):
                            target_chat_name = matches[int(sub_sel)]
                    else:
                        print(f"No match found for '{selection}'")
                        return []

        if target_chat_name not in chat_history:
            print(f"Chat '{target_chat_name}' not found.")
            return []
            
        print(f"Processing chat: {target_chat_name}")
        messages = chat_history[target_chat_name]
        
        # Date filtering setup
        cutoff_date = None
        if days_limit is not None:
            cutoff_date = datetime.now() - timedelta(days=days_limit)
            print(f"Filtering messages since: {cutoff_date.strftime('%Y-%m-%d')}")
        
        links = []
        msg_count = 0
        filtered_count = 0
        
        for msg in messages:
            # Date check
            if cutoff_date:
                date_str = msg.get("Date") # Format: "2026-01-16 08:36:59"
                if date_str:
                    try:
                        msg_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                        if msg_date < cutoff_date:
                            filtered_count += 1
                            continue # Skip old messages
                    except ValueError:
                        pass # If date parse fails, include it lightly or skip? Let's include specific warnings if needed, but safe to pass.

            content = msg.get("Content", "")
            # Check for tiktok links more broadly (tiktok.com, tiktokv.com, vm.tiktok.com)
            if "tiktok" in content and "video" in content:
                words = content.split()
                for word in words:
                    if "tiktok" in word and "/video/" in word:
                        links.append(word)
                        msg_count += 1
                        
        print(f"Scanned {len(messages)} messages.")
        if days_limit:
            print(f"Filtered out {filtered_count} messages older than {days_limit} days.")
            
        unique_links = list(set(links))
        print(f"Found {len(unique_links)} unique video links in JSON.")
        return unique_links

    except Exception as e:
        print(f"Error parsing JSON structure: {e}")
        return []
