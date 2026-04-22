import os
import re
import stat
import shutil
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
import sys
import ctypes
from PIL import Image, ImageTk


# 1. IDENTIDAD DE APP (Para permitir anclado)
try:
    id_app_unica = "MauricioEsparron.ConfiguradorValorant.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(id_app_unica)
except:
    pass

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def resource_path(relative_path):
    """ Obtiene la ruta absoluta del recurso para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ValorantConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("VALORANT Stretched Res Configurator")
        self.geometry("570x720") 
        self.resizable(False, False)
        
        # Icono de la ventana
        icon_path = resource_path("gato.ico")
        if os.path.exists(icon_path):
            self.wm_iconbitmap(icon_path)

        # Cargar iconos sociales
        try:
            self.img_github = ctk.CTkImage(light_image=Image.open(resource_path("github.png")), size=(28, 28))
            self.img_coffee = ctk.CTkImage(light_image=Image.open(resource_path("coffee.png")), size=(28, 28))
            self.img_stream = ctk.CTkImage(light_image=Image.open(resource_path("streamlabs.png")), size=(28, 28))
        except:
            self.img_github = self.img_coffee = self.img_stream = None

        # --- DICCIONARIOS DE IDIOMAS COMPLETOS ---
        self.idiomas = {
            "ES": {
                "titulo": "VALORANT 4:3 CONFIG",
                "cuenta_ok": "✅ Cuenta detectada:",
                "cuenta_no": "❌ No se detectó cuenta activa",
                "res_perso": "Resolución Personalizada",
                "ancho": "Ancho (X):",
                "alto": "Alto (Y):",
                "detectado": "← Detectado",
                "sugeridas": "Resoluciones sugeridas:",
                "btn_aplicar": "APLICAR CONFIGURACIÓN",
                "footer": "Cierra el juego antes de aplicar los cambios",
                "creditos": "Developed by Mauricio Ramirez | 16/04/2026 | v1.1.0",
                "combo_init": "Seleccionar resolución...",
                "boost": "Impulso FPS Ultra",
                "bloquear": "Bloquear archivo (Anti-Reversión)",
                "calidad_res": "Calidad de resolución 3D:",
                "btn_crear_bk": "CREAR BACKUP",
                "btn_restaurar_bk": "VOLVER A ANTERIOR",
                "exito": "¡Configuración aplicada!\nResolución: {}x{}\nCalidad 3D: {}%",
                "help_boost": "Fuerza parámetros gráficos ultra bajos que no están disponibles en los menús normales del juego, los cambios se aplicaran en: \n\n sg.ViewDistanceQuality=0,\n sg.AntiAliasingQuality=0,\n sg.ShadowQuality=0,\n sg.PostProcessQuality=0,\n sg.TextureQuality=0,\n sg.EffectsQuality=0,\n sg.FoliageQuality=0,\n sg.ShadingQuality=0,\n sg.GlobalIlluminationQuality=0,\n sg.ReflectionQuality=0\n\n NOTA: se definiran los valores en 0.",
                "help_lock": "Pone el archivo en 'Solo Lectura' para que Valorant no borre tus configuraciones en futuras actualizaciones.",
                "bk_exito": "Backup creado con éxito.",
                "bk_restaurado": "Se ha regresado a la versión guardada.",
                "bk_no_existe": "No hay versiones guardadas.",
                   "opciones": [
                    "1920x1440 (Alta / 2K)", "1600x1200 (Alta / Estándar)", "1440x1080 (Ideal para monitores 1080p)",
                    "1280x960 (Equilibrada / Popular)", "1152x864 (Calidad Media)", "1024x768 (Baja / +Rendimiento FPS)",
                    "800x600 (Extrema / PC de bajos recursos)", "640x480 (Mínima)"
                ]
            },
            "EN": {
                "titulo": "VALORANT 4:3 CONFIG",
                "cuenta_ok": "✅ Account detected:",
                "cuenta_no": "❌ No active account detected",
                "res_perso": "Custom Resolution",
                "ancho": "Width (X):",
                "alto": "Height (Y):",
                "detectado": "← Detected",
                "sugeridas": "Suggested resolutions:",
                "btn_aplicar": "APPLY CONFIGURATION",
                "footer": "Close the game before applying changes",
                "creditos": "Developed by Mauricio Ramirez | 16/04/2026 | v1.1.0", # <--- NUEVO
                "combo_init": "Select resolution...",
                "boost": "Ultra FPS Boost",
                "bloquear": "Lock File (Read Only)",
                "calidad_res": "3D Resolution Quality:",
                "btn_crear_bk": "CREATE BACKUP",
                "btn_restaurar_bk": "RETURN TO PREVIOUS",
                "exito": "Applied!\nResolution: {}x{}\n3D Quality: {}%",
                "help_boost": "Forces ultra-low graphical settings that are not available in the standard in-game menus. Changes will be applied to: \n\n sg.ViewDistanceQuality=0,\n sg.AntiAliasingQuality=0,\n sg.ShadowQuality=0,\n sg.PostProcessQuality=0,\n sg.TextureQuality=0,\n sg.EffectsQuality=0,\n sg.FoliageQuality=0,\n sg.ShadingQuality=0,\n sg.GlobalIlluminationQuality=0,\n sg.ReflectionQuality=0\n\n NOTE: All values will be set to 0.",
                "help_lock": "Sets file to Read Only to prevent resets.",
                "bk_exito": "Backup created successfully.",
                "bk_restaurado": "Returned to previous version.",
                "bk_no_existe": "No previous backup found.",
                "opciones": [
                    "1920x1440 (High / 2K)", "1600x1200 (High / Standard)", "1440x1080 (Ideal for 1080p monitors)",
                    "1280x960 (Balanced / Popular)", "1152x864 (Medium Quality)", "1024x768 (Low / +FPS Performance)",
                    "800x600 (Extreme / Low-end PC)", "640x480 (Minimum)"
                ]
            }
        }

        self.lang = "ES"
        
         # 1. Primero creamos la interfaz
        self.setup_ui() 

         # 2. Obtenemos la cuenta inicial (la última activa)
        # Asegúrate de que obtener_ruta_activa() siga existiendo o usa la nueva lógica
        self.ruta_ini = self.obtener_ruta_activa()
        
         # 3. Aplicamos el idioma (ahora ya existe label_cuenta_fija y combo_cuentas)
        self.cambiar_idioma() 

        # 4. Cargamos los datos en los inputs
        self.leer_datos_actuales()

        # 5. Creamos acceso directo (si no existe)
        self.crear_acceso_directo_inicio()

    # --- LÍNEA PARA EL REFRESCO ---
    #    self.bind("<FocusIn>", lambda e: self.leer_datos_actuales())
    # --- LÍNEA PARA EL ESTADO INICIAL ---
        self.actualizar_estado_interfaz()

        self.archivo_cache_fps = ""
        if self.ruta_ini:
            self.archivo_cache_fps = os.path.join(os.path.dirname(self.ruta_ini), "original_fps_settings.json")

    # --- LÓGICA DE VALIDACIÓN (SÓLO NÚMEROS) ---
    def validar_numeros(self, P):
        return P == "" or P.isdigit()

    # --- NUEVA FUNCIÓN PARA EL SELECTOR DE CUENTAS ---
    def obtener_todas_las_cuentas(self):
        """Busca todas las carpetas de cuentas y detecta la última activa."""
        import os
        ruta_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'VALORANT', 'Saved', 'Config')
        cuentas = []
        cuenta_actual = ""
        
        if os.path.exists(ruta_base):
            for nombre in os.listdir(ruta_base):
                ruta_folder = os.path.join(ruta_base, nombre)
                if os.path.isdir(ruta_folder) and "-" in nombre and "Windows" not in nombre and "CrashReport" not in nombre:
                    cuentas.append(nombre)
        
        ruta_riot = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Riot Games', 'Riot Client', 'Data', 'RiotLocalMachine.ini')
        if os.path.exists(ruta_riot):
            try:
                import configparser
                cp = configparser.ConfigParser()
                cp.read(ruta_riot)
                if 'General' in cp and 'LastPlayedUser' in cp['General']:
                    cuenta_actual = cp['General']['LastPlayedUser']
            except:
                pass

        return cuentas, cuenta_actual

    # --- NUEVA FUNCIÓN PARA ACTUALIZAR LA RUTA ---
    def cambiar_de_cuenta_manual(self, cuenta_seleccionada):
        """Cambia la ruta del archivo .ini según la cuenta seleccionada."""
        import os
        ruta_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'VALORANT', 'Saved', 'Config')
        nueva_ruta = os.path.join(ruta_base, cuenta_seleccionada, "WindowsClient", "GameUserSettings.ini")
        
        if os.path.exists(nueva_ruta):
            self.ruta_ini = nueva_ruta
            
            # --- AGREGAR ESTA LÍNEA AQUÍ ---
            # Actualiza la ruta del JSON de backup para la cuenta seleccionada
            self.archivo_cache_fps = os.path.join(os.path.dirname(self.ruta_ini), "original_fps_settings.json")
            
            self.leer_datos_actuales() # Recarga la resolución de esa cuenta

    # --- NUEVA FUNCIÓN PARA ACTUALIZAR LA RUTA ---
    def cambiar_de_cuenta_manual(self, cuenta_seleccionada):
        """Cambia la ruta del archivo .ini según la cuenta seleccionada."""
        import os
        ruta_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'VALORANT', 'Saved', 'Config')
        nueva_ruta = os.path.join(ruta_base, cuenta_seleccionada, "WindowsClient", "GameUserSettings.ini")
        
        if os.path.exists(nueva_ruta):
            self.ruta_ini = nueva_ruta
            # Actualiza la ruta del JSON de backup para la cuenta seleccionada
            self.archivo_cache_fps = os.path.join(os.path.dirname(self.ruta_ini), "original_fps_settings.json")
            self.leer_datos_actuales()

    # --- AGREGAR AQUÍ LA NUEVA FUNCIÓN ---
    def toggle_ultra_fps(self):
        import configparser
        import json
        import os

        if not self.ruta_ini or not os.path.exists(self.ruta_ini):
            return

        config = configparser.ConfigParser()
        # IMPORTANTE: Evita que convierta todo a minúsculas y duplique líneas
        config.optionxform = str 
        config.read(self.ruta_ini)
        
        section = 'ScalabilityGroups'
        parametros = [
            "sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality",
            "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality",
            "sg.FoliageQuality", "sg.ShadingQuality", "sg.GlobalIlluminationQuality",
            "sg.ReflectionQuality"
        ]

        if self.switch_fps.get() == 1:  # ACTIVAR
            originales = {}
            if not config.has_section(section):
                config.add_section(section)
            
            for p in parametros:
                # Guardamos el valor actual exacto antes de ponerlo en 0
                originales[p] = config.get(section, p, fallback="3")
                config.set(section, p, "0")
            
            # Guardamos el backup JSON
            with open(self.archivo_cache_fps, "w") as jf:
                json.dump(originales, jf)
        
        else:  # DESACTIVAR
            if os.path.exists(self.archivo_cache_fps):
                with open(self.archivo_cache_fps, "r") as jf:
                    originales = json.load(jf)
                
                if not config.has_section(section):
                    config.add_section(section)
                
                for p, valor in originales.items():
                    config.set(section, p, str(valor))
                
                # Borramos el JSON tras restaurar
                try: os.remove(self.archivo_cache_fps)
                except: pass

        # Guardar sin espacios adicionales para mantener el formato de Riot
        with open(self.ruta_ini, 'w') as f:
            config.write(f, space_around_delimiters=False)

    # --- LÓGICA DE DETECCIÓN ORIGINAL ---
    def obtener_ruta_activa(self):
        try:
            local_appdata = os.environ.get('LOCALAPPDATA')
            ruta_riot = os.path.join(local_appdata, 'VALORANT', 'Saved', 'Config', 'WindowsClient', 'RiotLocalMachine.ini')
            if not os.path.exists(ruta_riot): return None
            last_user_id = None
            for enc in ['utf-16', 'utf-8-sig', 'utf-8']:
                try:
                    with open(ruta_riot, 'r', encoding=enc) as f:
                        match = re.search(r'LastKnownUser=(.*)', f.read())
                        if match:
                            last_user_id = re.sub(r'[^a-zA-Z0-9-]', '', match.group(1).strip())
                            break
                except: continue
            if not last_user_id: return None
            base_path = os.path.join(local_appdata, 'VALORANT', 'Saved', 'Config')
            if os.path.exists(base_path):
                for carpeta in os.listdir(base_path):
                    if last_user_id.lower().replace("-","") in carpeta.lower().replace("-",""):
                        ruta = os.path.join(base_path, carpeta, 'WindowsClient', 'GameUserSettings.ini')
                        if os.path.exists(ruta): return ruta
            return None
        except: return None

    def leer_datos_actuales(self):
        if not self.ruta_ini or not os.path.exists(self.ruta_ini): 
            self.label_detect_x.configure(text=""), self.label_detect_y.configure(text="")
            return
        try:
            with open(self.ruta_ini, 'r') as f: contenido = f.read()
            x = re.search(r'ResolutionSizeX=(\d+)', contenido)
            y = re.search(r'ResolutionSizeY=(\d+)', contenido)
            if x and y:
                self.entry_x.delete(0, 'end'), self.entry_x.insert(0, x.group(1))
                self.entry_y.delete(0, 'end'), self.entry_y.insert(0, y.group(1))
                self.label_detect_x.configure(text=self.idiomas[self.lang]["detectado"])
                self.label_detect_y.configure(text=self.idiomas[self.lang]["detectado"])
            q = re.search(r'sg\.ResolutionQuality=(\d+)', contenido)
            if q:
                num = int(float(q.group(1)))
                self.slider_calidad.set(num)
                self.label_slider_num.configure(text=f"{num}%")
                self.actualizar_label_slider(num) 

                # --- NUEVA LÓGICA DE DETECCIÓN DE SWITCHES ---
                       # 1. Detectar si el Impulso FPS está activo (Solo actualiza si el archivo es distinto a la UI)
            ajustes_fps = ["sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality", "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality", "sg.FoliageQuality", "sg.ShadingQuality", "sg.GlobalIlluminationQuality", "sg.ReflectionQuality"]
            archivo_fps_activo = all(re.search(f'{k}=0', contenido) for k in ajustes_fps)
            
            if archivo_fps_activo != self.switch_fps.get():
                if archivo_fps_activo: self.switch_fps.select()
                else: self.switch_fps.deselect()

           # 2. Detectar si el archivo está bloqueado físicamente
            if os.path.exists(self.ruta_ini):
                # SI hay un bloqueo de interfaz en progreso, NO tocamos el switch
                if not getattr(self, 'bloqueo_en_progreso', False):
                    archivo_bloqueado = not (os.stat(self.ruta_ini).st_mode & stat.S_IWRITE)
                    if archivo_bloqueado:
                        self.switch_read_only.select()
                    else:
                        self.switch_read_only.deselect()

                         # Refrescamos el bloqueo de botones según lo que acabamos de leer del archivo
            self.actualizar_estado_interfaz()
        except: pass

    def setup_ui(self):
        # Contenedor superior con alineación mejorada
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(anchor="ne", padx=15, pady=10)

        # Cargar imagen de refresco
        try:
            # Bajamos un poco el tamaño a 16x16 para que no se vea tosco
            img_refresh = ctk.CTkImage(light_image=Image.open("refresh.png"), 
                                      dark_image=Image.open("refresh.png"), 
                                      size=(20, 18))
        except Exception:
            img_refresh = None

        # Botón de refresco (Estilo minimalista)
        self.btn_refresh = ctk.CTkButton(
              self.top_frame, 
              image=img_refresh,
              text="", 
              width=32, # Cuadrado perfecto
              height=32,
              corner_radius=16, # Lo hace circular
              fg_color="transparent", 
              hover_color="#333333",
              command=self.leer_datos_actuales
          )
        self.btn_refresh.pack(side="left", padx=(0, 5))

        # Botón cambio idioma
        self.switch_lang = ctk.CTkSwitch(
            self.top_frame, 
            text="English", 
            command=self.cambiar_idioma,
            progress_color="#ff4655" # Rojo VALORANT para el switch
        )
        self.switch_lang.pack(side="left")


        # Título y Estado
        self.label_titulo = ctk.CTkLabel(self, text="", font=("Segoe UI", 24, "bold"))
        self.label_titulo.pack(pady=2)
        # Contenedor centrado (Sin expandir al 100% del ancho)
        self.frame_cuenta_linea = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_cuenta_linea.pack(pady=5) # Quitamos el fill="x" para que no se pegue a los bordes

        # Parte 1: El texto
        self.label_cuenta_fija = ctk.CTkLabel(
            self.frame_cuenta_linea, 
            text="", 
            font=("Segoe UI", 12, "bold")
        )
        self.label_cuenta_fija.pack(side="left", padx=(0, 10))

        # Configuración de eventos
        self.label_cuenta_fija.configure(cursor="hand2")
        self.label_cuenta_fija.bind("<Button-1>", self.abrir_archivo_config)

        # --- EFECTO DE TAMAÑO (HOVER) ---
        # Al entrar: sube a tamaño 13
     # Al entrar: Se mantiene en 12 pero resalta más
        self.label_cuenta_fija.bind("<Enter>", lambda e: self.label_cuenta_fija.configure(
            font=("Segoe UI", 12, "bold"), 
            text_color="#005f52" # Cambia a blanco para un brillo extra
        ))

        # Al salir: Vuelve a su estado original
        self.label_cuenta_fija.bind("<Leave>", lambda e: self.label_cuenta_fija.configure(
            font=("Segoe UI", 12, "bold"), # O "normal" si prefieres que adelgace
            text_color="#4ade80"
        ))

       # Parte 2: El ComboBox (Selector)
        lista_cuentas, _ = self.obtener_todas_las_cuentas()
        self.combo_cuentas = ctk.CTkComboBox(
            self.frame_cuenta_linea,
            values=lista_cuentas,
            width=320,
            height=28,
            state="readonly",
            command=self.cambiar_de_cuenta_manual,
            fg_color="#1a1a1a",
            border_color="#4ade80",
            button_color="#4ade80",
            text_color="#4ade80", 
            # opciones al desplegar
            dropdown_text_color="#4ade80" 
        )
        self.combo_cuentas.pack(side="left")


        vcmd = (self.register(self.validar_numeros), '%P')
        self.label_res_p = ctk.CTkLabel(self, text="", font=("Segoe UI", 14, "bold"))
        self.label_res_p.pack(pady=(10, 5))
        
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)
        self.label_x_text = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 12))
        self.label_x_text.grid(row=0, column=0, padx=5, sticky="e")
        self.entry_x = ctk.CTkEntry(self.frame_inputs, width=120, validate="key", validatecommand=vcmd)
        self.entry_x.grid(row=0, column=1, pady=5)
        self.label_detect_x = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 10), text_color="#94a3b8")
        self.label_detect_x.grid(row=0, column=2, padx=10, sticky="w")

        self.label_y_text = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 12))
        self.label_y_text.grid(row=1, column=0, padx=5, sticky="e")
        self.entry_y = ctk.CTkEntry(self.frame_inputs, width=120, validate="key", validatecommand=vcmd)
        self.entry_y.grid(row=1, column=1, pady=5)
        self.label_detect_y = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 10), text_color="#94a3b8")
        self.label_detect_y.grid(row=1, column=2, padx=10, sticky="w")

        self.label_sug = ctk.CTkLabel(self, text="", font=("Segoe UI", 14, "bold"))
        self.label_sug.pack(pady=(10, 5))
        self.combo_res = ctk.CTkComboBox(self, width=350, state="readonly", command=self.on_combo_change)
        self.combo_res.pack(pady=10)

        # Slider
        self.frame_slider = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_slider.pack(pady=10, padx=40, fill="x")
        self.label_calidad = ctk.CTkLabel(self.frame_slider, text="", font=("Segoe UI", 12, "bold"))
        self.label_calidad.pack(side="left", padx=(10, 5))
        self.label_slider_num = ctk.CTkLabel(self.frame_slider, text="100%", font=("Segoe UI", 12, "bold"), text_color="#4F8DF8")
        self.label_slider_num.pack(side="left", padx=2)
        self.slider_calidad = ctk.CTkSlider(self.frame_slider, from_=10, to=100, command=self.actualizar_label_slider)
        self.slider_calidad.pack(side="right", fill="x", expand=True, padx=10)

        # Backup
        self.frame_bk = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bk.pack(pady=10, padx=40, fill="x")
        self.btn_crear_bk = ctk.CTkButton(self.frame_bk, text="", fg_color="#94a3b8", hover_color="#64748b", text_color="#000", font=("Segoe UI", 11, "bold"), command=self.crear_backup_manual)
        self.btn_crear_bk.pack(side="left", expand=True, padx=5, fill="x")
        self.btn_restaurar_bk = ctk.CTkButton(self.frame_bk, text="", fg_color="#94a3b8", hover_color="#64748b", text_color="#000", font=("Segoe UI", 11, "bold"), command=self.restaurar_backup)
        self.btn_restaurar_bk.pack(side="right", expand=True, padx=5, fill="x")

        # Switches Opciones
        self.frame_avanzado = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_avanzado.pack(pady=10, padx=40, fill="x")
        self.switch_fps = ctk.CTkSwitch(self.frame_avanzado, text="", command=self.toggle_ultra_fps)
        self.switch_fps.pack(side="left", padx=(10, 2))
        self.btn_help_fps = ctk.CTkButton(self.frame_avanzado, text="?", width=18, height=18, corner_radius=9, fg_color="#334155", command=lambda: self.mostrar_ayuda("fps"))
        self.btn_help_fps.pack(side="left", padx=(0, 20))
        self.switch_read_only = ctk.CTkSwitch(self.frame_avanzado, text="", command=self.toggle_lock)
        self.switch_read_only.pack(side="left", padx=(10, 2))
        self.btn_help_lock = ctk.CTkButton(self.frame_avanzado, text="?", width=18, height=18, corner_radius=9, fg_color="#334155", command=lambda: self.mostrar_ayuda("lock"))
        self.btn_help_lock.pack(side="left")

        # --- MENSAJE DE AVISO DE BLOQUEO ---
        self.label_aviso_bloqueo = ctk.CTkLabel(
            self, 
            text="", 
            font=("Segoe UI", 11, "bold"), 
            text_color="#ff4655" 
        )
        self.label_aviso_bloqueo.pack(pady=(5, 0))

        # Botón Aplicar Rojo
        self.btn_aplicar = ctk.CTkButton(
            self, text="", fg_color="#ff4655", hover_color="#a12d36", 
            height=50, font=("Segoe UI", 16, "bold"), command=self.aplicar
        )
        self.btn_aplicar.pack(pady=15, padx=40, fill="x")
        self.btn_aplicar.bind("<Enter>", lambda e: self.btn_aplicar.configure(height=52, border_width=2, border_color="#ffffff"))
        self.btn_aplicar.bind("<Leave>", lambda e: self.btn_aplicar.configure(height=50, border_width=0))

        # Redes Sociales
        self.frame_social = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_social.pack(pady=10)
        self.crear_soc(self.img_github, "#000", "https://github.com/MauricioEsparron/configurador_valorant")
        self.crear_soc(self.img_coffee, "#FFDD00", "https://buymeacoffee.com/maxpredator01")
        self.crear_soc(self.img_stream, "#7FF5D2", "https://streamlabs.com/maxpredator01/tip")

        # --- SECCIÓN DE CRÉDITOS ---
        self.label_creditos = ctk.CTkLabel(self, text="", font=("Segoe UI", 10, "bold"), text_color="#9ca3af")
        self.label_creditos.pack(side="bottom", pady=(0, 10))

        self.label_footer = ctk.CTkLabel(self, text="", font=("Segoe UI", 11, "italic"), text_color="#6b7280")
        self.label_footer.pack(side="bottom", pady=(10, 0))

    def crear_soc(self, img, color, url):
        btn = ctk.CTkButton(self.frame_social, text="", image=img, fg_color=color, hover_color=color, width=48, height=48, corner_radius=10, command=lambda: webbrowser.open(url))
        btn.pack(side="left", padx=10)

    def cambiar_idioma(self):
        self.lang = "EN" if self.switch_lang.get() == 1 else "ES"
        t = self.idiomas[self.lang]
        self.label_titulo.configure(text=t["titulo"]), self.label_res_p.configure(text=t["res_perso"])
        self.label_x_text.configure(text=t["ancho"]), self.label_y_text.configure(text=t["alto"])
        self.label_sug.configure(text=t["sugeridas"]), self.btn_aplicar.configure(text=t["btn_aplicar"])
        self.btn_crear_bk.configure(text=t["btn_crear_bk"]), self.btn_restaurar_bk.configure(text=t["btn_restaurar_bk"])
        self.label_calidad.configure(text=t["calidad_res"]), self.switch_fps.configure(text=t["boost"]), self.switch_read_only.configure(text=t["bloquear"])
        self.label_footer.configure(text=t["footer"]), self.label_creditos.configure(text=t["creditos"])
        self.combo_res.configure(values=t["opciones"])
        if self.combo_res.get() in ["", "CTkComboBox"]: self.combo_res.set(t["combo_init"])
              # --- BLOQUE ACTUALIZADO PARA SELECTOR DE CUENTAS ---
        t = self.idiomas[self.lang]
        if self.ruta_ini:
            # Extraer ID de la carpeta
            nombre = os.path.basename(os.path.dirname(os.path.dirname(self.ruta_ini)))
            
            # Actualizamos la etiqueta con subrayado para indicar que es un link
            self.label_cuenta_fija.configure(
                text=t["cuenta_ok"], 
                text_color="#4ade80",
                font=("Segoe UI", 12, "bold") # <--- Añadimos el subrayado
            )
            # Actualizamos el valor del combo
            self.combo_cuentas.set(nombre)
        else:
            self.label_cuenta_fija.configure(
                text=t["cuenta_no"], 
                text_color="#f87171",
                font=("Segoe UI", 12, "bold") # Sin subrayado si no hay cuenta
            )
            self.combo_cuentas.set("")

    def actualizar_o_insertar(self, contenido, clave, valor, ancla=None):
        if re.search(rf'^{clave}=.*', contenido, re.MULTILINE):
            return re.sub(rf'^{clave}=.*', f'{clave}={valor}', contenido, flags=re.MULTILINE)
        else:
            if ancla and re.search(rf'^{ancla}=.*', contenido, re.MULTILINE):
                return re.sub(rf'^({ancla}=.*)', rf'\1\n{clave}={valor}', contenido, flags=re.MULTILINE)
            return contenido.replace('[/Script/Engine.GameUserSettings]', f'{clave}={valor}\n\n[/Script/Engine.GameUserSettings]')

    def toggle_lock(self):
        """Muestra aviso y bloquea el refresco temporalmente."""
        if self.switch_read_only.get():
            # 1. Bloqueamos temporalmente el autorefresco
            self.bloqueo_en_progreso = True 
            
            titulo = "Modo de Bloqueo" if self.lang == "ES" else "Lock Mode"
            msg = ("Has seleccionado bloquear el archivo.\n\n"
                   "Este cambio se ejecutará físicamente cuando hagas clic en "
                   "'APLICAR CONFIGURACIÓN'.") if self.lang == "ES" else (
                   "You have selected to lock the file.\n\n"
                   "This change will take effect physically when you click "
                   "'APPLY CONFIGURATION'.")
            
            from tkinter import messagebox
            messagebox.showinfo(titulo, msg)
            
            # 2. Liberamos el bloqueo después de que el usuario cierra el mensaje
            self.after(500, lambda: setattr(self, 'bloqueo_en_progreso', False))

            self.actualizar_estado_interfaz() # <-- Añade esta línea al final

    def obtener_todas_las_cuentas(self):
        """Busca todas las carpetas de cuentas y detecta la última activa."""
        import os
        ruta_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'VALORANT', 'Saved', 'Config')
        cuentas = []
        cuenta_actual = ""
        
        # 1. Buscar todas las carpetas de cuentas
        if os.path.exists(ruta_base):
            for nombre in os.listdir(ruta_base):
                ruta_folder = os.path.join(ruta_base, nombre)
                if os.path.isdir(ruta_folder) and "-" in nombre and "Windows" not in nombre and "CrashReport" not in nombre:
                    cuentas.append(nombre)
        
        # 2. Intentar detectar la cuenta activa por RiotLocalMachine
        ruta_riot = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Riot Games', 'Riot Client', 'Data', 'RiotLocalMachine.ini')
        if os.path.exists(ruta_riot):
            try:
                import configparser
                cp = configparser.ConfigParser()
                cp.read(ruta_riot)
                if 'General' in cp and 'LastPlayedUser' in cp['General']:
                    cuenta_actual = cp['General']['LastPlayedUser']
            except:
                pass

        return cuentas, cuenta_actual

    def actualizar_estado_interfaz(self):
        """Bloquea funcionalidad y efecto hover manteniendo el diseño visual."""
        if not hasattr(self, 'switch_read_only'): return

        esta_bloqueado = self.switch_read_only.get()
        estado_input = "disabled" if esta_bloqueado else "normal"
        
        # Colores originales de tus botones (ajústalos si usas otros)
        color_backup = "#3b82f6" # Color azul original
        color_hover_original = "#2563eb" # Color hover original

        # 1. Inputs (se ponen en gris para indicar que no se puede escribir)
        self.entry_x.configure(state=estado_input)
        self.entry_y.configure(state=estado_input)
        self.combo_res.configure(state=estado_input)
        self.slider_calidad.configure(state=estado_input)
        self.switch_fps.configure(state=estado_input)
            # 2. Botones de Backup
        if esta_bloqueado:
            self.btn_crear_bk.configure(command=None, hover_color=self.btn_crear_bk.cget("fg_color"))
            self.btn_restaurar_bk.configure(command=None, hover_color=self.btn_restaurar_bk.cget("fg_color"))
        else:
            # --- CORRECCIÓN DE NOMBRES SEGÚN TU CÓDIGO ACTUAL ---
            # El PDF muestra que usas 'crear_backup_manual' y 'restaurar_backup'
            self.btn_crear_bk.configure(command=self.crear_backup_manual, hover_color="#2563eb")
            self.btn_restaurar_bk.configure(command=self.restaurar_backup, hover_color="#2563eb")
        # --- NUEVA LÓGICA DE AVISO VISUAL ---
        if esta_bloqueado:
            msg = ("⚠️ OPCIONES BLOQUEADAS: Desactiva 'Bloquear archivo' para modificar.") if self.lang == "ES" else (
                   "⚠️ OPTIONS LOCKED: Deactivate 'Lock File' to make changes.")
            self.label_aviso_bloqueo.configure(text=msg)
        else:
            self.label_aviso_bloqueo.configure(text="")

    # --- RESTO DE LÓGICA (backup, aplicar, ayuda...) ---
    def aplicar(self):
        t = self.idiomas[self.lang]
        if not self.ruta_ini: return
        
        x, y = self.entry_x.get().strip(), self.entry_y.get().strip()
        if not x.isdigit() or not y.isdigit(): return
        
        cal_valor = int(self.slider_calidad.get())
        cal_formato = f"{cal_valor}.000000"
        
        import stat
        if os.path.exists(self.ruta_ini):
            mode = os.stat(self.ruta_ini).st_mode
            os.chmod(self.ruta_ini, mode | stat.S_IWRITE)

        try:
            with open(self.ruta_ini, 'r', encoding='utf-8') as f:
                contenido_original = f.read()
            
            contenido = contenido_original 

            # 1. Parámetros de resolución
            params = {
                'bShouldLetterbox': 'False',
                'bLastConfirmedShouldLetterbox': 'False',
                'bUseVSync': 'False',
                'bUseDynamicResolution': 'False',
                'ResolutionSizeX': x,
                'ResolutionSizeY': y,
                'LastUserConfirmedResolutionSizeX': x,
                'LastUserConfirmedResolutionSizeY': y,
                'WindowPosX': '0',
                'WindowPosY': '0',
                'LastConfirmedFullscreenMode': '2',
                'PreferredFullscreenMode': '0',
                'AudioQualityLevel': '0',
                'LastConfirmedAudioQualityLevel': '0'
            }
            
            for clave, valor in params.items():
                contenido = self.actualizar_o_insertar(contenido, clave, valor)
            
            contenido = self.actualizar_o_insertar(contenido, 'FullscreenMode', '2', ancla='HDRDisplayOutputNits')
            contenido = re.sub(r'sg\.ResolutionQuality=.*', f'sg.ResolutionQuality={cal_formato}', contenido)

            # 2. Impulso FPS
            if self.switch_fps.get():
                ajustes_fps = ["sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality", "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality", "sg.FoliageQuality", "sg.ShadingQuality", "sg.GlobalIlluminationQuality", "sg.ReflectionQuality"]
                for k in ajustes_fps:
                    contenido = re.sub(f'{k}=.*', f'{k}=0', contenido)

            # 3. Guardar cambios
            with open(self.ruta_ini, 'w', encoding='utf-8') as f:
                f.write(contenido)

            # 4. Bloqueo físico
            if self.switch_read_only.get():
                mode = os.stat(self.ruta_ini).st_mode
                os.chmod(self.ruta_ini, mode & ~stat.S_IWRITE)

            # 5. LÓGICA DE MENSAJE INTELIGENTE
            cambios = []
            if f"ResolutionSizeX={x}" not in contenido_original or f"ResolutionSizeY={y}" not in contenido_original:
                cambios.append(f"• {t['ancho']} {x} {t['alto']} {y}")
            if f"sg.ResolutionQuality={cal_formato}" not in contenido_original:
                cambios.append(f"• {t['calidad_res']} {cal_valor}%")
                        # 3. Verificar FPS Boost (Validación estricta de las 10 líneas)
            ajustes_fps_nombres = [
                "sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality",
                "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality",
                "sg.FoliageQuality", "sg.ShadingQuality", "sg.GlobalIlluminationQuality",
                "sg.ReflectionQuality"
            ]
            
            # Comprobamos si en el archivo ORIGINAL ya estaban todas en 0
            estaba_todo_en_zero = all(re.search(rf'^{k}=0', contenido_original, re.MULTILINE) for k in ajustes_fps_nombres)
            
            # Solo informamos el cambio si el usuario activó el switch Y no estaban todas en 0 antes
            if self.switch_fps.get() and not estaba_todo_en_zero:
                cambios.append(f"• {t['boost']}: ✅")

            if self.switch_read_only.get() and (os.stat(self.ruta_ini).st_mode & stat.S_IWRITE):
                cambios.append(f"• {t['bloquear']}: ✅")

            # Mostrar mensaje según cantidad de cambios
            if len(cambios) == 1:
                cuerpo = "Se realizó un cambio:" if self.lang == "ES" else "One change was made:"
                mensaje_final = f"{cuerpo}\n\n{cambios[0]}"
            elif len(cambios) > 1:
                cuerpo = "Cambios aplicados en:" if self.lang == "ES" else "Changes applied to:"
                mensaje_final = f"{cuerpo}\n\n" + "\n".join(cambios)
            else:
                mensaje_final = "La configuración ya estaba aplicada." if self.lang == "ES" else "Settings were already applied."

            from tkinter import messagebox
            messagebox.showinfo("VALORANT", mensaje_final)

            self.leer_datos_actuales()
            self.actualizar_estado_interfaz()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Error", str(e))


    def mostrar_ayuda(self, tipo):
        """Muestra la ayuda detallada según el botón presionado."""
        t = self.idiomas[self.lang]
        titulo = t["boost"] if tipo == "fps" else t["bloquear"]
        msg = t["help_boost"] if tipo == "fps" else t["help_lock"]
        
        from tkinter import messagebox
        messagebox.showinfo(titulo, msg)


    def crear_backup_manual(self):
        if self.ruta_ini:
            shutil.copy2(self.ruta_ini, self.ruta_ini + ".bak")
            messagebox.showinfo("Backup", self.idiomas[self.lang]["bk_exito"])

    def restaurar_backup(self):
        if not self.ruta_ini: return
        path_bk = self.ruta_ini + ".bak"
        if os.path.exists(path_bk):
            os.chmod(self.ruta_ini, stat.S_IWRITE)
            shutil.copy2(path_bk, self.ruta_ini)
            messagebox.showinfo("Backup", self.idiomas[self.lang]["bk_restaurado"])
            self.leer_datos_actuales()

    def actualizar_label_slider(self, v):
        valor = int(float(v))
        self.label_slider_num.configure(text=f"{valor}%")

        # Lógica de colores dinámica (Verde -> Amarillo -> Naranja -> Rojo)
        if valor >= 80:
            color = "#4ade80" # Verde (Nitidez total)
        elif valor >= 60:
            color = "#eab308" # Amarillo (Balanceado)
        elif valor >= 35:
            color = "#f97316" # Naranja (Rendimiento)
        else:
            color = "#ff4655" # Rojo (Máximos FPS / Minecraft Mode)

        # Cambiamos el color del número y de la bolita del slider
        self.label_slider_num.configure(text_color=color)
        self.slider_calidad.configure(button_color=color, button_hover_color=color)

    def on_combo_change(self, choice):
        m = re.search(r'(\d+)x(\d+)', choice)
        if m:
            self.entry_x.delete(0, 'end'), self.entry_x.insert(0, m.group(1))
            self.entry_y.delete(0, 'end'), self.entry_y.insert(0, m.group(2))
            self.label_detect_x.configure(text=""), self.label_detect_y.configure(text="")


    def crear_acceso_directo_inicio(self):
        if not getattr(sys, 'frozen', False): return
        ruta_exe = os.path.abspath(sys.executable)
        ruta_lnk = os.path.join(os.environ.get('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', "ConfiguradorValorant.lnk")
        if not os.path.exists(ruta_lnk):
            try:
                vbs = f'Set o=CreateObject("WScript.Shell"):Set s=o.CreateShortcut("{ruta_lnk}"):s.TargetPath="{ruta_exe}":s.Save'
                with open("tmp.vbs","w") as f: f.write(vbs)
                os.system("cscript //nologo tmp.vbs"), os.remove("tmp.vbs")
            except: pass

    def abrir_archivo_config(self, event=None):
        """Abre el archivo GameUserSettings.ini con el editor de texto predeterminado."""
        import os
        from tkinter import messagebox # <--- Asegura que esto esté aquí
        
        if hasattr(self, 'ruta_ini') and self.ruta_ini and os.path.exists(self.ruta_ini):
            try:
                os.startfile(self.ruta_ini)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo: {e}")
        else:
            from tkinter import messagebox
            messagebox.showwarning("Aviso", "No se encontró el archivo de configuración.")


if __name__ == "__main__":
    app = ValorantConfigApp()
    app.mainloop()
