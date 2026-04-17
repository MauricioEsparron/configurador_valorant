import os
import re
import sys

def obtener_ruta_activa():
    local_appdata = os.environ.get('LOCALAPPDATA')
    ruta_riot_local = os.path.join(local_appdata, 'VALORANT', 'Saved', 'Config', 'WindowsClient', 'RiotLocalMachine.ini')
    
    if not os.path.exists(ruta_riot_local):
        return None

    last_user_id = None
    for enc in ['utf-16', 'utf-8-sig', 'utf-8']:
        try:
            with open(ruta_riot_local, 'r', encoding=enc) as f:
                match = re.search(r'LastKnownUser=(.*)', f.read())
                if match:
                    last_user_id = match.group(1).strip()
                    break
        except: continue

    if not last_user_id: return None

    id_query = re.sub(r'[^a-zA-Z0-9]', '', last_user_id).lower()
    base_config_path = os.path.join(local_appdata, 'VALORANT', 'Saved', 'Config')
    
    if os.path.exists(base_config_path):
        for carpeta in os.listdir(base_config_path):
            carpeta_limpia = re.sub(r'[^a-zA-Z0-9]', '', carpeta).lower()
            if id_query in carpeta_limpia:
                ruta_final = os.path.join(base_config_path, carpeta, 'WindowsClient', 'GameUserSettings.ini')
                if os.path.exists(ruta_final):
                    print(f"Cuenta activa detectada: {carpeta}")
                    return ruta_final
    return None

print(f"Resultado: {obtener_ruta_activa()}")