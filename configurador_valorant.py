import os
import re
import sys
import msvcrt

# Clase para manejar colores
class Color:
    VERDE = '\033[92m'
    AMARILLO = '\033[93m'
    ROJO = '\033[91m'
    CIAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def seleccionar_idioma():
    """Menú interactivo con flechas de arriba/abajo"""
    os.system('') 
    opciones = ["English", "Español"]
    seleccion = 0
    
    while True:
        os.system('cls')
        print(f"{Color.CIAN}Select Language / Selecciona Idioma:{Color.RESET}")
        print(f"{Color.AMARILLO}(Use ↑/↓ arrows and press ENTER / Usa flechas ↑/↓ y presiona ENTER){Color.RESET}\n")
        
        for i, opcion in enumerate(opciones):
            if i == seleccion:
                print(f"{Color.VERDE} > {Color.BOLD}{opcion}{Color.RESET}")
            else:
                print(f"   {opcion}")
        
        key = msvcrt.getch()
        if key == b'\r': 
            break
        elif key == b'\xe0': 
            key = msvcrt.getch()
            if key == b'H': # Arriba
                seleccion = (seleccion - 1) % len(opciones)
            elif key == b'P': # Abajo
                seleccion = (seleccion + 1) % len(opciones)

    if seleccion == 1: # Español
        return {
            "titulo": "VALORANT STRETCHED RESOLUTION CONFIGURATOR (4:3)",
            "cuenta_ok": "✅ Cuenta activa detectada:",
            "err_ruta": "❌ Error: No se encontró la ruta de configuración activa.",
            "menu_tit": "📌 LISTA DE RESOLUCIONES 4:3 RECOMENDADAS",
            "col_x": "ANCHO (X)",
            "col_y": "ALTO (Y)",
            "col_uso": "CALIDAD / USO",
            "res_alta_2k": "Alta / 2K",
            "res_alta_std": "Alta / Estándar",
            "res_ideal": "Ideal para monitores 1080p",
            "res_popular": "Equilibrada / Popular",
            "res_media": "Calidad Media",
            "res_baja": "Baja / Rendimiento FPS",
            "res_extrema": "Extrema / PC de bajos recursos",
            "res_minima": "Mínima",
            "ctrl_c": "💡 Presiona Ctrl + C en cualquier momento para cancelar.",
            "input_x": "👉 Ingresa el ANCHO (X) deseado: ",
            "input_y": "👉 Ingresa el ALTO (Y) deseado:  ",
            "err_num": "❌ Error: ¡Debes ingresar solo números!",
            "exito": "🚀 ¡Éxito! Archivo actualizado sin duplicados.",
            "importante": "💡 IMPORTANTE: Verifica la escala en el panel de NVIDIA/AMD.",
            "cancelado": "⚠️ Operación cancelada con éxito.",
            "finalizar": "Presiona Enter para finalizar..."
        }
    else: # English
        return {
            "titulo": "VALORANT STRETCHED RESOLUTION CONFIGURATOR (4:3)",
            "cuenta_ok": "✅ Active account detected:",
            "err_ruta": "❌ Error: Active configuration path not found.",
            "menu_tit": "📌 RECOMMENDED 4:3 RESOLUTIONS LIST",
            "col_x": "WIDTH (X)",
            "col_y": "HEIGHT (Y)",
            "col_uso": "QUALITY / USAGE",
            "res_alta_2k": "High / 2K",
            "res_alta_std": "High / Standard",
            "res_ideal": "Ideal for 1080p monitors",
            "res_popular": "Balanced / Popular",
            "res_media": "Medium Quality",
            "res_baja": "Low / FPS Performance",
            "res_extrema": "Extreme / Low-end PC",
            "res_minima": "Minimum",
            "ctrl_c": "💡 Press Ctrl + C at any time to cancel.",
            "input_x": "👉 Enter desired WIDTH (X): ",
            "input_y": "👉 Enter desired HEIGHT (Y): ",
            "err_num": "❌ Error: You must enter numbers only!",
            "exito": "🚀 Success! File updated without duplicates.",
            "importante": "💡 IMPORTANT: Check scaling in NVIDIA/AMD panel.",
            "cancelado": "⚠️ Operation successfully cancelled.",
            "finalizar": "Press Enter to finish..."
        }

TXT = {}

