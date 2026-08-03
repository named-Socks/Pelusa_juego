
"""
Regina-Alan-Fatima-Iván
"""
#librerías
import tkinter as tk
from tkinter import messagebox
import random
import os

try:
    from PIL import Image, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


# ============================================================
#                       CONFIGURACIÓN
# ============================================================
#rutas de las imágenes, los valores de las cartas, el tamaño visual y las paletas de colores y las letras
CARPETA_IMAGENES = "cartas"
PATRON_NOMBRE_IMAGEN = "Pelusa_{numero}.jpg"
NUMEROS = list(range(1, 11))

#img en el centro
TAMANO_IMAGEN = (280, 400)

#colores
COLORES = {
    "fondo": "#f0e6d2",
    "texto_principal": "#2c3e50",
    "boton_robar": "#27ae60",
    "boton_robar_rival": "#2980b9",
    "boton_detener": "#c0392b",
    "boton_deshabilitado": "#bdc3c7",
    "texto_boton": "#ffffff"
}

# 
FUENTES = {
    "titulo": ("Segoe UI", 24, "bold"),
    "subtitulo": ("Segoe UI", 16, "bold"),
    "puntos": ("Consolas", 11, "bold"), 
    "zona_activa": ("Segoe UI", 13),
    "mensaje": ("Segoe UI", 12, "italic"),
    "boton": ("Segoe UI", 12, "bold"),
    "extra": ("Segoe UI", 10)
}


# ============================================================
#                       LÓGICA DEL JUEGO
# ============================================================
# 
# 
#clases poo: la estructura individual de la Carta, el comportamiento y puntajes del Jugador y del Mazo de cartas.

class Carta:
    def __init__(self, numero):
        self.numero = numero
        self.imagen_archivo = PATRON_NOMBRE_IMAGEN.format(numero=numero)


class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.banco = []      #puntos seguros
        self.zona_activa = []  #acumuladas

    def tiene_numero(self, numero):
        return any(c.numero == numero for c in self.zona_activa)

    def aspirar(self):
        """Pasa las cartas de la zona activa al banco definitivo de puntos"""
        cant = len(self.zona_activa)
        if cant > 0:
            self.banco.extend(self.zona_activa)
            self.zona_activa = []
        return cant

    @property
    def puntos_totales(self):
        """Suma los valores numéricos de las cartas aspiradas"""
        return sum(c.numero for c in self.banco)


class Mazo:
    def __init__(self, num_jugadores):
        self.cartas = []
        # 2 y 3 jugadores -> 50 cartas | 4 y 5 jugadores -> 100 cartas
        if num_jugadores <= 3:
            self.copias_por_numero = 5   
        else:
            self.copias_por_numero = 10  
            
        self.generar()

    def generar(self):
        self.cartas = []
        for numero in NUMEROS:
            for _ in range(self.copias_por_numero):
                self.cartas.append(Carta(numero))
        random.shuffle(self.cartas)

    def robar(self):
        if not self.cartas:
            return None
        return self.cartas.pop()

    def quedan_cartas(self):
        return len(self.cartas) > 0


# ============================================================
#                       INTERFAZ (TKINTER)
# ============================================================
# Controla la interfaz gráfica principal con Tkinter, gestionando la navegación entre el menú de inicio, la captura de nombres y la ventana interactiva del juego.

