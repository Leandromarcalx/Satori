from src.json_parser import load_json_data
import os

file_path = "../data/raw/user_data_tiktok.json"
if os.path.exists(file_path):
    print(f"File found: {file_path}")
    data = load_json_data(file_path)
    if data:
        print("Data loaded successfully.")
        # Check structure
        chat_history = None
        if "Direct Message" in data and "ChatHistory" in data["Direct Message"]:
             chat_history = data["Direct Message"]["ChatHistory"]
        elif "Direct Message" in data and "Direct Messages" in data["Direct Message"]:
             if "ChatHistory" in data["Direct Message"]["Direct Messages"]:
                 chat_history = data["Direct Message"]["Direct Messages"]["ChatHistory"]
        
        if chat_history:
            print(f"Found {len(chat_history)} chats.")
            print("First 5 chats:")
            chats = list(chat_history.keys())
            for i, name in enumerate(chats[:5]):
                print(f"- {name}")
                
            # Test extraction on the first chat
            target_chat = chats[1] # Use the second one (felipegsouza) as it had links in the snippet
            print(f"\nTesting extraction on: {target_chat}")
            messages = chat_history[target_chat]
            
            from src.json_parser import extract_links_from_json
            # Pass data and name, OR just call extraction on the messages if functionality was exposed, 
            # but extract_links_from_json takes (data, target_chat_name)
            
            links = extract_links_from_json(data, target_chat)
            print(f"Extracted {len(links)} links.")
            if links:
                print(f"Sample: {links[0]}")
        else:
            print("ChatHistory not found in expected structure.")
    else:
        print("Failed to parse JSON.")
else:
    print(f"File NOT found: {file_path}")
