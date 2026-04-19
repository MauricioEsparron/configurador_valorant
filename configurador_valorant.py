import os
import re
import stat
import shutil
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
import sys
import ctypes
from PIL import Image

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
        self.geometry("550x720") 
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
                "creditos": "Developed by Mauricio Ramirez | 16/04/2026 | v1.0.0", # <--- NUEVO
                "combo_init": "Select resolution...",
                "boost": "Ultra FPS Boost",
                "bloquear": "Lock File (Read Only)",
                "calidad_res": "3D Resolution Quality:",
                "btn_crear_bk": "CREATE BACKUP",
                "btn_restaurar_bk": "RETURN TO PREVIOUS",
                "exito": "Applied!\nResolution: {}x{}\n3D Quality: {}%",
                "help_boost": "Forces ultra-low graphics settings not available in normal menus.\nAll values will be set to 0.",
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
        self.ruta_ini = self.obtener_ruta_activa()
        
        self.setup_ui()
        self.cambiar_idioma() 
        self.leer_datos_actuales()
        self.crear_acceso_directo_inicio()

    # --- LÓGICA DE VALIDACIÓN (SÓLO NÚMEROS) ---
    def validar_numeros(self, P):
        return P == "" or P.isdigit()

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
            self.actualizar_label_slider(num) # Esto dispara el cambio de color

        except: pass

    def setup_ui(self):
        self.switch_lang = ctk.CTkSwitch(self, text="English", command=self.cambiar_idioma)
        self.switch_lang.pack(anchor="ne", padx=20, pady=10)

        self.label_titulo = ctk.CTkLabel(self, text="", font=("Segoe UI", 24, "bold"))
        self.label_titulo.pack(pady=5)
        self.label_estado = ctk.CTkLabel(self, text="", font=("Segoe UI", 12))
        self.label_estado.pack(pady=5)

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
        self.switch_fps = ctk.CTkSwitch(self.frame_avanzado, text="")
        self.switch_fps.pack(side="left", padx=(10, 2))
        self.btn_help_fps = ctk.CTkButton(self.frame_avanzado, text="?", width=18, height=18, corner_radius=9, fg_color="#334155", command=lambda: self.mostrar_ayuda("fps"))
        self.btn_help_fps.pack(side="left", padx=(0, 20))
        self.switch_read_only = ctk.CTkSwitch(self.frame_avanzado, text="")
        self.switch_read_only.pack(side="left", padx=(10, 2))
        self.btn_help_lock = ctk.CTkButton(self.frame_avanzado, text="?", width=18, height=18, corner_radius=9, fg_color="#334155", command=lambda: self.mostrar_ayuda("lock"))
        self.btn_help_lock.pack(side="left")

        # Botón Aplicar Rojo
        self.btn_aplicar = ctk.CTkButton(self, text="", fg_color="#ff4655", hover_color="#a12d36", height=50, font=("Segoe UI", 16, "bold"), command=self.aplicar)
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
        if self.ruta_ini:
            nombre = os.path.basename(os.path.dirname(os.path.dirname(self.ruta_ini)))
            # Solo cambiamos el texto, el color y ponemos la letra en BOLD
            self.label_estado.configure(
                text=f"{t['cuenta_ok']} {nombre}", 
                text_color="#4ade80",
                font=("Segoe UI", 13, "bold") 
            )
        else: 
            self.label_estado.configure(
                text=t["cuenta_no"], 
                text_color="#f87171",
                font=("Segoe UI", 12, "normal")
            )
    def actualizar_o_insertar(self, contenido, clave, valor, ancla=None):
        if re.search(rf'^{clave}=.*', contenido, re.MULTILINE):
            return re.sub(rf'^{clave}=.*', f'{clave}={valor}', contenido, flags=re.MULTILINE)
        else:
            if ancla and re.search(rf'^{ancla}=.*', contenido, re.MULTILINE):
                return re.sub(rf'^({ancla}=.*)', rf'\1\n{clave}={valor}', contenido, flags=re.MULTILINE)
            return contenido.replace('[/Script/Engine.GameUserSettings]', f'{clave}={valor}\n\n[/Script/Engine.GameUserSettings]')

    # --- RESTO DE LÓGICA (backup, aplicar, ayuda...) ---
    def aplicar(self):
        t = self.idiomas[self.lang]
        if not self.ruta_ini: return
        
        x, y = self.entry_x.get().strip(), self.entry_y.get().strip()
        if not x.isdigit() or not y.isdigit(): return
        
        cal_valor = int(self.slider_calidad.get())
        cal_formato = f"{cal_valor}.000000"
        
        try:
            with open(self.ruta_ini, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            # 1. Parámetros generales y de resolución
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
                contenido = self.actualizar_o_insertar(contenido, clave, valor)
            
            contenido = self.actualizar_o_insertar(contenido, 'FullscreenMode', '2', ancla='HDRDisplayOutputNits')
            
            # 2. Manejo de Calidad 3D (Siempre se actualiza según el Slider)
            contenido = re.sub(r'sg\.ResolutionQuality=.*', f'sg.ResolutionQuality={cal_formato}', contenido)
            
            # 3. LÓGICA DE IMPULSO FPS ULTRA (Solo si el switch está activado)
            if self.switch_fps.get():
                ajustes_fps = [
                    "sg.ViewDistanceQuality", "sg.AntiAliasingQuality", "sg.ShadowQuality", 
                    "sg.PostProcessQuality", "sg.TextureQuality", "sg.EffectsQuality", 
                    "sg.FoliageQuality", "sg.ShadingQuality", "sg.GlobalIlluminationQuality", 
                    "sg.ReflectionQuality"
                ]
                for k in ajustes_fps:
                    contenido = re.sub(f'{k}=.*', f'{k}=0', contenido)

            # Escribir cambios
            with open(self.ruta_ini, 'w', encoding='utf-8') as f:
                f.write(contenido)
            
            # Mensaje de éxito con los 3 valores corregidos
            messagebox.showinfo("VALORANT", t["exito"].format(x, y, cal_valor))
            
            self.leer_datos_actuales() # Refrescar flechas de detección
            
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def mostrar_ayuda(self, tipo):
        t = self.idiomas[self.lang]
        msg = t["help_boost"] if tipo == "fps" else t["help_lock"]
        messagebox.showinfo("Ayuda", msg)

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

if __name__ == "__main__":
    app = ValorantConfigApp()
    app.mainloop()
