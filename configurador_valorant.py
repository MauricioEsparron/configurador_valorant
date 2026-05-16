import os
import re
import stat
import shutil
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
import sys
import ctypes
import json
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

    def tr(self, clave, fallback=""):
            """Obtiene una traducción segura según el idioma actual."""
            return self.idiomas.get(self.lang, {}).get(clave, fallback)

    def __init__(self):
        super().__init__()
        import json

        # 1. El "Ancla"
        self.archivo_semilla = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_launcher.json")

        # Ruta por defecto
        self.default_data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

        # Estado inicial
        onboarding_prev = False
        self.folder_data = self.default_data_folder

        # 2. Leer semilla si existe
        if os.path.exists(self.archivo_semilla):
            try:
                with open(self.archivo_semilla, "r", encoding="utf-8") as f:
                    seed = json.load(f)

                self.folder_data = seed.get("data_path", self.default_data_folder)

                onboarding_prev = seed.get(
                    "onboarding_completed",
                    os.path.exists(os.path.join(self.folder_data, "profiles.json"))
                )

            except:
                pass

        # 3. Rutas reales
        self.ruta_perfiles = os.path.join(self.folder_data, "profiles.json")
        self.folder_backups = os.path.join(self.folder_data, "backups")

        # 4. Crear estructura solo si onboarding ya existe
        if onboarding_prev:
            os.makedirs(self.folder_data, exist_ok=True)
            os.makedirs(self.folder_backups, exist_ok=True)

        # 5. Cargar datos
        self.datos_pro = self.cargar_y_migrar_datos(crear_archivos=onboarding_prev)

        # Resolución
        self.valor_3d_inicial = self.datos_pro.get("config_global", {}).get("res_3d_default", 100)

        # Idioma
        self.lang = self.datos_pro.get("config_global", {}).get("language", "en")

        # Cache
        self.idiomas = {}

        # 6. Mostrar onboarding si corresponde
        if not onboarding_prev:
            self.withdraw()
            self.after(100, self.mostrar_modal_bienvenida_tyc)
        # Catálogo global de idiomas
        self.idiomas_disponibles = {
            "es": "Español",
            "en": "English",
            "fr": "Français",
            "de": "Deutsch",
            "it": "Italiano",
            "pt": "Português",
            "ja": "日本語",
            "ko": "한국어",
            "zh-CN": "中文 (简体)",
            "ru": "Русский"
        }

        # Cargar idioma actual
        self.idiomas[self.lang] = self.cargar_idioma_dinamico(self.lang)

        # --- CONFIGURACIÓN DE VENTANA ---
        self.title("VALORANT Stretched Res Configurator")
        self.geometry("595x695")
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
            self.img_refresh = ctk.CTkImage(light_image=Image.open(resource_path("refresh.png")), size=(20, 18))
        except:
            self.img_github = self.img_coffee = self.img_stream = None

        # --- DICCIONARIOS DE IDIOMAS COMPLETOS ---
        self.idiomas = {}
        
        # 1. Cargamos el código del idioma desde el Super JSON
        self.lang = self.datos_pro.get("config_global", {}).get("language", "ES")
        
        # 2. Cargamos dinámicamente el archivo JSON correspondiente
        self.idiomas[self.lang] = self.cargar_idioma_dinamico(self.lang)            
        
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

        # Configuración de backup FPS
        self.archivo_cache_fps = ""
        if self.ruta_ini:
            self.archivo_cache_fps = os.path.join(os.path.dirname(self.ruta_ini), "original_fps_settings.json")

        # --- SOLUCIÓN AL ERROR: Definir la lista aquí ---
        self.parametros_fps = [
            "sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality",
            "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality",
            "sg.FoliageQuality", "sg.ShadingQuality", "sg.GlobalIlluminationQuality",
            "sg.ReflectionQuality"
        ]

        self.archivo_custom_fps = os.path.join(os.path.dirname(self.ruta_ini), "custom_fps_settings.json") if self.ruta_ini else ""

        # import json

        # onboarding_completado = False

        # # Leer primero desde archivo semilla (fuente absoluta)
        # if not onboarding_prev:
        #     self.withdraw()
        #     self.after(100, self.mostrar_modal_bienvenida_tyc)

            # --- LÓGICA DE VALIDACIÓN (SÓLO NÚMEROS) ---
    def validar_numeros(self, P):
        return P == "" or P.isdigit()

    def mostrar_modal_bienvenida_tyc(self):
        """Fase 1: Ventana modal que obliga a aceptar los términos o cerrar la app."""
        self.ventana_bienvenida = ctk.CTkToplevel(self)
        self.ventana_bienvenida.title(self.tr("titulo_bienvenida", "Bienvenido"))
        self.ventana_bienvenida.geometry("450x200")
        self.ventana_bienvenida.resizable(False, False)
        self.ventana_bienvenida.grab_set()
        self.ventana_bienvenida.attributes("-topmost", True)
        
        # Función interna para limpiar archivos residuales si decide no aceptar
        def cancelar_y_limpiar():
            try:
                # Si se alcanzó a crear la carpeta temporal 'data' al iniciar, la borramos
                if os.path.exists(self.folder_data):
                    import shutil
                    shutil.rmtree(self.folder_data)
            except Exception:
                pass
            self.quit()

        self.ventana_bienvenida.protocol("WM_DELETE_WINDOW", cancelar_y_limpiar)
        
        lbl_mensaje = ctk.CTkLabel(
            self.ventana_bienvenida, 
            text=self.tr("msg_onboarding_tyc", "Al usar esta aplicación, aceptas los términos y condiciones de uso."),
            font=("Segoe UI", 13, "bold"),
            wraplength=380,
            justify="center"
        )
        lbl_mensaje.pack(pady=(40, 20), padx=20)
        
        frame_botones = ctk.CTkFrame(self.ventana_bienvenida, fg_color="transparent")
        frame_botones.pack(pady=10)
        
        btn_cancelar = ctk.CTkButton(
            frame_botones, 
            text=self.tr("btn_cancelar", "Cancelar"), 
            fg_color="#343a40", 
            hover_color="#23272b",
            width=120,
            command=cancelar_y_limpiar
        )
        btn_cancelar.pack(side="left", padx=15)
        
        btn_aceptar = ctk.CTkButton(
            frame_botones, 
            text=self.tr("btn_aceptar", "Aceptar"), 
            fg_color="#ff4655", 
            hover_color="#b8323d",
            width=120,
            command=self.onboarding_aceptar_terminos
        )
        btn_aceptar.pack(side="left", padx=15)

    def onboarding_aceptar_terminos(self):
        """Transición: Cierra bienvenida y pasa a la configuración de almacenamiento."""
        if hasattr(self, 'ventana_bienvenida') and self.ventana_bienvenida.winfo_exists():
            self.ventana_bienvenida.destroy()
        self.mostrar_modal_almacenamiento_inicial()

    def mostrar_modal_almacenamiento_inicial(self):
            """Fase 2: Ventana obligatoria para elegir la ruta de datos en la primera ejecución."""
            self.ventana_onboarding_alm = ctk.CTkToplevel(self)
            self.ventana_onboarding_alm.title(self.tr("tab_storage", "Almacenamiento"))
            self.ventana_onboarding_alm.geometry("500x280")
            self.ventana_onboarding_alm.resizable(False, False)
            self.ventana_onboarding_alm.grab_set()
            self.ventana_onboarding_alm.attributes("-topmost", True)
            
            self.ventana_onboarding_alm.protocol("WM_DELETE_WINDOW", self.quit)
            
            ctk.CTkLabel(
                self.ventana_onboarding_alm, 
                text=self.tr("lbl_titulo_ruta", "Selecciona la ruta de almacenamiento para los datos:"), 
                font=("Segoe UI", 12, "bold")
            ).pack(pady=(25, 5))
            
            self.lbl_ruta_onboarding = ctk.CTkLabel(
                self.ventana_onboarding_alm, 
                text=f"{self.folder_data}", 
                wraplength=440,
                text_color="#8b949e"
            )
            self.lbl_ruta_onboarding.pack(pady=10)
            
            # --- FUNCIÓN INTERNA PARA EXAMINAR RUTA ---
            def examinar_ruta_inicial():
                from tkinter import filedialog
                nueva_ruta = filedialog.askdirectory()
                if nueva_ruta:
                    self.folder_data = nueva_ruta
                    self.lbl_ruta_onboarding.configure(text=f"{nueva_ruta}")
                    
            # 1. EL BOTÓN QUE TE HABÍA BORRADO (Cambiar Ubicación)
            btn_examinar = ctk.CTkButton(
                self.ventana_onboarding_alm, 
                text=self.tr("btn_cambiar_ruta", "Cambiar Ubicación"), 
                fg_color="#343a40",
                hover_color="#23272b",
                width=140,
                command=examinar_ruta_inicial
            )
            btn_examinar.pack(pady=10)
            
            # --- FUNCIÓN INTERNA PARA GUARDAR Y FINALIZAR ---
            def finalizar_configuracion():
                import json
                
                # Crear estructura física final en la ruta elegida
                os.makedirs(self.folder_data, exist_ok=True)
                self.ruta_perfiles = os.path.join(self.folder_data, "profiles.json")
                self.folder_backups = os.path.join(self.folder_data, "backups")
                os.makedirs(self.folder_backups, exist_ok=True)

                # 1. Guardamos la ruta definitiva en el archivo semilla
                with open(self.archivo_semilla, "w", encoding="utf-8") as f:
                    json.dump({
                        "data_path": self.folder_data,
                        "onboarding_completed": True
                    }, f, indent=4, ensure_ascii=False)
                    
                # 2. Guardamos en el diccionario de memoria de la app
                self.guardar_en_super_json("config_global", None, "data_path", self.folder_data)
                self.guardar_en_super_json("config_global", None, "onboarding_completed", True)
                
                # 3. Forzar escritura real del Super JSON por primera vez en su ruta correcta
                with open(self.ruta_perfiles, "w", encoding="utf-8") as f:
                    json.dump(self.datos_pro, f, indent=4, ensure_ascii=False)
                
                # 4. Cerramos asistente y restauramos UI
                self.ventana_onboarding_alm.destroy()
                self.deiconify()

            # 2. EL BOTÓN DE FINALIZACIÓN (Confirmar)
            btn_finalizar = ctk.CTkButton(
                self.ventana_onboarding_alm, 
                text=self.tr("btn_finalizar", "Finalizar"), 
                fg_color="#2ea44f", 
                hover_color="#22863a",
                width=140,
                command=finalizar_configuracion
            )
            btn_finalizar.pack(pady=(5, 10))

    # --- LÓGICA DE VALIDACIÓN (SÓLO NÚMEROS) ---
    def validar_numeros(self, P):
        return P == "" or P.isdigit()

    def obtener_todas_las_cuentas(self):
        """Versión Final: Filtro Regex + Super JSON + Detección Riot."""
        import getpass
        import configparser

        ruta_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'VALORANT', 'Saved', 'Config')
        usuario_windows = getpass.getuser()
        cuentas = []
        cuenta_actual = ""
        
        # Regex estricto de ID de Riot (UUID + Región)
        patron_cuenta = re.compile(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}-[a-zA-Z]+$')

        # 1. Cargamos perfiles del Super JSON (en memoria)
        perfiles = self.cargar_alias()

        if os.path.exists(ruta_base):
            for nombre in os.listdir(ruta_base):
                # Filtros de exclusión por nombre de usuario y carpetas sistema
                if nombre.lower().startswith(usuario_windows.lower()): continue
                if nombre in ["Windows", "WindowsClient", "CrashReportClient"]: continue
                
                # Validación por Regex y existencia de .ini
                if patron_cuenta.match(nombre):
                    ruta_ini_check = os.path.join(ruta_base, nombre, "WindowsClient", "GameUserSettings.ini")
                    if os.path.exists(ruta_ini_check):
                        # --- LÓGICA DE TRADUCCIÓN LIMPIA ---
                        if nombre in perfiles:
                            datos = perfiles[nombre]
                            # Extraemos solo el texto del alias si es un diccionario
                            alias_texto = datos.get("alias", "") if isinstance(datos, dict) else ""
                            
                            if alias_texto:
                                cuentas.append(f"{alias_texto}  |  id: {nombre}")
                            else:
                                cuentas.append(nombre)
                        else:
                            cuentas.append(nombre)

        # 2. Detección de cuenta activa de Riot
        ruta_riot = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Riot Games', 'Riot Client', 'Data', 'RiotLocalMachine.ini')
        if os.path.exists(ruta_riot):
            try:
                cp = configparser.ConfigParser()
                cp.read(ruta_riot)
                if 'General' in cp and 'LastPlayedUser' in cp['General']:
                    cuenta_actual = cp['General']['LastPlayedUser']
            except: pass
                
        return cuentas, cuenta_actual

    def cambiar_de_cuenta_manual(self, cuenta_seleccionada):
        """Versión 1.3: Cambia de cuenta y carga TODO desde el Super JSON."""
        import os
        
        # 1. Extraemos el ID real (Manejando Alias)
        id_real = self.extraer_id_real(cuenta_seleccionada)
        
        ruta_base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'VALORANT', 'Saved', 'Config')
        nueva_ruta = os.path.join(ruta_base, id_real, "WindowsClient", "GameUserSettings.ini")
        
        if os.path.exists(nueva_ruta):
            self.ruta_ini = nueva_ruta
            
            # 2. Accedemos a los datos de esta cuenta en el Super JSON
            perfil = self.datos_pro.get("accounts", {}).get(id_real, {})
            
            # --- CARGAR RESOLUCIÓN 3D ---
            # Si no tiene una grabada, usa el default global o 100
            val_default = self.datos_pro.get("config_global", {}).get("res_3d_default", 100)
            valor_3d = perfil.get("res_3d", val_default)
            
            self.slider_calidad.set(valor_3d)
            self.actualizar_label_slider(valor_3d)
            
            # --- CARGAR ESTADO DE FPS (Opcional por ahora) ---
            # Aquí podrías poner el switch en ON si detectas que tiene boost activo
            
            # 3. Recarga la UI general (lectura del .ini, idioma, etc.)
            self.leer_datos_actuales()

    def cargar_alias(self):
        """Retorna el diccionario de cuentas desde el Super JSON en memoria."""
        # En lugar de leer un archivo viejo, leemos lo que ya tenemos cargado
        return self.datos_pro.get("accounts", {})

    def guardar_alias(self, folder_id, nuevo_nombre):
        """Guarda el nombre personalizado directamente en el Super JSON (profiles.json)."""
        # Usamos la función maestra para inyectar el alias en el perfil de la cuenta
        self.guardar_en_super_json("accounts", folder_id, "alias", nuevo_nombre)

    def abrir_ventana_alias(self):
        import tkinter.messagebox as messagebox
        
        seleccion = self.combo_cuentas.get()
        if not seleccion:
            messagebox.showwarning(
                self.tr("msg_aviso_titulo", "Warning"),
                self.tr("selecciona_cuenta", "Select an account first.")
            )
            return

        id_real = self.extraer_id_real(seleccion)
        alias_dict = self.cargar_alias()
        # --- CAMBIO 1: Extraer solo el texto del alias para el Entry ---
        perfil_cuenta = alias_dict.get(id_real, {})
        # Si perfil_cuenta es un diccionario, extraemos 'alias'; si no, usamos vacío
        nombre_actual = perfil_cuenta.get("alias", "") if isinstance(perfil_cuenta, dict) else ""

        # 1. Creamos una ventana de nivel superior (Popup)
        self.ventana_input = ctk.CTkToplevel(self)
        self.ventana_input.title(self.tr("personalizar_cuenta_titulo", "Personalize Account"))
        self.ventana_input.geometry("550x230")
        self.ventana_input.resizable(False, False)
        self.ventana_input.grab_set() # Bloquea la ventana principal hasta cerrar esta

        # 2. Etiquetas de información
        ctk.CTkLabel(self.ventana_input, text=f"ID: {id_real}", font=("Arial", 10), text_color="gray").pack(pady=(15, 0))
        ctk.CTkLabel(self.ventana_input, text=self.tr("escribe_alias", "Enter the new alias (3-30 characters):"), font=("Arial", 12, "bold")).pack(pady=10)
        # 3. EL CAMPO DE TEXTO CON LA DATA CARGADA
        self.entry_alias = ctk.CTkEntry(self.ventana_input, width=300)
        self.entry_alias.insert(0, nombre_actual) # <--- AQUÍ CARGAMOS EL NOMBRE ANTERIOR
        self.entry_alias.pack(pady=10)
        self.entry_alias.focus_set() # Pone el cursor ahí automáticamente

        # 4. Botón de Guardar
        def confirmar():
            nuevo_alias = self.entry_alias.get().strip()
            
            # 1. Validaciones
            if len(nuevo_alias) < 3 or len(nuevo_alias) > 30:
                messagebox.showerror(
                    self.tr("msg_error_titulo", "Error"),
                    self.tr("error_nombre_longitud", "Must be between 3 and 30 characters.")
                )
                return

            otros_alias = []
            for fid, datos in alias_dict.items():
                if fid != id_real and isinstance(datos, dict):
                    otros_alias.append(datos.get("alias", "").lower())

            if nuevo_alias.lower() in otros_alias:
                messagebox.showerror(
                    self.tr("msg_error_titulo", "Error"),
                    self.tr("error_nombre_duplicado", "This name is already used by another account.")
                )
                return

            # 1. GUARDAR EN DISCO
            self.guardar_alias(id_real, nuevo_alias)
            
            # 2. ACTUALIZAR MEMORIA (Importante para que no use datos viejos)
            if "accounts" not in self.datos_pro:
                self.datos_pro["accounts"] = {}
            self.datos_pro["accounts"][id_real] = {"alias": nuevo_alias}

            # 3. REGENERAR LISTA
            nueva_lista, _ = self.obtener_todas_las_cuentas()
            self.combo_cuentas.configure(values=nueva_lista)
            
            # 4. SETEAR EL TEXTO VISUAL (Aquí estaba el error)
            nombre_formateado = f"{nuevo_alias}  |  id: {id_real}"
            self.combo_cuentas.set(nombre_formateado)

            self.ventana_input.destroy()
            messagebox.showinfo(
                self.tr("msg_exito_titulo", "Success"),
                self.tr("nombre_actualizado", "Name updated.")
            )

        ctk.CTkButton(self.ventana_input, text=self.tr("btn_guardar", "Save"), command=confirmar).pack(pady=20)

    def abrir_ajustes_globales(self):
        """Ventana de ajustes con pestañas para una mejor organización."""
        self.ventana_adj = ctk.CTkToplevel(self)
        self.ventana_adj.geometry("550x380")
        self.ventana_adj.resizable(False, False)
        self.ventana_adj.grab_set()
        self.ventana_adj.attributes("-topmost", True)
        
        t = self.idiomas[self.lang]
        
        self.tabview_adj = ctk.CTkTabview(self.ventana_adj, width=500, height=400)
        self.tabview_adj.pack(padx=20, pady=10)

        # 1. GUARDAMOS NOMBRES Y AÑADIMOS PESTAÑAS
        name_gen = t.get("tab_general", "General")
        name_alm = t.get("tab_storage", "Storage")
        # name_apa = t.get("tab_appearance", "Appearance")
        name_abo = t.get("tab_About", "About")

        self.tabview_adj.add(name_gen)
        self.tabview_adj.add(name_alm)
        # self.tabview_adj.add(name_apa)
        self.tabview_adj.add(name_abo)

        # 2. CONTENIDO PESTAÑA: GENERAL
        tab_gen = self.tabview_adj.tab(name_gen)
        self.lbl_lang_ajustes = ctk.CTkLabel(tab_gen, text="", font=("Arial", 12, "bold"))
        self.lbl_lang_ajustes.pack(pady=(10, 5))

        self.entry_busqueda_lang = ctk.CTkEntry(tab_gen)
        self.entry_busqueda_lang.pack(pady=5, fill="x", padx=30)
        self.entry_busqueda_lang.bind("<KeyRelease>", lambda e: self.filtrar_idiomas())

        self.scroll_idiomas = ctk.CTkScrollableFrame(tab_gen, height=220, fg_color="#161b22")
        self.scroll_idiomas.pack(pady=10, fill="both", expand=True, padx=30)

        # 3. CONTENIDO PESTAÑA: ALMACENAMIENTO
        tab_alm = self.tabview_adj.tab(name_alm)
        self.lbl_titulo_ruta = ctk.CTkLabel(tab_alm, text="", font=("Arial", 12, "bold"))
        self.lbl_titulo_ruta.pack(pady=20)
        
        self.lbl_ruta_actual = ctk.CTkLabel(tab_alm, text=f"{self.folder_data}", wraplength=400)
        self.lbl_ruta_actual.pack(pady=10)

        def cambiar_ruta_interna():
            from tkinter import filedialog
            nueva_ruta = filedialog.askdirectory()
            if nueva_ruta:
                with open(self.archivo_semilla, "w") as f:
                    json.dump({"data_path": nueva_ruta}, f)
                self.guardar_en_super_json("config_global", None, "data_path", nueva_ruta)
                t_msg = self.idiomas[self.lang]
                messagebox.showinfo(t_msg.get("msg_exito_titulo", "Success"), t_msg.get("ruta_actualizada", "Restart required"))
                self.ventana_adj.destroy()

        self.btn_cambiar_ruta = ctk.CTkButton(tab_alm, command=cambiar_ruta_interna)
        self.btn_cambiar_ruta.pack(pady=20)

        # 3. CONTENIDO PESTAÑA: APARIENCIA
        # name_apa = self.tabview_adj.tab(name_alm)
        # self.lbl_titulo_ruta = ctk.CTkLabel(tab_alm, text="", font=("Arial", 12, "bold"))
        # self.lbl_titulo_ruta.pack(pady=20)
        
        # 4. CONTENIDO PESTAÑA: ACERCA DE (About)
        tab_abo = self.tabview_adj.tab(name_abo)
        
        # Nombre del Desarrollador
        ctk.CTkLabel(tab_abo, text="VALORANT TRUE STRETCHED CONFIGURATOR", font=("Segoe UI", 16, "bold"), text_color="#ff4655").pack(pady=(10, 0))
        ctk.CTkLabel(tab_abo, text=f"v2.0.0 | {t.get('creditos_por', 'Developed by')}", font=("Segoe UI", 10)).pack()
        ctk.CTkLabel(tab_abo, text="Mauricio Ramirez", font=("Segoe UI", 14, "bold")).pack(pady=(0, 10))

        # 4. CONFIGURACIÓN DE IDIOMAS Y BOTONES
        self.diccionario_global_idiomas = {
            "ES": "Español", "EN": "English", "FR": "Français", "DE": "Deutsch",
            "IT": "Italiano", "PT": "Português", "RU": "Pусский", "JP": "日本語",
            "KO": "한국어", "ZH": "中文"
        }
        
        self.botones_idiomas = {}
        self.generar_lista_idiomas()

        # 5. TRADUCCIÓN FINAL (Ahora sí, todos los objetos existen)
        self.retranslate_ajustes()

        # Botón de GitHub
        def abrir_github():
            import webbrowser
            webbrowser.open("https://github.com/MauricioEsparron/configurador_valorant/tree/main")

        self.btn_github = ctk.CTkButton(tab_abo, text="GitHub Repository", fg_color="#24292e", hover_color="#333", 
                                        command=abrir_github)
        self.btn_github.pack(pady=10)

        # Sección de Donaciones
        ctk.CTkLabel(tab_abo, text=t.get("donaciones_titulo", "Support the Project"), font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
        
        frame_donaciones = ctk.CTkFrame(tab_abo, fg_color="transparent")
        frame_donaciones.pack(pady=5)

        def abrir_link(url):
            import webbrowser
            webbrowser.open(url)

        # Opción 1: PayPal
        self.btn_paypal = ctk.CTkButton(frame_donaciones, text="PayPal", width=100, fg_color="#003087", 
                                            command=lambda: abrir_link("https://paypal.me/mauramirezesparron"))
        self.btn_paypal.pack(side="left", padx=5)

        # Opción 2: Ko-fi / BuyMeACoffee
        self.btn_kofi = ctk.CTkButton(frame_donaciones, text="Ko-fi", width=100, fg_color="#29abe0", 
                                        command=lambda: abrir_link("https://buymeacoffee.com/maxpredator01"))
        self.btn_kofi.pack(side="left", padx=5)

        # Opción 3: Binance Pay (Llama a la función del QR)
        self.btn_otros = ctk.CTkButton(frame_donaciones, text="Binance Pay", width=100, fg_color="#f7931a", 
                                        command=self.mostrar_qr_binance) # <--- CAMBIO AQUÍ
        self.btn_otros.pack(side="left", padx=5)    

        self.lbl_lnk_terminos = ctk.CTkLabel(
            tab_abo, 
            text=t.get("lnk_terminos", "Términos y condiciones"), 
            font=("Segoe UI", 11, "bold", "underline"),
            text_color="#369fc9", # Azul clásico interactivo
            cursor="hand2"
        )
        self.lbl_lnk_terminos.pack(pady=(20, 0))
        
        # Evento de clic para abrir la ventana modal de TyC
        self.lbl_lnk_terminos.bind("<Button-1>", lambda event: self.abrir_ventana_terminos())

    def mostrar_qr_binance(self):
        """Abre una ventana emergente con el código QR de Binance."""
        from PIL import Image
        import os
        
        # 1. Crear la ventana popup
        vent_qr = ctk.CTkToplevel(self)
        vent_qr.title(self.tr("donar_crypto", "Donate with Crypto"))
        vent_qr.geometry("400x600") # Un poco más alto para que quepa el botón abajo
        vent_qr.resizable(False, False)
        vent_qr.grab_set() 
        vent_qr.attributes("-topmost", True)

        # 2. Cargar la imagen
        ruta_qr = resource_path("binance_pay.png") # Asegúrate que el nombre coincida
        
        if os.path.exists(ruta_qr):
            # Usamos Pillow para abrir la imagen
            pil_img = Image.open(ruta_qr)
            
            # Ajustamos el tamaño visual en la app (350x480 aprox para mantener proporción)
            img_qr = ctk.CTkImage(
                light_image=pil_img,
                dark_image=pil_img,
                size=(350, 480)
            )
            
            lbl_img = ctk.CTkLabel(vent_qr, image=img_qr, text="")
            lbl_img.pack(pady=20, padx=20)
        else:
            ctk.CTkLabel(vent_qr, text="Error: binance_pay.png not found").pack(pady=50)

        # 3. Botón para cerrar (Traducido)
        ctk.CTkButton(vent_qr, text=self.tr("btn_cerrar", "Close"), 
                    command=vent_qr.destroy).pack(pady=(0, 20))

    def abrir_ventana_terminos(self):
        """Abre una subventana emergente y centrada con los Términos y Condiciones."""
        ventana_tyc = ctk.CTkToplevel(self)
        ventana_tyc.title(self.idiomas[self.lang].get("titulo_terminos", "Términos y Condiciones"))
        ventana_tyc.geometry("500://450") # Tamaño adecuado para el texto largo
        ventana_tyc.resizable(False, False)
        ventana_tyc.grab_set()
        ventana_tyc.attributes("-topmost", True)
        
        t = self.idiomas[self.lang]
        
        # TextBox con scroll dinámico para que el texto legal quepa perfectamente
        txt_legal = ctk.CTkTextbox(ventana_tyc, width=460, height=340, wrap="word", font=("Segoe UI", 11))
        txt_legal.pack(padx=20, pady=(20, 10))
        
        # Insertar texto e impedir su edición
        txt_legal.insert("0.0", t.get("texto_legal", ""))
        txt_legal.configure(state="disabled")
        
        # Botón de cierre
        btn_cerrar = ctk.CTkButton(
            ventana_tyc, 
            text=t.get("btn_cerrar", "Cerrar"), 
            command=ventana_tyc.destroy,
            fg_color="#ff4655", # Color rojo institucional de Valorant
            hover_color="#b8323d"
        )
        btn_cerrar.pack(pady=(0, 15))

    def retranslate_ajustes(self):
        """Actualiza los textos de la ventana de ajustes."""
        if hasattr(self, 'ventana_adj') and self.ventana_adj.winfo_exists():
            t = self.idiomas[self.lang]
            
            self.ventana_adj.title(t.get("ajustes_titulo", "Settings"))

            # Método compatible con las últimas versiones de CustomTkinter
            try:
                # Intentamos acceder a los botones del SegmentedButton
                # En versiones nuevas, la lista de botones se suele manejar así:
                for btn in self.tabview_adj._segmented_button._buttons_dictionary.values():
                    if btn.cget("text") in ["General", t.get("tab_general")]:
                        btn.configure(text=t.get("tab_general", "General"))
                    elif btn.cget("text") in ["Almacenamiento", t.get("tab_storage")]:
                        btn.configure(text=t.get("tab_storage", "Data"))
                    elif btn.cget("text") in ["Apariencia", t.get("tab_appearance")]:
                        btn.configure(text=t.get("tab_appearance", "Appearance"))
            except:
                # Si falla el acceso interno, al menos traducimos el resto
                pass

            # Traducir el resto de elementos
            self.lbl_lang_ajustes.configure(text=t.get("seleccionar_idioma", "Select Language:"))
            self.entry_busqueda_lang.configure(placeholder_text=t.get("buscar_idioma", "Search..."))
            self.lbl_titulo_ruta.configure(text=t.get("titulo_ruta", "Data Location"))
            self.btn_cambiar_ruta.configure(text=t.get("btn_cambiar_ruta", "Change Path"))

    def filtrar_idiomas(self, event=None):
        """Filtra idiomas mientras el usuario escribe."""
        # VALIDACIÓN DE SEGURIDAD: 
        # Si la ventana no existe o ya se cerró, salimos para evitar el error
        if not hasattr(self, 'ventana_adj') or not self.ventana_adj.winfo_exists():
            return
            
        try:
            texto_busqueda = self.entry_busqueda_lang.get().strip().lower()
            self.generar_lista_idiomas(texto_busqueda)
        except Exception as e:
            # Esto evita que el programa se cierre si el componente desaparece justo al escribir
            print(f"Error en filtrado: {e}")

    def seleccionar_nuevo_idioma(self, codigo):
        """Lógica al hacer clic en un idioma de la lista con scroll."""
        self.lang = codigo
        # 1. Guardar permanentemente en el Super JSON
        self.guardar_en_super_json("config_global", None, "language", codigo)
        
        # 2. Cargar la traducción del archivo externo
        self.idiomas[codigo] = self.cargar_idioma_dinamico(codigo)
        
        # 3. Actualizar toda la interfaz al instante
        self.cambiar_idioma()
        
        # Esto garantiza que hasta los nombres de las pestañas se traduzcan
        if hasattr(self, 'ventana_adj') and self.ventana_adj.winfo_exists():
            self.ventana_adj.destroy()  # Cierra la versión con idioma viejo
            self.abrir_ajustes_globales()  # Abre la versión con idioma nuevo
        
        # 4. Refrescar la lista de botones para resaltar el nuevo seleccionado
        self.filtrar_idiomas(None)


    def actualizar_listado_cuentas(self):
        """Refresca el ComboBox con los nuevos nombres."""
        lista, _ = self.obtener_todas_las_cuentas()
        self.combo_cuentas.configure(values=lista)
        # Seleccionamos el primero de la lista (el recién editado)
        if lista:
            self.combo_cuentas.set(lista[0])

    def extraer_id_real(self, texto_combo):
        """Extrae el ID real reconociendo formatos nuevos y antiguos."""
        
        if not texto_combo:
            return ""

        # Caso formato moderno: cualquier variante de "| id:"
        if "| id:" in texto_combo:
            return texto_combo.split("| id:")[-1].strip()

        if "|  id:" in texto_combo:
            return texto_combo.split("|  id:")[-1].strip()

        if "| id: " in texto_combo:
            return texto_combo.split("| id: ")[-1].strip()

        if " |  id: " in texto_combo:
            return texto_combo.split(" |  id: ")[-1].strip()

        # Caso viejo: Alias (UUID...)
        if "(" in texto_combo and ")" in texto_combo:
            try:
                id_parcial = texto_combo.split("(")[-1].split("...")[0].replace(")", "").strip()

                perfiles = self.cargar_alias()
                for folder_id in perfiles.keys():
                    if folder_id.startswith(id_parcial):
                        return folder_id
            except:
                pass

        # Si ya es ID puro
        return texto_combo.strip()

    def toggle_ultra_fps(self):
        import configparser
        import tkinter.messagebox as messagebox
        
        if not self.ruta_ini or not os.path.exists(self.ruta_ini):
            return
            
        id_real = self.extraer_id_real(self.combo_cuentas.get())
        perfil = self.datos_pro.get("accounts", {}).get(id_real, {})
        fps_data = perfil.get("fps_boost", {})

        # --- CASO 1: ACTIVAR BOOST ---
        if self.switch_fps.get() == 1:
            # Solo capturamos originales si no existen en el perfil de esta cuenta
            if "original_values" not in fps_data:
                config = configparser.ConfigParser()
                config.optionxform = str
                config.read(self.ruta_ini)
                originales = {}
                section = 'ScalabilityGroups'
                if config.has_section(section):
                    for p in self.parametros_fps:
                        originales[p] = config.get(section, p, fallback="3")
                    
                    # Guardamos el backup inicial en el Super JSON
                    fps_data["original_values"] = originales
                    self.guardar_en_super_json("accounts", id_real, "fps_boost", fps_data)
            
            # Abrimos la ventana para que el usuario elija sus niveles
            self.abrir_ventana_opciones_fps()

        # --- CASO 2: DESACTIVAR BOOST (RESTAURAR) ---
        else:
            originales = fps_data.get("original_values", {})
            if originales:
                config = configparser.ConfigParser()
                config.optionxform = str
                config.read(self.ruta_ini)
                
                # Reinyectamos los valores que guardamos en el JSON
                for p, valor in originales.items():
                    config.set('ScalabilityGroups', p, str(valor))
                
                with open(self.ruta_ini, 'w') as f:
                    config.write(f, space_around_delimiters=False)
                
                # Marcamos el boost como inactivo en el JSON
                fps_data["is_active"] = False
                self.guardar_en_super_json("accounts", id_real, "fps_boost", fps_data)
                
                # Mostramos el mensaje de confirmación
                messagebox.showinfo(
                    self.tr("msg_valorant_config_titulo", "VALORANT Config"),
                    self.tr("valores_restaurados", "Original values have been successfully restored.")
                )

    def abrir_ventana_opciones_fps(self):
        """Abre un popup cargando los valores directamente desde el Super JSON."""
        # 1. Identificar cuenta y extraer datos del Super JSON
        id_real = self.extraer_id_real(self.combo_cuentas.get())
        perfil = self.datos_pro.get("accounts", {}).get(id_real, {})
        fps_data = perfil.get("fps_boost", {})

        # 2. Prioridad de precarga: Custom -> Originales -> Vacío (0)
        valores_previuos = fps_data.get("custom_values", {})
        if not valores_previuos:
            valores_previuos = fps_data.get("original_values", {})

        # --- Crear ventana secundaria modal ---
        self.popup = ctk.CTkToplevel(self)
        self.popup.title(self.tr("ultra_fps_titulo", "Ultra FPS Options"))
        self.popup.geometry("450x580")
        self.popup.resizable(False, False)
        self.popup.grab_set() 
        self.popup.attributes("-topmost", True)

        lbl_info = ctk.CTkLabel(self.popup, text=self.tr("elige_opt", "Choose optimization type:"), font=("Segoe UI", 14, "bold"))
        lbl_info.pack(pady=10)

        # Botones Principales
        frame_btns = ctk.CTkFrame(self.popup, fg_color="transparent")
        frame_btns.pack(pady=5)
        
        btn_defecto = ctk.CTkButton(frame_btns, text=self.tr("btn_fps_defecto", "Default (All 0)"), fg_color="#ff4655", hover_color="#a12d36", command=self.aplicar_fps_defecto)
        btn_defecto.pack(side="left", padx=10)

        # Frame contenedor para los inputs manuales
        self.frame_manual = ctk.CTkFrame(self.popup, fg_color="#1a1a1a", border_width=1, border_color="#334155")
        self.frame_manual.pack(pady=15, padx=20, fill="both", expand=True)

        # Validación: Solo números del 0 al 5
        def validar_0_5(P):
            if P == "": return True
            if P.isdigit() and 0 <= int(P) <= 5: return True
            return False
        vcmd = (self.popup.register(validar_0_5), '%P')

        self.entries_fps = {}
        for p in self.parametros_fps:
            row_frame = ctk.CTkFrame(self.frame_manual, fg_color="transparent")
            row_frame.pack(fill="x", padx=10, pady=1)
            
            # Lógica de traducción de etiquetas técnicas:
            # Quitamos "sg." y "Quality" para buscar en el diccionario (ej: "Shadow")
            nombre_limpio = p.replace("sg.", "").replace("Quality", "")
            # Buscamos en el JSON, si no existe, usamos el nombre limpio como fallback
            texto_label = self.tr(nombre_limpio, nombre_limpio)
            
            lbl_p = ctk.CTkLabel(row_frame, text=texto_label, font=("Segoe UI", 10), width=150, anchor="w")
            lbl_p.pack(side="left")
            
            entry_p = ctk.CTkEntry(row_frame, width=50, height=22, validate="key", validatecommand=vcmd)
            valor_a_mostrar = valores_previuos.get(p, "0")
            entry_p.insert(0, str(valor_a_mostrar))
            entry_p.pack(side="right")
            self.entries_fps[p] = entry_p

        btn_guardar_custom = ctk.CTkButton(self.popup, text=self.tr("btn_guardar_custom", "APPLY CUSTOM CONFIGURATION"), fg_color="#4ade80", hover_color="#22c55e", text_color="#000", font=("Segoe UI", 12, "bold"), height=40, width=380, command=self.aplicar_fps_personalizado)
        btn_guardar_custom.pack(pady=20)

        def al_cerrar():
            if self.switch_fps.get() == 1: self.switch_fps.deselect()
            self.popup.destroy()
        self.popup.protocol("WM_DELETE_WINDOW", al_cerrar)


    def aplicar_fps_defecto(self):
        """Aplica ceros y guarda el backup en el Super JSON."""
        import configparser
        id_real = self.extraer_id_real(self.combo_cuentas.get())
        perfil = self.datos_pro.get("accounts", {}).get(id_real, {})

        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(self.ruta_ini)
        section = 'ScalabilityGroups'
        originales = {}
        
        if not config.has_section(section):
            config.add_section(section)
            
        for p in self.parametros_fps:
            originales[p] = config.get(section, p, fallback="3")
            config.set(section, p, "0")

        # TODO AL SUPER JSON
        datos_boost = {
            "is_active": True,
            "custom_values": {p: "0" for p in self.parametros_fps},
            "original_values": originales
        }
        self.guardar_en_super_json("accounts", id_real, "fps_boost", datos_boost)

        with open(self.ruta_ini, 'w') as f:
            config.write(f, space_around_delimiters=False)
        self.popup.destroy()

    def aplicar_fps_personalizado(self):
        """Aplica los valores, genera backup y los guarda en el Super JSON por cuenta."""
        import configparser
        
        # 1. Identificamos la cuenta para saber dónde guardar en el JSON
        id_real = self.extraer_id_real(self.combo_cuentas.get())
        
        config = configparser.ConfigParser()
        config.optionxform = str
        config.read(self.ruta_ini)
        
        section = 'ScalabilityGroups'
        originales = {}
        ajustes_a_guardar_para_siempre = {} 

        if not config.has_section(section):
            config.add_section(section)

        for p in self.parametros_fps:
            # Guardamos el valor original (el juego antes de tocar nada)
            originales[p] = config.get(section, p, fallback="3")
            
            # Obtenemos tu entrada personalizada
            valor_ingresado = self.entries_fps[p].get().strip()
            if valor_ingresado == "":
                valor_ingresado = "0"
                
            ajustes_a_guardar_para_siempre[p] = valor_ingresado
            config.set(section, p, valor_ingresado)

        # --- AQUÍ ESTÁ EL CAMBIO MAESTRO: Todo al Super JSON ---
        datos_boost = {
            "is_active": True,
            "custom_values": ajustes_a_guardar_para_siempre,
            "original_values": originales
        }
        # Guardamos el bloque completo en la sección de la cuenta
        self.guardar_en_super_json("accounts", id_real, "fps_boost", datos_boost)

        # Guardamos en el archivo real del juego (.ini)
        with open(self.ruta_ini, 'w') as f:
            config.write(f, space_around_delimiters=False)
            
        self.popup.destroy()
        messagebox.showinfo(
            self.tr("msg_exito_titulo", "Success"),
            self.tr("perfil_guardado", "Configuration saved to your unified profile.")
        )

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

    def obtener_ruta_datos_inicial(self):
        """Lee el archivo semilla para saber dónde está la carpeta data."""
        import json
        if os.path.exists(self.archivo_semilla):
            try:
                with open(self.archivo_semilla, "r") as f:
                    config = json.load(f)
                    return config.get("data_path", os.path.join(os.path.abspath("."), "data"))
            except:
                pass
        # Si el archivo no existe, usamos la ruta por defecto al lado del exe
        return os.path.join(os.path.abspath("."), "data")

    def cargar_y_migrar_datos(self, crear_archivos=True):
        """Lee el Super JSON o migra archivos antiguos si es la primera vez."""
        
        # Si ya existe el Super JSON, simplemente lo cargamos
        if os.path.exists(self.ruta_perfiles):
            try:
                with open(self.ruta_perfiles, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass

        # Si no existe, creamos la estructura base
        nuevo_super_json = {
            "config_global": {"res_3d_default": 100, "language": "EN"},
            "accounts": {}
        }

        # --- MIGRACIÓN DE ALIAS ---
        ruta_alias_vieja = os.path.join(self.folder_data, "account_names.json")
        if os.path.exists(ruta_alias_vieja):
            try:
                with open(ruta_alias_vieja, "r", encoding="utf-8") as f:
                    viejos_alias = json.load(f)
                    for fid, alias in viejos_alias.items():
                        # Creamos la estructura por cuenta
                        nuevo_super_json["accounts"][fid] = {"alias": alias, "res_3d": 100}
                # OJO: Solo borramos el archivo antiguo si el usuario ya está en su ruta final
                if "onboarding_completed" in nuevo_super_json.get("config_global", {}):
                    os.remove(ruta_alias_vieja)
            except Exception: 
                pass

        # Guardamos el nuevo Super JSON SOLO si ya se completó onboarding
        if crear_archivos:
            os.makedirs(self.folder_data, exist_ok=True)
            os.makedirs(self.folder_backups, exist_ok=True)

            with open(self.ruta_perfiles, "w", encoding="utf-8") as f:
                json.dump(nuevo_super_json, f, indent=4, ensure_ascii=False)
            
        return nuevo_super_json

    def guardar_en_super_json(self, seccion, subseccion, clave, valor):
        """Guarda cualquier dato en el Super JSON y actualiza el archivo."""

        # 🔥 ASEGURAR ESTRUCTURA FÍSICA ANTES DE ESCRIBIR
        os.makedirs(self.folder_data, exist_ok=True)
        os.makedirs(self.folder_backups, exist_ok=True)

        if seccion not in self.datos_pro:
            self.datos_pro[seccion] = {}

        if subseccion:
            if subseccion not in self.datos_pro[seccion]:
                self.datos_pro[seccion][subseccion] = {}

            self.datos_pro[seccion][subseccion][clave] = valor
        else:
            self.datos_pro[seccion][clave] = valor

        try:
            with open(self.ruta_perfiles, "w", encoding="utf-8") as f:
                json.dump(self.datos_pro, f, indent=4, ensure_ascii=False)

        except Exception as e:
            print(f"Error al guardar Super JSON: {e}")

    def setup_ui(self):
        # Contenedor superior con alineación mejorada
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(anchor="ne", padx=15, pady=(10, 0))

        # Ya no cargamos la imagen aquí, usamos la que cargamos en el __init__
        self.btn_refresh = ctk.CTkButton(
            self.top_frame,
            image=self.img_refresh, # <--- Usamos la variable de la clase
            text="" if self.img_refresh else "↻",
            width=32,
            height=32,
            corner_radius=16,
            fg_color="transparent",
            hover_color="#333333",
            command=self.leer_datos_actuales
        )
        self.btn_refresh.pack(side="left", padx=(0, 5))

        # Botón cambio idioma
        # self.switch_lang = ctk.CTkSwitch(
        #     self.top_frame, 
        #     text="English", 
        #     command=self.cambiar_idioma,
        #     progress_color="#ff4655" # Rojo VALORANT para el switch
        # )
        # self.switch_lang.pack(side="left")

        # Botón Configuración (Tuerquita)
        self.btn_config = ctk.CTkButton(
            self.top_frame,
            text="⚙",
            width=32,
            height=32,
            corner_radius=16,
            fg_color="transparent",
            hover_color="#333333",
            font=("Arial", 18),
            command=self.abrir_ajustes_globales
        )
        self.btn_config.pack(side="left", padx=(0, 5))

            # Título y Estado
        self.label_titulo = ctk.CTkLabel(self, text="", font=("Segoe UI", 24, "bold"))
        self.label_titulo.pack(pady=(0, 5))
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

        # --- SECCIÓN DE CUENTAS (UNIFICADA) ---
        # 1. Creamos el contenedor que permite poner cosas una al lado de la otra
        self.container_cuenta_pro = ctk.CTkFrame(self, fg_color="transparent")
        self.container_cuenta_pro.pack(pady=5, padx=20, fill="x")

        # 2. Etiqueta de Cuenta
        self.label_cuenta_fija = ctk.CTkLabel(
            self.container_cuenta_pro, 
            text="", 
            font=("Segoe UI", 12, "bold")
        )
        self.label_cuenta_fija.grid(row=0, column=0, padx=(0, 10))

        # Eventos de la etiqueta (Abrir archivo y efectos Hover)
        self.label_cuenta_fija.configure(cursor="hand2")
        self.label_cuenta_fija.bind("<Button-1>", self.abrir_archivo_config)
        self.label_cuenta_fija.bind("<Enter>", lambda e: self.label_cuenta_fija.configure(text_color="#005f52"))
        self.label_cuenta_fija.bind("<Leave>", lambda e: self.label_cuenta_fija.configure(text_color="#4ade80"))

        # 3. ComboBox de Cuentas
        lista_cuentas, _ = self.obtener_todas_las_cuentas()
        self.combo_cuentas = ctk.CTkComboBox(
            self.container_cuenta_pro,
            values=lista_cuentas,
            width=480, # Aumentamos un poco más para el ID completo (36 chars) + Alias (30 chars)
            height=28,
            state="readonly",
            command=self.cambiar_de_cuenta_manual,
            fg_color="#1a1a1a",          # Fondo principal
            border_color="#4ade80",      # Borde verde

            button_color="#22c55e",      # Flecha más visible
            button_hover_color="#16a34a",# Hover más oscuro

            text_color="#4ade80",        # Texto
            dropdown_text_color="#4ade80",
            dropdown_fg_color="#111827", # Fondo dropdown oscuro
            font=("Segoe UI", 11) # Fuente un poco más pequeña ayuda a que quepa más texto
        )
        # Bloquear escritura en el combobox
        self.combo_cuentas._entry.bind("<Key>", lambda e: "break")
        # Bloquear selección/clic dentro del texto
        self.combo_cuentas._entry.bind("<Button-1>", lambda e: "break")
        self.combo_cuentas._entry.bind("<B1-Motion>", lambda e: "break")
        self.combo_cuentas._entry.bind("<Double-Button-1>", lambda e: "break")
        # Quitar cursor de texto (I-beam)
        self.combo_cuentas._entry.configure(cursor="arrow")
        # Evitar foco visual
        self.combo_cuentas._entry.bind("<FocusIn>", lambda e: self.focus())
        # Bloquear selección por teclado
        self.combo_cuentas._entry.bind("<<Selection>>", lambda e: "break")
        # El sticky="we" hará que se adapte al ancho del contenedor
        self.combo_cuentas.grid(row=0, column=1, sticky="we", padx=(0, 5))

        # 4. Botón de Editar Alias (El lápiz)
        self.btn_editar_alias = ctk.CTkButton(
            self.container_cuenta_pro,
            text="✎",
            width=35,
            height=28,
            fg_color="#1f538d",
            hover_color="#14375e",
            command=self.abrir_ventana_alias
        )
        self.btn_editar_alias.grid(row=0, column=2, padx=(5, 0))

        # Configuración de estiramiento
        self.container_cuenta_pro.columnconfigure(1, weight=1)


        vcmd = (self.register(self.validar_numeros), '%P')
        self.label_res_p = ctk.CTkLabel(self, text="", font=("Segoe UI", 14, "bold"))
        self.label_res_p.pack(pady=(10, 5))
        
        # --- SECCIÓN DE RESOLUCIÓN (ESTILO ORIGINAL CON CHECKBOX EN LÍNEA) ---
        self.frame_inputs = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inputs.pack(pady=5)

        # Fila 0: Ancho (X)
        self.label_x_text = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 12))
        self.label_x_text.grid(row=0, column=0, padx=5, sticky="e") # Volvemos al sticky="e"
        self.entry_x = ctk.CTkEntry(self.frame_inputs, width=120, validate="key", validatecommand=vcmd)
        self.entry_x.grid(row=0, column=1, pady=5)
        self.label_detect_x = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 10), text_color="#94a3b8")
        self.label_detect_x.grid(row=0, column=2, padx=10, sticky="w")

        # Fila 1: Alto (Y)
        self.label_y_text = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 12))
        self.label_y_text.grid(row=1, column=0, padx=5, sticky="e") # Volvemos al sticky="e"
        self.entry_y = ctk.CTkEntry(self.frame_inputs, width=120, validate="key", validatecommand=vcmd)
        self.entry_y.grid(row=1, column=1, pady=5)
        self.label_detect_y = ctk.CTkLabel(self.frame_inputs, text="", font=("Segoe UI", 10), text_color="#94a3b8")
        self.label_detect_y.grid(row=1, column=2, padx=10, sticky="w")

        # Contenedor lateral para el Checkbox y Ayuda (Ocupa las dos filas)
        self.frame_extra_win = ctk.CTkFrame(self.frame_inputs, fg_color="transparent")
        self.frame_extra_win.grid(row=0, column=3, rowspan=2, padx=(15, 0), sticky="ns")

        # --- AQUÍ ESTÁ EL CAMBIO PARA QUE ESTÉN A LA PAR ---
        self.frame_check_horizontal = ctk.CTkFrame(self.frame_extra_win, fg_color="transparent")
        self.frame_check_horizontal.pack(expand=True) # Centra verticalmente en el bloque

        self.check_res_windows = ctk.CTkCheckBox(
            self.frame_check_horizontal, 
            text="", 
            width=20, height=20,
            checkbox_width=18, checkbox_height=18,
            fg_color="#ff4655", hover_color="#a12d36"
        )
        self.check_res_windows.pack(side="left") # Checkbox a la izquierda

        self.btn_help_res = ctk.CTkButton(
            self.frame_check_horizontal, 
            text="?", width=18, height=18, corner_radius=9, 
            fg_color="#334155", 
            command=lambda: self.mostrar_ayuda("res_win")
        )
        self.btn_help_res.pack(side="left", padx=(5, 0)) # Botón "?" justo al lado

        self.label_sug = ctk.CTkLabel(self, text="", font=("Segoe UI", 14, "bold"))
        self.label_sug.pack(pady=(10, 5))

        self.combo_res = ctk.CTkComboBox(
        self,
        width=350,
        state="readonly",
        command=self.on_combo_change
    )

        # Bloquear escritura
        self.combo_res._entry.bind("<Key>", lambda e: "break")

        # Bloquear clic dentro del campo (evita selección y cursor de texto)
        self.combo_res._entry.bind("<Button-1>", lambda e: "break")
        self.combo_res._entry.bind("<B1-Motion>", lambda e: "break")
        self.combo_res._entry.bind("<Double-Button-1>", lambda e: "break")

        # Quitar cursor tipo texto (I-beam)
        self.combo_res._entry.configure(cursor="arrow")

        # Evitar foco visual (quita el palito de escritura)
        self.combo_res._entry.bind("<FocusIn>", lambda e: self.focus())

        # Opcional: deshabilitar selección por teclado (Ctrl+A, Shift, etc.)
        self.combo_res._entry.bind("<<Selection>>", lambda e: "break")

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
        self.slider_calidad.bind("<ButtonRelease-1>", lambda e: self.guardar_pref_3d(self.slider_calidad.get()))
        self.slider_calidad.set(self.valor_3d_inicial)
        self.actualizar_label_slider(self.valor_3d_inicial)

        # Backup
        self.frame_bk = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bk.pack(pady=10, padx=40, fill="x")
        self.btn_crear_bk = ctk.CTkButton(self.frame_bk, text="", fg_color="#94a3b8", hover_color="#64748b", text_color="#000", font=("Segoe UI", 11, "bold"), command=self.crear_backup_manual)
        self.btn_crear_bk.pack(side="left", expand=True, padx=5, fill="x")
        self.btn_restaurar_bk = ctk.CTkButton(self.frame_bk, text="", fg_color="#94a3b8", hover_color="#64748b", text_color="#000", font=("Segoe UI", 11, "bold"), command=self.restaurar_backup)
        self.btn_restaurar_bk.pack(side="right", expand=True, padx=5, fill="x")

        # Switches Opciones
        self.frame_avanzado = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_avanzado.pack(pady=(10, 0), padx=40, fill="x")
        self.switch_fps = ctk.CTkSwitch(self.frame_avanzado, text="", command=self.toggle_ultra_fps)
        self.switch_fps.pack(side="left", padx=(10, 2))
        self.btn_help_fps = ctk.CTkButton(self.frame_avanzado, text="?", width=18, height=18, corner_radius=9, fg_color="#334155", command=lambda: self.mostrar_ayuda("fps"))
        self.btn_help_fps.pack(side="left", padx=(0, 20))
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
        self.label_aviso_bloqueo.pack(pady=(2, 0))

        # Botón Aplicar Rojo
        self.btn_aplicar = ctk.CTkButton(
            self, text="", fg_color="#ff4655", hover_color="#a12d36", 
            height=50, font=("Segoe UI", 16, "bold"), command=self.aplicar
        )
        self.btn_aplicar.pack(pady=15, padx=40, fill="x")
        self.btn_aplicar.bind("<Enter>", lambda e: self.btn_aplicar.configure(height=52, border_width=2, border_color="#ffffff"))
        self.btn_aplicar.bind("<Leave>", lambda e: self.btn_aplicar.configure(height=50, border_width=0))

        # Redes Sociales
        # self.frame_social = ctk.CTkFrame(self, fg_color="transparent")
        # self.frame_social.pack(pady=10)
        # self.crear_soc(self.img_github, "#000", "https://github.com/MauricioEsparron/configurador_valorant")
        # self.crear_soc(self.img_coffee, "#FFDD00", "https://buymeacoffee.com/maxpredator01")
        # self.crear_soc(self.img_stream, "#7FF5D2", "https://streamlabs.com/maxpredator01/tip")

        # --- SECCIÓN DE CRÉDITOS ---
        self.label_creditos = ctk.CTkLabel(self, text="", font=("Segoe UI", 10, "bold"), text_color="#9ca3af")
        self.label_creditos.pack(side="bottom", pady=(0, 10))

        self.label_footer = ctk.CTkLabel(self, text="", font=("Segoe UI", 11, "italic"), text_color="#6b7280")
        self.label_footer.pack(side="bottom", pady=(10, 0))

    def cargar_idioma_dinamico(self, codigo):
        """Busca el JSON de idioma. Si no existe, devuelve un backup básico."""
        import json
        # Construimos la ruta: data/locales/es.json (por ejemplo)
        ruta = resource_path(os.path.join("locales", f"{codigo.lower()}.json"))
        
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al leer el archivo de idioma {codigo}: {e}")
        
                # BACKUP: Diccionario completo para evitar KeyErrors
        return {
            "titulo": "VALORANT TRUE STRETCHED CONFIG",
            "cuenta_ok": "✅ Account detected:",
            "cuenta_no": "❌ No active account detected",
            "res_perso": "Custom Resolution",
            "ancho": "Width (X):",
            "alto": "Height (Y):",
            "detectado": "← Detected",
            "sugeridas": "Suggested resolutions:",
            "btn_aplicar": "APPLY CONFIGURATION",
            "footer": "Close the game before applying changes",
            "creditos": "Developed by Mauricio Ramirez | 10/05/2026 | v2.0.0",
            "combo_init": "Select resolution...",
            "boost": "Ultra FPS Boost",
            "bloquear": "Lock File (Read Only)",
            "calidad_res": "3D Resolution Quality:",
            "btn_crear_bk": "CREATE BACKUP",
            "btn_restaurar_bk": "RETURN TO PREVIOUS",
            "exito": "Applied!\nResolution: {}x{}\n3D Quality: {}%",

            # =========================
            # TITLES / HEADERS
            # =========================
            "msg_exito_titulo": "Success",
            "msg_error_titulo": "Error",
            "msg_aviso_titulo": "Warning",
            "msg_backup_titulo": "Backup",
            "msg_valorant_titulo": "VALORANT",
            "msg_valorant_config_titulo": "VALORANT Config",
            "msg_windows_display_titulo": "Windows Display",

            # =========================
            # INFO MESSAGES
            # =========================
            "nombre_actualizado": "Name updated.",
            "ruta_actualizada": "Path updated. Restart the application.",
            "valores_restaurados": "Original values have been successfully restored.",
            "perfil_guardado": "Configuration saved to your unified profile.",

            # =========================
            # WARNING MESSAGES
            # =========================
            "selecciona_cuenta": "Select an account first.",
            "archivo_no_encontrado": "Configuration file not found.",

            # =========================
            # ERROR MESSAGES
            # =========================
            "error_nombre_longitud": "Must be between 3 and 30 characters.",
            "error_nombre_duplicado": "This name is already used by another account.",
            "error_abrir_archivo": "Could not open file: {}",
            "system_error": "Error: {}",

            # =========================
            # SETTINGS / HELP
            # =========================
            "help_boost": "Forces ultra-low graphical settings that are not available in the standard in-game menus. Changes will be applied to: \n\n sg.ViewDistanceQuality=0,\n sg.AntiAliasingQuality=0,\n sg.ShadowQuality=0,\n sg.PostProcessQuality=0,\n sg.TextureQuality=0,\n sg.EffectsQuality=0,\n sg.FoliageQuality=0,\n sg.ShadingQuality=0,\n sg.GlobalIlluminationQuality=0,\n sg.ReflectionQuality=0\n\n NOTE: You can define the values between 0 and 5.",

            "help_lock": "Sets the file to 'Read Only' so Valorant doesn't change your settings when you close the game. \n\n⚠️ RECOMMENDATION: Disable this option during Valorant updates to avoid patching errors.",

            "help_res": "Changes your desktop resolution to match the game. This prevents the black screen flicker when Alt-Tabbing.",

            # =========================
            # BACKUP
            # =========================
            "bk_exito": "Backup created successfully.",
            "bk_restaurado": "Returned to previous version.",
            "bk_no_existe": "No previous backup found.",

            # =========================
            # EXTRA UI (Recommended)
            # =========================
            "ajustes_titulo": "Application Settings",
            "tab_idioma": "Language",
            "buscar_idioma": "Search language...",
            "idioma_global": "Global Language",
            "btn_guardar": "Save",
            "btn_cancelar": "Cancel",
            "btn_cerrar": "Close",
            "ultra_fps_titulo": "Ultra FPS Options",
            "lnk_terminos": "Terms and conditions",
                "titulo_terminos": "Terms and Conditions of Use",
                "btn_cerrar": "Close",
                "texto_legal": (
                    "TERMS AND CONDITIONS OF USE\n"
                    "Last updated: 05/11/26\n\n"
                    "By downloading, installing or using VAL-ConfigPro, you agree to comply with and be bound by the following terms and conditions. If you do not agree to these terms, do not use the Software.\n\n"
                    "1. Nature of the Service\n"
                    "The Software is an independent technical customization tool designed to optimize and adjust local configuration files (.ini) and the operating system display resolution.\n\n"
                    "2. Third-Party Disclaimer\n"
                    "VAL-ConfigPro is not affiliated, associated, authorized, endorsed by, or in any way officially connected with Riot Games, VALORANT, or any of its subsidiaries or affiliates.\n\n"
                    "The name \"VALORANT\", as well as related names, marks, emblems and images are registered trademarks of their respective owners.\n\n"
                    "The use of this software is at the user's own risk. The developer is not responsible for any sanctions, account suspensions (bans) or restrictions imposed by third parties derived from the use of this tool.\n\n"
                    "3. User Responsibility\n"
                    "The user is solely responsible for:\n"
                    "- Ensuring that the use of the Software does not violate the Terms of Service of the games they decide to optimize.\n"
                    "- Checking the compatibility of display resolutions with their monitor. The developer is not responsible for hardware damage or operating system misconfigurations.\n\n"
                    "4. Intellectual Property\n"
                    "All code, design, and logic of the Software are the exclusive property of Mauricio Ramirez Esparron. Reverse engineering, decompilation, or unauthorized redistribution of the binary without explicit written permission is prohibited.\n\n"
                    "5. Limitation of Liability\n"
                    "To the maximum extent permitted by law, the developer shall not be liable for any direct, indirect, incidental, or special damages arising out of the use or inability to use the Software, including but not limited to loss of data or system interruption.\n\n"
                    "6. Modifications\n"
                    "The developer reserves the right to modify these terms at any time. Continued use of the Software following any changes constitutes acceptance of the new terms."
                ),
            # =========================
            # RESOLUTION OPTIONS
            # =========================
            "win_res_title": "Display Settings",
            "win_res_msg": "Keep these display settings? Reverting in {} seconds.",
            "btn_confirmar": "Keep changes",
            "btn_revertir_ahora": "Revert",
        
            "opciones": [
                "1920x1440 (High / 2K)",
                "1600x1200 (High / Standard)",
                "1440x1080 (Ideal for 1080p monitors)",
                "1280x960 (Balanced / Popular)",
                "1152x864 (Medium Quality)",
                "1024x768 (Low / +FPS Performance)",
                "800x600 (Extreme / Low-end PC)",
                "640x480 (Minimum)"
            ],

            # =========================
            # WINDOWS SYNC
            # =========================
            "res_win": "Sync Windows"
        }

    def crear_soc(self, img, color, url):
        btn = ctk.CTkButton(self.frame_social, text="", image=img, fg_color=color, hover_color=color, width=48, height=48, corner_radius=10, command=lambda: webbrowser.open(url))
        btn.pack(side="left", padx=10)

    def cambiar_idioma(self):
        # --- 1. CARGA DEL DICCIONARIO ---
        if self.lang not in self.idiomas:
            self.idiomas[self.lang] = self.cargar_idioma_dinamico(self.lang)
        
        t = self.idiomas[self.lang]

        # --- 2. ACTUALIZACIÓN DE TEXTOS ESTÁTICOS ---
        self.label_titulo.configure(text=t["titulo"])
        self.label_res_p.configure(text=t["res_perso"])
        self.label_x_text.configure(text=t["ancho"])
        self.label_y_text.configure(text=t["alto"])
        self.label_sug.configure(text=t["sugeridas"])
        self.btn_aplicar.configure(text=t["btn_aplicar"])
        self.btn_crear_bk.configure(text=t["btn_crear_bk"])
        self.btn_restaurar_bk.configure(text=t["btn_restaurar_bk"])
        self.label_calidad.configure(text=t["calidad_res"])
        self.switch_fps.configure(text=t["boost"])
        self.switch_read_only.configure(text=t["bloquear"])
        self.label_footer.configure(text=t["footer"])
        self.label_creditos.configure(text=t["creditos"])
        self.check_res_windows.configure(text=t["res_win"])

        # --- 3. ACTUALIZACIÓN DEL COMBOBOX DE RESOLUCIONES ---
        self.combo_res.configure(values=t["opciones"])
        
        texto_actual_combo = self.combo_res.get()
        
        # TRUCO: Si el texto actual NO contiene una 'x' (que indica resolución numérica)
        # significa que es un placeholder como "Seleccionar..." y debemos traducirlo.
        if "x" not in texto_actual_combo.lower():
            self.combo_res.set(t["combo_init"])

        # --- 4. SECCIÓN DE CUENTAS (Lógica de Alias) ---
        if self.ruta_ini:
            id_carpeta = os.path.basename(os.path.dirname(os.path.dirname(self.ruta_ini)))
            alias_dict = self.cargar_alias()
            
            if id_carpeta in alias_dict:
                datos_cuenta = alias_dict[id_carpeta]
                alias_texto = datos_cuenta.get("alias", "") if isinstance(datos_cuenta, dict) else ""
                nombre_final = f"{alias_texto} | id: {id_carpeta}" if alias_texto else id_carpeta
            else:
                nombre_final = id_carpeta

            self.label_cuenta_fija.configure(
                text=t["cuenta_ok"], 
                text_color="#4ade80", 
                font=("Segoe UI", 12, "bold")
            )
            self.combo_cuentas.set(nombre_final)
        else:
            self.label_cuenta_fija.configure(
                text=t["cuenta_no"], 
                text_color="#f87171", 
                font=("Segoe UI", 12, "bold")
            )
            self.combo_cuentas.set("")


    def generar_lista_idiomas(self, filtro=""):
        """Genera o filtra la lista global de idiomas en la ventana de ajustes."""

        if not hasattr(self, "scroll_idiomas"):
            return

        # Limpiar lista anterior
        for widget in self.scroll_idiomas.winfo_children():
            widget.destroy()

        filtro = filtro.strip().lower()

        self.botones_idiomas = {}

        for codigo, nombre in self.diccionario_global_idiomas.items():
            if filtro in nombre.lower() or filtro in codigo.lower():

                btn = ctk.CTkButton(
                    self.scroll_idiomas,
                    text=nombre,
                    fg_color="#ff4655" if self.lang == codigo else "transparent",
                    anchor="w",
                    command=lambda c=codigo: self.seleccionar_nuevo_idioma(c)
                )

                btn.pack(fill="x", pady=2, padx=5)

                self.botones_idiomas[codigo] = btn

    def seleccionar_idioma_global(self, codigo):
        self.lang = codigo

        # Cargar idioma dinámicamente
        self.idiomas[self.lang] = self.cargar_idioma_dinamico(self.lang)

        # Guardar persistencia
        if "config_global" not in self.datos_pro:
            self.datos_pro["config_global"] = {}

        self.datos_pro["config_global"]["language"] = codigo

        self.guardar_datos_pro()

        # Aplicar inmediatamente
        self.cambiar_idioma()

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
            messagebox.showinfo(
                titulo,
                msg
            )
            
            # 2. Liberamos el bloqueo después de que el usuario cierra el mensaje
            self.after(500, lambda: setattr(self, 'bloqueo_en_progreso', False))

            self.actualizar_estado_interfaz() # <-- Añade esta línea al final

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

            x = self.entry_x.get()
            y = self.entry_y.get()
            cal = self.slider_calidad.get()

            try:
                if self.check_res_windows.get() == 1:
                    # Si esto tiene éxito, mostrar_popup_seguridad_win se encarga de todo
                    if self.cambiar_res_windows(int(x), int(y)):
                        self.mostrar_popup_seguridad_win()
                else:
                    # SOLO si no se marcó Windows, mostramos la ventana clásica blanca
                    messagebox.showinfo(
                        self.tr("msg_exito_titulo"), 
                        self.tr("exito").format(x, y, int(cal))
                    )
            except Exception:
                pass

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
            messagebox.showinfo(
                self.tr("msg_valorant_titulo", "VALORANT"),
                mensaje_final
            )

            self.leer_datos_actuales()
            self.actualizar_estado_interfaz()

        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror(
                self.tr("msg_error_titulo", "Error"),
                str(e)
            )

    def mostrar_ayuda(self, tipo):
        """Muestra la ayuda detallada según el botón presionado."""
        t = self.idiomas[self.lang]
        
        # Lógica para elegir el título y mensaje según el tipo
        if tipo == "fps":
            titulo = t["boost"]
            msg = t["help_boost"]
        elif tipo == "lock":
            titulo = t["bloquear"]
            msg = t["help_lock"]
        elif tipo == "res_win": # <--- NUEVO CASO PARA WINDOWS
            titulo = t["res_win"]
            msg = t["help_res"]
        
        from tkinter import messagebox
        messagebox.showinfo(
            titulo,
            msg
        )

    def crear_backup_manual(self):
        if self.ruta_ini:
            # Creamos un nombre único basado en el ID de la cuenta
            id_cuenta = os.path.basename(os.path.dirname(os.path.dirname(self.ruta_ini)))
            nombre_bk = f"backup_{id_cuenta}.bak"
            ruta_destino = os.path.join(self.folder_backups, nombre_bk)
            
            import shutil
            shutil.copy2(self.ruta_ini, ruta_destino)
            messagebox.showinfo(
                self.tr("msg_backup_titulo", "Backup"),
                self.tr("bk_exito", "Backup created successfully.")
            )

    def restaurar_backup(self):
        if not self.ruta_ini: return
        # Construimos el nombre exacto que usamos al guardar
        id_cuenta = os.path.basename(os.path.dirname(os.path.dirname(self.ruta_ini)))
        path_bk = os.path.join(self.folder_backups, f"backup_{id_cuenta}.bak")
        
        if os.path.exists(path_bk):
            import stat, shutil
            # Quitamos el 'Solo lectura' de Riot para poder escribir el backup
            os.chmod(self.ruta_ini, stat.S_IWRITE)
            shutil.copy2(path_bk, self.ruta_ini)
            messagebox.showinfo(
                self.tr("msg_backup_titulo", "Backup"),
                self.tr("bk_restaurado", "Returned to previous version.")
            )
            self.leer_datos_actuales()
        else:
            messagebox.showwarning(
                self.tr("msg_backup_titulo", "Backup"),
                self.tr("bk_no_existe", "No previous backup found.")
            )

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

    def guardar_pref_3d(self, v):
        """Guarda la resolución 3D directamente en el Super JSON (profiles.json)."""
        valor = int(float(v))
        
        # 1. Obtenemos el ID real de la cuenta seleccionada
        id_real = self.extraer_id_real(self.combo_cuentas.get())
        
        # 2. Guardamos en el perfil de la cuenta dentro del Super JSON
        self.guardar_en_super_json("accounts", id_real, "res_3d", valor)
        
        # 3. OPCIONAL: Actualizamos el valor global por defecto
        self.guardar_en_super_json("config_global", None, "res_3d_default", valor)

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
                messagebox.showerror(
                    self.tr("msg_error_titulo", "Error"),
                    self.tr("error_abrir_archivo", "Could not open file: {}").format(e)
                )
        else:
            from tkinter import messagebox
            messagebox.showwarning(
                self.tr("msg_aviso_titulo", "Warning"),
                self.tr("archivo_no_encontrado", "Configuration file not found.")
            )

    def mostrar_popup_seguridad_win(self):
        self.popup_win = ctk.CTkToplevel(self)
        self.popup_win.title(self.tr("msg_exito_titulo")) # Título: "Éxito"
        self.popup_win.geometry("450x220")
        self.popup_win.attributes("-topmost", True)
        self.popup_win.grab_set()

        self.segundos = 15
        
        # Usamos un icono de check o algo visualmente positivo al inicio
        lbl_msg = ctk.CTkLabel(
            self.popup_win, 
            text=self.tr("win_res_full_info").format(self.segundos),
            wraplength=400,
            font=("Segoe UI", 13),
            justify="center"
        )
        lbl_msg.pack(pady=(30, 10), padx=20)

        def tick():
            if self.segundos > 0:
                self.segundos -= 1
                lbl_msg.configure(text=self.tr("win_res_msg").format(self.segundos))
                self.timer_id = self.after(1000, tick)
            else:
                ejecutar_reversion()

        def confirmar():
            self.after_cancel(self.timer_id)
            self.popup_win.destroy()

        def ejecutar_reversion():
            try: 
                self.after_cancel(self.timer_id)
            except: 
                pass
            
            # 1. Revertimos SOLO Windows
            self.cambiar_res_windows(self.old_win_x, self.old_win_y)
            
            # 2. Desmarcar el checkbox usando el nombre CORRECTO
            # Cambiamos check_res_win por check_res_windows
            if hasattr(self, 'check_res_windows'):
                self.check_res_windows.deselect() 
            
            # 3. Cerrar la ventana
            self.popup_win.destroy()

        # Botones
        frame_btns = ctk.CTkFrame(self.popup_win, fg_color="transparent")
        frame_btns.pack(pady=10)

        ctk.CTkButton(frame_btns, text=self.tr("btn_confirmar"), command=confirmar, width=120).pack(side="left", padx=10)
        ctk.CTkButton(frame_btns, text=self.tr("btn_revertir_ahora"), command=ejecutar_reversion, fg_color="gray", width=120).pack(side="right", padx=10)

        tick()

    def cambiar_res_windows(self, ancho, alto):
        """Cambia la resolución del escritorio de Windows con notificaciones visuales."""
        try:
            import ctypes
            from tkinter import messagebox
            t = self.idiomas[self.lang]

            # 1. Definición de la estructura
            class DEVMODE(ctypes.Structure):
                _fields_ = [
                    ("dmDeviceName", ctypes.c_wchar * 32), ("dmSpecVersion", ctypes.c_ushort),
                    ("dmDriverVersion", ctypes.c_ushort), ("dmSize", ctypes.c_ushort),
                    ("dmDriverExtra", ctypes.c_ushort), ("dmFields", ctypes.c_uint),
                    ("dmOrientation", ctypes.c_short), ("dmPaperSize", ctypes.c_short),
                    ("dmPaperLength", ctypes.c_short), ("dmPaperWidth", ctypes.c_short),
                    ("dmScale", ctypes.c_short), ("dmCopies", ctypes.c_short),
                    ("dmDefaultSource", ctypes.c_short), ("dmPrintQuality", ctypes.c_short),
                    ("dmColor", ctypes.c_short), ("dmDuplex", ctypes.c_short),
                    ("dmYResolution", ctypes.c_short), ("dmTTOption", ctypes.c_short),
                    ("dmCollate", ctypes.c_short), ("dmFormName", ctypes.c_wchar * 32),
                    ("dmLogPixels", ctypes.c_ushort), ("dmBitsPerPel", ctypes.c_uint),
                    ("dmPelsWidth", ctypes.c_uint), ("dmPelsHeight", ctypes.c_uint),
                    ("dmDisplayFlags", ctypes.c_uint), ("dmDisplayFrequency", ctypes.c_uint),
                ]

            user32 = ctypes.windll.user32
            dm = DEVMODE()
            dm.dmSize = ctypes.sizeof(DEVMODE)

            # 2. CAPTURA: Antes de modificar 'dm', obtenemos la resolución ACTUAL
            if user32.EnumDisplaySettingsW(None, -1, ctypes.byref(dm)):
                self.old_win_x = dm.dmPelsWidth  # Guardamos el punto de retorno
                self.old_win_y = dm.dmPelsHeight

                # 3. APLICACIÓN: Ahora sí, configuramos los nuevos valores
                dm.dmPelsWidth = int(ancho)
                dm.dmPelsHeight = int(alto)
                dm.dmFields = 0x00080000 | 0x00100000
                
                # Aplicamos el cambio (1 = Permanente/Registro)
                resultado = user32.ChangeDisplaySettingsW(ctypes.byref(dm), 1)
                
                if resultado != 0:
                    # Si falla, avisamos al usuario con una ventana
                    error_msg = f"Windows rejected {ancho}x{alto}. Code: {resultado}" if self.lang == "EN" else f"Windows rechazó {ancho}x{alto}. Código: {resultado}"
                    messagebox.showwarning(
                        self.tr("msg_windows_display_titulo", "Windows Display"), error_msg
                    )
                return True # Cambio exitoso, podemos lanzar el popup         
                    
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror(
                self.tr("msg_error_titulo", "Error"),
                self.tr("system_error", "Error: {}").format(str(e))
            )

if __name__ == "__main__":
    app = ValorantConfigApp()
    app.mainloop()