class JuegoPelusas:
    def __init__(self, root):
        self.root = root
        self.root.title("¡Pelusas! - Juego de Cartas")
        self.root.geometry("900x800")
        self.root.configure(bg=COLORES["fondo"])

        self.imagenes_cache = {}
        self.ultima_carta_robada = None
        self.cantidad_jugadores_actual = 3
        self.nombres_guardados = []
        self.frame_juego = None
        self.frame_menu = None

        self._mostrar_menu_inicial()

    def _limpiar_pantalla(self):
        """Destruye los frames activos para poder cambiar de vista limpiamente"""
        if self.frame_menu:
            self.frame_menu.destroy()
            self.frame_menu = None
        if self.frame_juego:
            self.frame_juego.destroy()
            self.frame_juego = None

    def _mostrar_menu_inicial(self):
        """Pantalla inicial para elegir cuántos jugadores van a participar"""
        self._limpiar_pantalla()

        self.frame_menu = tk.Frame(self.root, bg=COLORES["fondo"])
        self.frame_menu.pack(expand=True)

        tk.Label(
            self.frame_menu, text="¡PELUSAS!", font=FUENTES["titulo"],
            bg=COLORES["fondo"], fg=COLORES["texto_principal"]
        ).pack(pady=30)

        tk.Label(
            self.frame_menu, text="Selecciona la cantidad de jugadores:",
            font=FUENTES["zona_activa"], bg=COLORES["fondo"]
        ).pack(pady=10)

        frame_botones_num = tk.Frame(self.frame_menu, bg=COLORES["fondo"])
        frame_botones_num.pack(pady=20)

        for n in range(2, 6):
            cartas_txt = "50 cartas" if n <= 3 else "100 cartas"
            btn = tk.Button(
                frame_botones_num, 
                text=f"{n} Jugadores\n({cartas_txt})", 
                font=FUENTES["extra"],
                bg=COLORES["boton_robar"], fg=COLORES["texto_boton"], width=16, height=2,
                relief="flat", cursor="hand2",
                command=lambda num=n: self._pedir_nombres_jugadores(num)
            )
            btn.pack(side="left", padx=10)

    def _pedir_nombres_jugadores(self, cantidad_jugadores):
        """Pantalla para escribir los nombres de cada uno de los jugadores"""
        self._limpiar_pantalla()
        self.cantidad_jugadores_actual = cantidad_jugadores

        self.frame_menu = tk.Frame(self.root, bg=COLORES["fondo"])
        self.frame_menu.pack(expand=True)

        tk.Label(
            self.frame_menu, text="Introduce los nombres de los jugadores:",
            font=FUENTES["subtitulo"], bg=COLORES["fondo"], fg=COLORES["texto_principal"]
        ).pack(pady=30)

        self.entries_nombres = []
        frame_entradas = tk.Frame(self.frame_menu, bg=COLORES["fondo"])
        frame_entradas.pack(pady=15)

        for i in range(cantidad_jugadores):
            row_frame = tk.Frame(frame_entradas, bg=COLORES["fondo"])
            row_frame.pack(pady=8)

            lbl = tk.Label(
                row_frame, text=f"Jugador {i+1}:", font=FUENTES["zona_activa"],
                bg=COLORES["fondo"], width=10, anchor="e"
            )
            lbl.pack(side="left", padx=8)

            entry = tk.Entry(row_frame, font=FUENTES["zona_activa"], width=25, relief="solid")
            entry.insert(0, f"Jugador {i+1}")
            entry.pack(side="left", padx=8)
            self.entries_nombres.append(entry)

        btn_comenzar = tk.Button(
            self.frame_menu, text="¡Empezar Partida!", font=FUENTES["boton"],
            bg=COLORES["boton_robar_rival"], fg=COLORES["texto_boton"], width=22, height=2,
            relief="flat", cursor="hand2",
            command=self._procesar_nombres_y_empezar
        )
        btn_comenzar.pack(pady=35)

    def _procesar_nombres_y_empezar(self):
        """Recoge los nombres escritos y arranca el juego"""
        self.nombres_guardados = []
        for i, entry in enumerate(self.entries_nombres):
            nombre = entry.get().strip()
            if not nombre:
                nombre = f"Jugador {i+1}"
            self.nombres_guardados.append(nombre)

        self._iniciar_partida()

    def _iniciar_partida(self):
        """Inicializa la partida con los nombres definidos"""
        self._limpiar_pantalla()

        self.jugadores = [Jugador(nombre) for nombre in self.nombres_guardados]
        self.mazo = Mazo(self.cantidad_jugadores_actual)
        self.turno_actual = 0

        self._crear_interfaz_juego()
        self._iniciar_turno()

        if not PIL_DISPONIBLE:
            self.label_mensaje.config(
                text="(Pillow no está instalado: se mostrarán números en vez de imágenes.)"
            )

    def _reiniciar_partida(self):
        """Reinicia el juego con los mismos jugadores y sus mismos nombres"""
        if messagebox.askyesno("Reiniciar", "¿Estás seguro de que quieres reiniciar la partida actual?"):
            self._iniciar_partida()

    def _volver_al_menu(self):
        """Regresa a la pantalla de selección de jugadores"""
        if messagebox.askyesno("Salir al menú", "¿Quieres salir al menú principal para cambiar de jugadores?"):
            self._mostrar_menu_inicial()

    def _crear_interfaz_juego(self):
        """Rediseño visual completo de la interfaz de juego activa."""
        self.frame_juego = tk.Frame(self.root, bg=COLORES["fondo"])
        self.frame_juego.pack(fill="both", expand=True, padx=20, pady=10)

        # 1. PANEL SUPERIOR: Turno y Puntajes Globales
        frame_header = tk.Frame(self.frame_juego, bg=COLORES["fondo"])
        frame_header.pack(fill="x", pady=(0, 10))

        self.label_turno = tk.Label(
            frame_header, text="Turno de:", font=FUENTES["subtitulo"], 
            bg=COLORES["fondo"], fg=COLORES["texto_principal"]
        )
        self.label_turno.pack(anchor="w")

        # Contenedor para puntajes con fondo blanco
        frame_scores = tk.Frame(frame_header, bg="#ffffff", relief="solid", bd=1)
        frame_scores.pack(fill="x", pady=5)
        
        self.label_puntajes = tk.Label(
            frame_scores, text="", font=FUENTES["puntos"], 
            bg="#ffffff", fg=COLORES["texto_principal"], pady=6, wraplength=840
        )
        self.label_puntajes.pack(fill="x")

        # 2. PANEL CENTRAL: La Carta y la Zona Activa
        frame_central = tk.Frame(self.frame_juego, bg=COLORES["fondo"])
        frame_central.pack(fill="both", expand=True, pady=5)
        
        # --- Carta Grande ---
        self.frame_carta = tk.Frame(
            frame_central, bg="#ffffff", 
            width=TAMANO_IMAGEN[0] + 10, height=TAMANO_IMAGEN[1] + 10,
            relief="ridge", bd=3
        )
        self.frame_carta.pack(pady=5)
        self.frame_carta.pack_propagate(False)

        self.label_imagen = tk.Label(self.frame_carta, bg="#ffffff")
        self.label_imagen.pack(expand=True)

        # --- Zona Activa (Debajo de la carta, destacada) ---
        frame_info_turno = tk.Frame(frame_central, bg=COLORES["fondo"])
        frame_info_turno.pack(fill="x", pady=5)

        tk.Label(
            frame_info_turno, text="TU ZONA ACTIVA (Cartas en riesgo):", 
            font=FUENTES["extra"], bg=COLORES["fondo"], fg="#7f8c8d"
        ).pack()

        self.label_cartas_turno = tk.Label(
            frame_info_turno, text="", font=("Segoe UI", 15, "bold"), 
            bg=COLORES["fondo"], fg="#e67e22", wraplength=840
        )
        self.label_cartas_turno.pack(pady=(2, 4))

        self.label_otros = tk.Label(
            self.frame_juego, text="", font=("Segoe UI", 9), 
            bg=COLORES["fondo"], fg="#7f8c8d", wraplength=840
        )
        self.label_otros.pack(pady=2)

        # 3. PANEL DE BOTONES (Grandes y Estilo Plano)
        frame_botones = tk.Frame(self.frame_juego, bg=COLORES["fondo"])
        frame_botones.pack(pady=10)

        estilo_btn = {
            "font": FUENTES["boton"],
            "fg": COLORES["texto_boton"],
            "relief": "flat",
            "cursor": "hand2",
            "width": 18,
            "pady": 8
        }

        self.btn_robar = tk.Button(
            frame_botones, text="Robar del mazo", 
            command=self.robar_carta, bg=COLORES["boton_robar"], **estilo_btn
        )
        self.btn_robar.grid(row=0, column=0, padx=10)

        self.btn_robar_otro = tk.Button(
            frame_botones, text="Robar a rivales", 
            command=self.ejecutar_robo_rivales, bg=COLORES["boton_robar_rival"], **estilo_btn
        )
        self.btn_robar_otro.grid(row=0, column=1, padx=10)

        self.btn_detener = tk.Button(
            frame_botones, text="Detener turno", 
            command=self.detener_turno, bg=COLORES["boton_detener"], **estilo_btn
        )
        self.btn_detener.grid(row=0, column=2, padx=10)

        # 4. PANEL INFERIOR: Mensajes y Mazo
        self.label_mensaje = tk.Label(
            self.frame_juego, text="", font=FUENTES["mensaje"], 
            bg=COLORES["fondo"], fg=COLORES["texto_principal"], height=2
        )
        self.label_mensaje.pack(pady=5)

        self.label_mazo = tk.Label(
            self.frame_juego, text="", font=FUENTES["extra"], 
            bg=COLORES["fondo"], fg="#95a5a6"
        )
        self.label_mazo.pack(pady=(0, 5))

        # Barra inferior de opciones extra
        frame_opciones_extra = tk.Frame(self.frame_juego, bg=COLORES["fondo"])
        frame_opciones_extra.pack(fill="x", side="bottom", pady=5)

        btn_reiniciar = tk.Button(
            frame_opciones_extra, text="🔄 Reiniciar partida", 
            font=FUENTES["extra"], command=self._reiniciar_partida, 
            bg="#f39c12", fg=COLORES["texto_boton"], width=20,
            relief="flat", cursor="hand2"
        )
        btn_reiniciar.pack(side="left", padx=10)

        btn_salir = tk.Button(
            frame_opciones_extra, text="⚙️ Cambiar Jugadores / Salir", 
            font=FUENTES["extra"], command=self._volver_al_menu, 
            bg="#7f8c8d", fg=COLORES["texto_boton"], width=25,
            relief="flat", cursor="hand2"
        )
        btn_salir.pack(side="right", padx=10)

    def _deshabilitar_botones_accion(self):
        """Deshabilita los botones durante transiciones o derrotas"""
        self.btn_robar.config(state="disabled", bg=COLORES["boton_deshabilitado"])
        self.btn_robar_otro.config(state="disabled", bg=COLORES["boton_deshabilitado"])
        self.btn_detener.config(state="disabled", bg=COLORES["boton_deshabilitado"])

    def _habilitar_botones_accion(self):
        """Habilita los botones de acción para el nuevo turno"""
        self.btn_robar.config(state="normal", bg=COLORES["boton_robar"])
        self.btn_robar_otro.config(state="normal", bg=COLORES["boton_robar_rival"])

    def jugador_actual(self):
        return self.jugadores[self.turno_actual]

    def _otros_jugadores(self):
        return [j for i, j in enumerate(self.jugadores) if i != self.turno_actual]

    def _iniciar_turno(self):
        jugador = self.jugador_actual()
        aspiradas = jugador.aspirar()
        self.ultima_carta_robada = None
        
        self._habilitar_botones_accion()

        self.label_imagen.config(image="", text="")
        if aspiradas > 0:
            self.label_mensaje.config(
                text=f"🌀 ¡{jugador.nombre} ha ASPIRADO {aspiradas} pelusa(s)! (Suma actual: {jugador.puntos_totales} pts)"
            )
        else:
            self.label_mensaje.config(text="")
            
        self._actualizar_interfaz()

    def _actualizar_interfaz(self):
        jugador = self.jugador_actual()
        self.label_turno.config(text=f"Turno de: {jugador.nombre}")

        partes_puntajes = []
        for j in self.jugadores:
            nombre_fmt = f"{j.nombre[:12]:<12}"
            pts_fmt = f"{j.puntos_totales:>3} pts"
            cartas_fmt = f"({len(j.banco)} c)"
            partes_puntajes.append(f"{nombre_fmt}: {pts_fmt} {cartas_fmt}")
        
        self.label_puntajes.config(text="  |  ".join(partes_puntajes))

        numeros_turno = [str(c.numero) for c in jugador.zona_activa]
        suma_actual_turno = sum(c.numero for c in jugador.zona_activa)
        
        texto_turno = " - ".join(numeros_turno) if numeros_turno else "(vacía)"
        cant_cartas = len(jugador.zona_activa)
        
        self.label_cartas_turno.config(
            text=f"{texto_turno}   [{cant_cartas} cartas | Suma: {suma_actual_turno} pts]"
        )

        partes = []
        for j in self._otros_jugadores():
            nums = ", ".join(str(c.numero) for c in j.zona_activa) or "(nada)"
            partes.append(f"{j.nombre}: {nums}")
        self.label_otros.config(text="Otros jugadores en riesgo -> " + "   |   ".join(partes))

        self.label_mazo.config(text=f"Pelusas restantes en el mazo: {len(self.mazo.cartas)}")

        if self.btn_robar['state'] != "disabled":
            if cant_cartas >= 3:
                self.btn_detener.config(state="normal", bg=COLORES["boton_detener"])
            else:
                self.btn_detener.config(state="disabled", bg=COLORES["boton_deshabilitado"])

    def _mostrar_carta(self, carta):
        """Muestra la imagen grande o el número si Pillow/imagen no está disponible."""
        ruta = os.path.join(CARPETA_IMAGENES, carta.imagen_archivo)

        if ruta in self.imagenes_cache:
            self.label_imagen.config(image=self.imagenes_cache[ruta], text="")
            return

        if PIL_DISPONIBLE and os.path.exists(ruta):
            try:
                img_pil = Image.open(ruta).resize(TAMANO_IMAGEN)
                img_tk = ImageTk.PhotoImage(img_pil)
                self.imagenes_cache[ruta] = img_tk
                self.label_imagen.config(image=img_tk, text="")
                return
            except Exception:
                pass

        self.label_imagen.config(
            image="", text=str(carta.numero), font=("Segoe UI", 120, "bold"), fg=COLORES["texto_principal"]
        )

    def robar_carta(self):
        if not self.mazo.quedan_cartas():
            self._terminar_juego()
            return

        jugador = self.jugador_actual()
        carta = self.mazo.robar()
        self.ultima_carta_robada = carta
        self._mostrar_carta(carta)

        repetido = jugador.tiene_numero(carta.numero)
        
        # BUST: Pierde a partir de la 4ª carta (teniendo ya 3 acumuladas)
        if repetido and len(jugador.zona_activa) >= 3:
            self._deshabilitar_botones_accion()

            self.label_mensaje.config(
                text=f"💥 ¡OH NO! {jugador.nombre} repitió el {carta.numero} a partir de su 4ª carta. "
                     f"¡Pierde sus pelusas de este turno!"
            )
            jugador.zona_activa = []
            self._actualizar_interfaz()
            self.root.after(2000, self._pasar_turno)
        else:
            jugador.zona_activa.append(carta)
            if repetido:
                self.label_mensaje.config(
                    text=f"Salió un {carta.numero} repetido, pero estás dentro de tus primeras 3 cartas seguras."
                )
            else:
                self.label_mensaje.config(text=f"Has robado una pelusa de valor {carta.numero}.")
            self._actualizar_interfaz()

        if not self.mazo.quedan_cartas():
            self.root.after(1700, self._terminar_juego)

    def ejecutar_robo_rivales(self):
        """Roba TODAS las cartas de ese número de TODOS los rivales a la vez"""
        if not self.ultima_carta_robada:
            messagebox.showinfo(
                "Robar a rivales",
                "Debes robar primero una carta del mazo en este turno."
            )
            return

        jugador = self.jugador_actual()
        num_objetivo = self.ultima_carta_robada.numero
        
        cartas_robadas_totales = []
        nombres_afectados = []

        for rival in self._otros_jugadores():
            coincidencias = [c for c in rival.zona_activa if c.numero == num_objetivo]
            if coincidencias:
                rival.zona_activa = [c for c in rival.zona_activa if c.numero != num_objetivo]
                cartas_robadas_totales.extend(coincidencias)
                nombres_afectados.append(f"{rival.nombre} ({len(coincidencias)})")

        if not cartas_robadas_totales:
            messagebox.showinfo(
                "Robar a rivales",
                f"Ningún rival tiene pelusas de valor {num_objetivo}."
            )
            return

        jugador.zona_activa.extend(cartas_robadas_totales)
        self.ultima_carta_robada = None 

        texto_afectados = ", ".join(nombres_afectados)
        cant_total = len(cartas_robadas_totales)
        self.label_mensaje.config(
            text=f"🥷 ¡Robaste un total de {cant_total} pelusa(s) del {num_objetivo} a: {texto_afectados}!"
        )
        self._actualizar_interfaz()

    def detener_turno(self):
        jugador = self.jugador_actual()
        if len(jugador.zona_activa) < 3:
            messagebox.showwarning("Aviso", "Necesitas al menos 3 cartas en tu zona activa para poder plantarte.")
            return

        self._deshabilitar_botones_accion()
        suma = sum(c.numero for c in jugador.zona_activa)
        self.label_mensaje.config(
            text=f"🛑 {jugador.nombre} se planta con {len(jugador.zona_activa)} pelusas (Suma: {suma} pts)."
        )
        self._actualizar_interfaz()
        self.root.after(1500, self._pasar_turno)

    def _pasar_turno(self):
        if not self.mazo.quedan_cartas():
            self._terminar_juego()
            return
        self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
        self._iniciar_turno()

    def _terminar_juego(self):
        for j in self.jugadores:
            j.aspirar()

        jugadores_ordenados = sorted(self.jugadores, key=lambda j: j.puntos_totales, reverse=True)
        ganador = jugadores_ordenados[0]

        mensaje = "🎉 ¡FIN DE LA PARTIDA! 🎉\n\nResultados finales:\n"
        for rank, j in enumerate(jugadores_ordenados, start=1):
            mensaje += f"{rank}º {j.nombre}: {j.puntos_totales} puntos ({len(j.banco)} cartas)\n"
            
        mensaje += f"\n🏆 ¡El ganador es {ganador.nombre}! 🏆"
        messagebox.showinfo("Fin de la partida", mensaje)
        self._deshabilitar_botones_accion()


# ============================================================
#                       INICIO DE LA APLICACIÓN
# ============================================================
# Configura la ventana raíz principal de Tkinter y arranca el bucle de eventos para iniciar el programa.

if __name__ == "__main__":
    root = tk.Tk()
    juego = JuegoPelusas(root)
    root.mainloop()