def obtener_ruta_activa():
    local_appdata = os.environ.get('LOCALAPPDATA')
    ruta_riot_local = os.path.join(local_appdata, 'VALORANT', 'Saved', 'Config', 'WindowsClient', 'RiotLocalMachine.ini')
    if not os.path.exists(ruta_riot_local): return None
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
                    print(f"{Color.VERDE}{TXT['cuenta_ok']}{Color.RESET} {Color.CIAN}{carpeta}{Color.RESET}")
                    return ruta_final
    return None

def mostrar_menu_resoluciones():
    print(f"\n{Color.BOLD} {TXT['menu_tit']}{Color.RESET}")
    print("-" * 75)
    print(f"{Color.CIAN}{TXT['col_x']:<12} | {TXT['col_y']:<10}{Color.RESET} | {TXT['col_uso']}")
    print("-" * 75)
    print(f"{'1920':<12} x {'1440':<10} | {TXT['res_alta_2k']}")
    print(f"{'1600':<12} x {'1200':<10} | {TXT['res_alta_std']}")
    print(f"{'1440':<12} x {'1080':<10} | {Color.VERDE}{TXT['res_ideal']}{Color.RESET}")
    print(f"{'1280':<12} x {'960':<10} | {Color.AMARILLO}{TXT['res_popular']}{Color.RESET}")
    print(f"{'1152':<12} x {'864':<10} | {TXT['res_media']}")
    print(f"{'1024':<12} x {'768':<10} | {TXT['res_baja']}")
    print(f"{'800':<12} x {'600':<10} | {TXT['res_extrema']}")
    print(f"{'640':<12} x {'480':<10} | {TXT['res_minima']}")
    print("-" * 75)
    print(f"{Color.AMARILLO}{TXT['ctrl_c']}{Color.RESET}\n")

def actualizar_o_insertar(contenido, clave, valor, ancla=None):
    if re.search(rf'^{clave}=.*', contenido, re.MULTILINE):
        return re.sub(rf'^{clave}=.*', f'{clave}={valor}', contenido, flags=re.MULTILINE)
    else:
        if ancla and re.search(rf'^{ancla}=.*', contenido, re.MULTILINE):
            return re.sub(rf'^({ancla}=.*)', rf'\1\n{clave}={valor}', contenido, flags=re.MULTILINE)
        return contenido.replace('[/Script/Engine.GameUserSettings]', f'{clave}={valor}\n\n[/Script/Engine.GameUserSettings]')

def modificar_archivo():
    global TXT
    try:
        TXT = seleccionar_idioma()
        os.system('cls')
        print(f"{Color.CIAN}{'='*65}{Color.RESET}")
        print(f"{Color.BOLD}      {TXT['titulo']}{Color.RESET}")
        print(f"{Color.CIAN}{'='*65}{Color.RESET}")
        ruta_archivo = obtener_ruta_activa()
        if not ruta_archivo:
            print(f"\n{Color.ROJO}{TXT['err_ruta']}{Color.RESET}")
            input(f"\n{TXT['finalizar']}")
            return
        mostrar_menu_resoluciones()
        x = input(f"{Color.BOLD}{TXT['input_x']}{Color.RESET}").strip()
        y = input(f"{Color.BOLD}{TXT['input_y']}{Color.RESET}").strip()
        if not x.isdigit() or not y.isdigit():
            print(f"\n{Color.ROJO}{TXT['err_num']}{Color.RESET}")
            input(f"{TXT['finalizar']}")
            return
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        params = {
            'bShouldLetterbox': 'False', 'bLastConfirmedShouldLetterbox': 'False',
            'bUseVSync': 'False', 'bUseDynamicResolution': 'False',
            'ResolutionSizeX': x, 'ResolutionSizeY': y,
            'LastUserConfirmedResolutionSizeX': x, 'LastUserConfirmedResolutionSizeY': y,
            'WindowPosX': '0', 'WindowPosY': '0',
            'LastConfirmedFullscreenMode': '2', 'PreferredFullscreenMode': '0',
            'AudioQualityLevel': '0', 'LastConfirmedAudioQualityLevel': '0'
        }
        for clave, valor in params.items():
            contenido = actualizar_o_insertar(contenido, clave, valor)
        contenido = actualizar_o_insertar(contenido, 'FullscreenMode', '2', ancla='HDRDisplayOutputNits')
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
        print(f"\n{Color.VERDE}{TXT['exito']}{Color.RESET}")
        print(f"{Color.AMARILLO}{TXT['importante']}{Color.RESET}")
        input(f"\n{TXT['finalizar']}")
    except KeyboardInterrupt:
        print(f"\n\n{Color.ROJO}{TXT['cancelado']}{Color.RESET}")
        sys.exit()

if __name__ == "__main__":
    modificar_archivo()
