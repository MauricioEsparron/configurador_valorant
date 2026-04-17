import os
import re

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

def modificar_archivo():
    
    os.system('') 
    
    try:
        print(f"{'='*65}")
        print(f"VALORANT STRETCHED RESOLUTION CONFIGURATOR (4:3)")
        print(f"{'='*65}")
        
        ruta_archivo = obtener_ruta_activa()
        
        if not ruta_archivo:
            print(f"\n❌ Error: No se encontró la ruta de configuración activa.")
            input("\nPresiona Enter para salir...")
            return

        mostrar_menu_resoluciones()

        x = input(f"👉 Ingresa el ANCHO (X): ").strip()
        y = input(f"👉 Ingresa el ALTO (Y):  ").strip()

        if not x.isdigit() or not y.isdigit():
            print(f"\n ❌ Error: ¡Debes ingresar solo números!")
            input("Presiona Enter para reintentar...")
            return

        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()

        # --- PROCESAMIENTO ---
        for flag in ['bShouldLetterbox', 'bLastConfirmedShouldLetterbox', 'bUseVSync', 'bUseDynamicResolution']:
            contenido = re.sub(rf'{flag}=.*', f'{flag}=False', contenido)

        contenido = re.sub(r'ResolutionSizeX=.*', f'ResolutionSizeX={x}', contenido)
        contenido = re.sub(r'ResolutionSizeY=.*', f'ResolutionSizeY={y}', contenido)
        contenido = re.sub(r'LastUserConfirmedResolutionSizeX=.*', f'LastUserConfirmedResolutionSizeX={x}', contenido)
        contenido = re.sub(r'LastUserConfirmedResolutionSizeY=.*', f'LastUserConfirmedResolutionSizeY={y}', contenido)

        contenido = re.sub(r'WindowPosX=.*', 'WindowPosX=0', contenido)
        contenido = re.sub(r'WindowPosY=.*', 'WindowPosY=0', contenido)
        contenido = re.sub(r'LastConfirmedFullscreenMode=.*', 'LastConfirmedFullscreenMode=2', contenido)
        contenido = re.sub(r'PreferredFullscreenMode=.*', 'PreferredFullscreenMode=0', contenido)

        if "FullscreenMode=2" not in contenido:
            contenido = re.sub(r'(HDRDisplayOutputNits=1000)', r'\1\nFullscreenMode=2', contenido)
        else:
            contenido = re.sub(r'FullscreenMode=.*', 'FullscreenMode=2', contenido)

        patron_scal = r'\[ScalabilityGroups\].*?(?=\n\[|$)'
        nuevo_scal = (
            "[ScalabilityGroups]\nsg.ResolutionQuality=65.000000\nsg.ViewDistanceQuality=0\n"
            "sg.AntiAliasingQuality=0\nsg.ShadowQuality=0\nsg.PostProcessQuality=0\n"
            "sg.TextureQuality=0\nsg.EffectsQuality=0\nsg.FoliageQuality=0\n"
            "sg.ShadingQuality=0\nsg.GlobalIlluminationQuality=0\nsg.ReflectionQuality=0"
        )
        contenido = re.sub(patron_scal, nuevo_scal, contenido, flags=re.DOTALL)

        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"\n ¡Éxito! Archivo actualizado a {x}x{y}.")
        print(f"💡 IMPORTANTE: Verifica la escala en el panel de NVIDIA/AMD.")
        input("\nPresiona Enter para finalizar...")

    except KeyboardInterrupt:
        print(f"\n\n⚠️ Operación cancelada con éxito por el usuario.")
        sys.exit()

if __name__ == "__main__":
    modificar_archivo()