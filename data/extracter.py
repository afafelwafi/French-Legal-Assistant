import os
import nest_asyncio
import asyncio
import json
from pylegifrance import LegiHandler, recherche_CODE
from config import PISTE_API_CLIENT_ID, PISTE_API_CLIENT_SECRET, CODES, FOLDER_NAME

nest_asyncio.apply()


# Initialisation client Legifrance

client = LegiHandler()
client.set_api_keys(
    legifrance_api_key=PISTE_API_CLIENT_ID,
    legifrance_api_secret=PISTE_API_CLIENT_SECRET,
)


os.makedirs(FOLDER_NAME, exist_ok=True)


async def fetch_and_save_code(code_name):
    try:
        print(f"🔎 Téléchargement de : {code_name}")
        data = recherche_CODE(code_name=code_name, formatter=True)
        if data:
            filename = os.path.join(
                FOLDER_NAME,
                f"{code_name.replace(' ', '_').replace('(', '').replace(')', '').lower()}.json",
            )
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ Sauvé : {filename}")
        else:
            print(f"⚠️ Aucun contenu trouvé pour : {code_name}")
    except Exception as e:
        print(f"❌ Erreur pour {code_name} : {str(e)}")


async def main():
    tasks = [fetch_and_save_code(code) for code in codes]
    await asyncio.gather(*tasks)


# Launch the event loop
if __name__ == "__main__":
    asyncio.run(main())
    print(f"📁 All files are located in the folder: {FOLDER_NAME}/")
