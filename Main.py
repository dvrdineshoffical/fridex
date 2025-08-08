import os
import pymongo
import wikipediaapi
import time
from datetime import datetime

print("Starting learning core...")

# --- Setup ---
# Railway secrets se connection string lein
MONGO_CONNECTION_STRING = os.environ.get("MONGO_CONNECTION_STRING")
if not MONGO_CONNECTION_STRING:
    print("Error: MONGO_CONNECTION_STRING not found!")
    exit()

try:
    client = pymongo.MongoClient(MONGO_CONNECTION_STRING)
    # Ping the server to check the connection
    client.admin.command('ping')
    print("MongoDB connection successful!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit()

db = client['friday_memory_db']
knowledge_collection = db['knowledge_collection']

# Wikipedia setup (Hindi me)
# Aap 'hi' (Hindi) ya 'en' (English) chun sakte hain
wiki_wiki = wikipediaapi.Wikipedia(
    user_agent='FridayAI/1.0 (dineshkumarbamanpuri@gmail.com)',
    language='hi',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)

def learn_from_wikipedia():
    try:
        # Wikipedia ke mukhya page se "Kya aap jaante hain..." section lein
        main_page = wiki_wiki.page("मुखपृष्ठ") # Hindi main page
        
        if main_page.exists():
            # Yeh section aam taur par roz badalta hai
            did_you_know_section = main_page.section_by_title("क्या आप जानते हैं...")
            
            if did_you_know_section:
                # Har naye tathy ko alag se save karein
                for line in did_you_know_section.text.split('\n'):
                    fact = line.strip()
                    if fact and len(fact) > 20: # Chhoti lines ko ignore karein
                        # Check karein ki yeh tathy pehle se save to nahi hai
                        if knowledge_collection.count_documents({'summary': fact}) == 0:
                            knowledge_entry = {
                                "source": "wikipedia_dyk",
                                "summary": fact,
                                "timestamp": datetime.utcnow()
                            }
                            knowledge_collection.insert_one(knowledge_entry)
                            print(f"Naya gyaan prapt hua: '{fact}'")
                        else:
                            print(f"Gyaan pehle se hai: '{fact}'")
            else:
                print("Wikipedia par 'Kya aap jaante hain...' section nahi mila.")
        else:
            print("Wikipedia ka mukhya page nahi mila.")
    except Exception as e:
        print(f"Wikipedia se seekhne me error: {e}")

# --- Mukhya Loop ---
while True:
    print(f"\nLast checked at: {datetime.now()}")
    learn_from_wikipedia()
    # Har 6 ghante me naya gyaan khojega
    sleep_duration = 6 * 60 * 60
    print(f"Ab {sleep_duration / 3600} ghante ke liye so raha hoon...")
    time.sleep(sleep_duration)
