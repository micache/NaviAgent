import requests
import json
import time
from reception.config import settings

def test_api():
    """Test the API with a sample conversation flow"""
    
    BASE_URL = f"http://{settings.host}:{settings.port}{settings.api_prefix}"
    
    print("="*80)
    print("Testing NaviAgent Reception API")
    print("="*80)
    
    try:
        # 1. Start session
        print("\n1. Starting session...")
        response = requests.post(f"{BASE_URL}/session/start")
        data = response.json()
        session_id = data["session_id"]
        print(f"   Session ID: {session_id}")
        print(f"   Greeting: {data['message']}")
        
        # 2. Chat - Send messages
        messages = [
            "Hanoi, Vietnam",
            "Seoul",
            "5 days",
            "2 people",
            "20 million VND",
            "Food and shopping",
            "No special requirements",
            "yes"  # Confirm
        ]
        
        for i, msg in enumerate(messages, 1):
            print(f"\n{i+1}. Sending message: '{msg}'")
            response = requests.post(f"{BASE_URL}/chat", json={
                "session_id": session_id,
                "message": msg
            })
            data = response.json()
            print(f"   Agent: {data['agent_message'][:100]}...")
            print(f"   Complete: {data['is_complete']}, Confirmed: {data['is_confirmed']}")
            
            if data['is_confirmed']:
                print("\n   Conversation confirmed! Stopping.")
                break
            
            time.sleep(1)
        
        # 3. Get metadata
        print("\n3. Getting final metadata...")
        response = requests.get(f"{BASE_URL}/session/{session_id}/metadata")
        data = response.json()
        print(f"   Metadata:")
        print(json.dumps(data['metadata'], indent=4, ensure_ascii=False))
        
        # 4. End session
        print("\n4. Ending session...")
        response = requests.delete(f"{BASE_URL}/session/{session_id}")
        print(f"   {response.json()['message']}")
        
        print("\n" + "="*80)
        print("Test completed successfully!")
        print("="*80)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Cannot connect to API server.")
        print("Please make sure the server is running with: python -m reception.main")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api()
