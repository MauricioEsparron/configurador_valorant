import os
import re
import webbrowser
import customtkinter as ctk
from tkinter import messagebox
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ValorantConfigApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VALORANT Stretched Res Configurator")
        self.geometry("520x750")
        self.resizable(False, False)

        self.idiomas = {
            "ES": {
                "titulo": "VALORANT 4:3 CONFIG",
                "cuenta_ok": "✅ Cuenta detectada:",
                "cuenta_no": "❌ No se detectó cuenta activa",
                "res_perso": "Resolución Personalizada",
                "ancho": "Ancho (X)",
                "alto": "Alto (Y)",
                "sugeridas": "Resoluciones sugeridas:",
                "btn_aplicar": "APLICAR CONFIGURACIÓN",
                "footer": "Cierra el juego antes de aplicar los cambios",
                "donar": "Apoyar el proyecto ☕",
                "repo": "Ver Código en GitHub 📂",
                "combo_init": "Seleccionar resolución...",
                "exito": "¡Configuración aplicada!\nResolución: {}x{}\n\nRecuerda ajustar la escala en tu panel de video.",
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
                "ancho": "Width (X)",
                "alto": "Height (Y)",
                "sugeridas": "Suggested resolutions:",
                "btn_aplicar": "APPLY CONFIGURATION",
                "footer": "Close the game before applying changes",
                "donar": "Support the project ☕",
                "repo": "View Code on GitHub 📂",
                "combo_init": "Select resolution...",
                "exito": "Configuration applied!\nResolution: {}x{}\n\nRemember to adjust scaling in your video panel.",
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

    def abrir_url(self, url):
        webbrowser.open_new_tab(url)

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
            id_query = last_user_id.lower()
            base_path = os.path.join(local_appdata, 'VALORANT', 'Saved', 'Config')
            
            if os.path.exists(base_path):
                for carpeta in os.listdir(base_path):
                    if id_query.replace("-","") in carpeta.lower().replace("-",""):
                        ruta = os.path.join(base_path, carpeta, 'WindowsClient', 'GameUserSettings.ini')
                        if os.path.exists(ruta): return ruta
            return None
        except: return None

    def cambiar_idioma(self):
        self.lang = "EN" if self.switch_lang.get() == 1 else "ES"
        t = self.idiomas[self.lang]
        
        self.label_titulo.configure(text=t["titulo"])
        self.label_res_p.configure(text=t["res_perso"])
        self.entry_x.configure(placeholder_text=t["ancho"])
        self.entry_y.configure(placeholder_text=t["alto"])
        self.label_sug.configure(text=t["sugeridas"])
        self.btn_aplicar.configure(text=t["btn_aplicar"])
        self.label_footer.configure(text=t["footer"])
        self.btn_donar.configure(text=t["donar"])
        self.btn_github.configure(text=t["repo"])
        
        texto_actual = self.combo_res.get()
        if texto_actual in ["CTkComboBox", "", self.idiomas["ES"]["combo_init"], self.idiomas["EN"]["combo_init"]]:
            self.combo_res.set(t["combo_init"])
        
        self.combo_res.configure(values=t["opciones"])
        
        if self.ruta_ini:
            nombre = os.path.basename(os.path.dirname(os.path.dirname(self.ruta_ini)))
            self.label_estado.configure(text=f"{t['cuenta_ok']} {nombre}")
        else:
            self.label_estado.configure(text=t["cuenta_no"])

    def setup_ui(self):
        # 1. Switch de Idioma
        self.switch_lang = ctk.CTkSwitch(self, text="English", command=self.cambiar_idioma)
        self.switch_lang.pack(anchor="ne", padx=20, pady=10)

        # 2. Título principal
        self.label_titulo = ctk.CTkLabel(self, text="", font=("Segoe UI", 26, "bold"))
        self.label_titulo.pack(pady=(5, 10))

        # 3. Estado de cuenta
        self.label_estado = ctk.CTkLabel(self, text="", font=("Segoe UI", 13, "bold"))
        self.label_estado.pack(pady=5)

        # 4. Frame de Resolución Personalizada
        frame = ctk.CTkFrame(self, fg_color="#2b2b2b")
        frame.pack(pady=15, padx=40, fill="x")
        
        self.label_res_p = ctk.CTkLabel(frame, text="", font=("Segoe UI", 12, "bold"))
        self.label_res_p.pack(pady=5)
        
        self.entry_x = ctk.CTkEntry(frame, height=35)
        self.entry_x.pack(pady=8, padx=30, fill="x")

        self.entry_y = ctk.CTkEntry(frame, height=35)
        self.entry_y.pack(pady=8, padx=30, fill="x")

        # 5. Sección de Resoluciones Sugeridas
        self.label_sug = ctk.CTkLabel(self, text="", font=("Segoe UI", 12))
        self.label_sug.pack(pady=(10, 0))
        
        self.combo_res = ctk.CTkComboBox(self, values=[], command=self.set_res, width=300)
        self.combo_res.pack(pady=10)

        # 6. Botón Aplicar
        self.btn_aplicar = ctk.CTkButton(self, text="", fg_color="#ff4655", hover_color="#bd3944", 
                                         height=45, font=("Segoe UI", 14, "bold"), command=self.aplicar)
        self.btn_aplicar.pack(pady=20, padx=40, fill="x")

        # 7. Sección Social y Donaciones
        self.frame_social = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_social.pack(pady=10, padx=40, fill="x")

        self.btn_github = ctk.CTkButton(self.frame_social, text="", fg_color="#333333", hover_color="#444444", 
                                        height=32, command=lambda: self.abrir_url("https://github.com"))
        self.btn_github.pack(pady=5, fill="x")

        self.frame_donar = ctk.CTkFrame(self.frame_social, fg_color="transparent")
        self.frame_donar.pack(fill="x", pady=5)

        self.btn_donar = ctk.CTkButton(self.frame_donar, text="", fg_color="#FFDD00", text_color="black", hover_color="#FFEA00", 
                                       height=32, font=("Segoe UI", 11, "bold"), 
                                       command=lambda: self.abrir_url("https://buymeacoffee.com"))
        self.btn_donar.pack(side="left", padx=(0, 5), expand=True, fill="x")

        self.btn_stream = ctk.CTkButton(self.frame_donar, text="Streamlabs 🎮", fg_color="#31f7ed", text_color="black", hover_color="#29d9d0", 
                                        height=32, font=("Segoe UI", 11, "bold"), 
                                        command=lambda: self.abrir_url("https://streamlabs.com"))
        self.btn_stream.pack(side="left", padx=(5, 0), expand=True, fill="x")

        # 8. Pie de página
        self.label_footer = ctk.CTkLabel(self, text="", font=("Segoe UI", 10), text_color="gray")
        self.label_footer.pack(side="bottom", pady=10)

        self.cambiar_idioma()

    def set_res(self, choice):
        match = re.search(r'(\d+)x(\d+)', choice)
        if match:
            x, y = match.groups()
            self.entry_x.delete(0, 'end')
            self.entry_x.insert(0, x)
            self.entry_y.delete(0, 'end')
            self.entry_y.insert(0, y)

    def actualizar_o_insertar(self, contenido, clave, valor, ancla=None):
        if re.search(rf'^{clave}=.*', contenido, re.MULTILINE):
            return re.sub(rf'^{clave}=.*', f'{clave}={valor}', contenido, flags=re.MULTILINE)
        else:
            if ancla and re.search(rf'^{ancla}=.*', contenido, re.MULTILINE):
                return re.sub(rf'^({ancla}=.*)', rf'\1\n{clave}={valor}', contenido, flags=re.MULTILINE)
            return contenido.replace('[/Script/Engine.GameUserSettings]', f'{clave}={valor}\n\n[/Script/Engine.GameUserSettings]')

    def aplicar(self):
        t = self.idiomas[self.lang]
        if not self.ruta_ini: return
        x, y = self.entry_x.get().strip(), self.entry_y.get().strip()
        if not x.isdigit() or not y.isdigit(): return
        try:
            with open(self.ruta_ini, 'r', encoding='utf-8') as f:
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
                contenido = self.actualizar_o_insertar(contenido, clave, valor)
            contenido = self.actualizar_o_insertar(contenido, 'FullscreenMode', '2', ancla='HDRDisplayOutputNits')
            patron_scal = r'\[ScalabilityGroups\].*?(?=\n\[|$)'
            nuevo_scal = "[ScalabilityGroups]\nsg.ResolutionQuality=65.000000\nsg.ViewDistanceQuality=0\nsg.AntiAliasingQuality=0\nsg.ShadowQuality=0\nsg.PostProcessQuality=0\nsg.TextureQuality=0\nsg.EffectsQuality=0\nsg.FoliageQuality=0\nsg.ShadingQuality=0\nsg.GlobalIlluminationQuality=0\nsg.ReflectionQuality=0"
            contenido = re.sub(patron_scal, nuevo_scal, contenido, flags=re.DOTALL)
            with open(self.ruta_ini, 'w', encoding='utf-8') as f:
                f.write(contenido)
            messagebox.showinfo("Success / Éxito", t["exito"].format(x, y))
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = ValorantConfigApp()
    app.mainloop()
