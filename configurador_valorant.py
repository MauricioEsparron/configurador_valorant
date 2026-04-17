import os
import re
import sys

# Clase para manejar colores en la consola
class Color:
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    ROJO = '\033[91m'
    CIAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

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
                    print(f"{Color.VERDE} Cuenta activa detectada:{Color.RESET} {Color.CIAN}{carpeta}{Color.RESET}")
                    return ruta_final
    return None

def mostrar_menu_resoluciones():
    print(f"\n{Color.BOLD} LISTA DE RESOLUCIONES 4:3 RECOMENDADAS{Color.RESET}")
    print("-" * 65)
    print(f"{Color.CIAN}{'ANCHO (X)':<12} | {'ALTO (Y)':<10}{Color.RESET} | {'CALIDAD / USO'}")
    print("-" * 65)
    print(f"{'1920':<12} x {'1440':<10} | Alta / 2K")
    print(f"{'1600':<12} x {'1200':<10} | Alta / Estándar")
    print(f"{'1440':<12} x {'1080':<10} | Ideal para monitores 1080p")
    print(f"{'1280':<12} x {'960':<10} | Equilibrada / Popular")
    print(f"{'1152':<12} x {'864':<10} | Calidad Media")
    print(f"{'1024':<12} x {'768':<10} | Baja / Rendimiento FPS")
    print(f"{'800':<12} x {'600':<10} | Extrema / PC de bajos recursos")
    print(f"{'640':<12} x {'480':<10} | Mínima")
    print("-" * 65)
    print(f"{Color.AMARILLO}💡 Presiona Ctrl + C en cualquier momento para cancelar.{Color.RESET}\n")

def modificar_archivo():
    # Habilitar colores en consolas de Windows antiguas
    os.system('') 
    
    try:
        print(f"{Color.CIAN}{'='*65}{Color.RESET}")
        print(f"{Color.BOLD}      VALORANT STRETCHED RESOLUTION CONFIGURATOR (4:3){Color.RESET}")
        print(f"{Color.CIAN}{'='*65}{Color.RESET}")
        
        ruta_archivo = obtener_ruta_activa()
        
        if not ruta_archivo:
            print(f"\n{Color.ROJO}❌ Error: No se encontró la ruta de configuración activa.{Color.RESET}")
            input("\nPresiona Enter para salir...")
            return

        mostrar_menu_resoluciones()

        x = input(f"{Color.BOLD}👉 Ingresa el ANCHO (X): {Color.RESET}").strip()
        y = input(f"{Color.BOLD}👉 Ingresa el ALTO (Y):  {Color.RESET}").strip()

        if not x.isdigit() or not y.isdigit():
            print(f"\n{Color.ROJO}❌ Error: ¡Debes ingresar solo números!{Color.RESET}")
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
        
        print(f"\n{Color.VERDE}🚀 ¡Éxito! Archivo actualizado a {x}x{y}.{Color.RESET}")
        print(f"{Color.AMARILLO}💡 IMPORTANTE: Verifica la escala en el panel de NVIDIA/AMD.{Color.RESET}")
        input("\nPresiona Enter para finalizar...")

    except KeyboardInterrupt:
        print(f"\n\n{Color.ROJO}⚠️ Operación cancelada con éxito por el usuario.{Color.RESET}")
        sys.exit()

if __name__ == "__main__":
    modificar_archivo()