"""
¡Pelusas! - Juego de cartas de mesa (v13)
----------------------------------------
Novedad:
1. Deshabilitación de todos los botones de acción en el momento exacto en que 
   un jugador pierde por repetir número a partir de la 4ª carta.
2. Rehabilitación automática de los botones al cambiar de turno.
"""

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

CARPETA_IMAGENES = "cartas"
PATRON_NOMBRE_IMAGEN = "Pelusa_{numero}.jpg"
NUMEROS = list(range(1, 11))
TAMANO_IMAGEN = (160, 230)


# ============================================================
#                       LÓGICA DEL JUEGO
# ============================================================

class Carta:
    def __init__(self, numero):
        self.numero = numero
        self.imagen_archivo = PATRON_NOMBRE_IMAGEN.format(numero=numero)


class Jugador:
    def __init__(self, nombre):
        self.nombre = nombre
        self.banco = []        # Cartas aspiradas (puntos seguros)
        self.zona_activa = []  # Cartas acumuladas este turno (en riesgo)

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

class JuegoPelusas:
    def __init__(self, root):
        self.root = root
        self.root.title("¡Pelusas! - Juego de Cartas")
        self.root.geometry("820x680")
        self.root.configure(bg="#f0e6d2")
        self.root.resizable(False, False)

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

        self.frame_menu = tk.Frame(self.root, bg="#f0e6d2")
        self.frame_menu.pack(expand=True)

        tk.Label(
            self.frame_menu, text="¡PELUSAS!", font=("Arial", 30, "bold"),
            bg="#f0e6d2", fg="#2c3e50"
        ).pack(pady=20)

        tk.Label(
            self.frame_menu, text="Selecciona la cantidad de jugadores:",
            font=("Arial", 14), bg="#f0e6d2"
        ).pack(pady=10)

        frame_botones_num = tk.Frame(self.frame_menu, bg="#f0e6d2")
        frame_botones_num.pack(pady=15)

        for n in range(2, 6):
            cartas_txt = "50 cartas" if n <= 3 else "100 cartas"
            btn = tk.Button(
                frame_botones_num, 
                text=f"{n} Jugadores\n({cartas_txt})", 
                font=("Arial", 11, "bold"),
                bg="#4caf50", fg="white", width=14, height=2,
                command=lambda num=n: self._pedir_nombres_jugadores(num)
            )
            btn.pack(side="left", padx=8)

    def _pedir_nombres_jugadores(self, cantidad_jugadores):
        """Pantalla para escribir los nombres de cada uno de los jugadores"""
        self._limpiar_pantalla()
        self.cantidad_jugadores_actual = cantidad_jugadores

        self.frame_menu = tk.Frame(self.root, bg="#f0e6d2")
        self.frame_menu.pack(expand=True)

        tk.Label(
            self.frame_menu, text="Introduce los nombres de los jugadores:",
            font=("Arial", 18, "bold"), bg="#f0e6d2", fg="#2c3e50"
        ).pack(pady=20)

        self.entries_nombres = []
        frame_entradas = tk.Frame(self.frame_menu, bg="#f0e6d2")
        frame_entradas.pack(pady=10)

        for i in range(cantidad_jugadores):
            row_frame = tk.Frame(frame_entradas, bg="#f0e6d2")
            row_frame.pack(pady=6)

            lbl = tk.Label(
                row_frame, text=f"Jugador {i+1}:", font=("Arial", 11, "bold"),
                bg="#f0e6d2", width=10, anchor="e"
            )
            lbl.pack(side="left", padx=5)

            entry = tk.Entry(row_frame, font=("Arial", 11), width=22)
            entry.insert(0, f"Jugador {i+1}")
            entry.pack(side="left", padx=5)
            self.entries_nombres.append(entry)

        btn_comenzar = tk.Button(
            self.frame_menu, text="¡Empezar Partida!", font=("Arial", 12, "bold"),
            bg="#2196f3", fg="white", width=20, height=2,
            command=self._procesar_nombres_y_empezar
        )
        btn_comenzar.pack(pady=25)

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
        self.frame_juego = tk.Frame(self.root, bg="#f0e6d2")
        self.frame_juego.pack(fill="both", expand=True)

        self.label_turno = tk.Label(
            self.frame_juego, text="", font=("Arial", 18, "bold"), bg="#f0e6d2"
        )
        self.label_turno.pack(pady=6)

        self.label_puntajes = tk.Label(
            self.frame_juego, text="", font=("Arial", 10, "bold"), bg="#f0e6d2", fg="#2c3e50"
        )
        self.label_puntajes.pack(pady=4)

        self.frame_carta = tk.Frame(self.frame_juego, bg="#ffffff", width=180, height=230,
                                     relief="ridge", bd=2)
        self.frame_carta.pack(pady=8)
        self.frame_carta.pack_propagate(False)

        self.label_imagen = tk.Label(self.frame_carta, bg="#ffffff")
        self.label_imagen.pack(expand=True)

        self.label_cartas_turno = tk.Label(
            self.frame_juego, text="", font=("Arial", 11), bg="#f0e6d2", wraplength=760
        )
        self.label_cartas_turno.pack(pady=6)

        self.label_otros = tk.Label(
            self.frame_juego, text="", font=("Arial", 9), bg="#f0e6d2", fg="#555", wraplength=780
        )
        self.label_otros.pack(pady=4)

        # Botones principales
        frame_botones = tk.Frame(self.frame_juego, bg="#f0e6d2")
        frame_botones.pack(pady=10)

        self.btn_robar = tk.Button(
            frame_botones, text="Robar del mazo", font=("Arial", 11, "bold"),
            command=self.robar_carta, bg="#4caf50", fg="white", width=16
        )
        self.btn_robar.grid(row=0, column=0, padx=5)

        self.btn_robar_otro = tk.Button(
            frame_botones, text="Robar a rivales", font=("Arial", 11, "bold"),
            command=self.ejecutar_robo_rivales, bg="#2196f3", fg="white", width=16
        )
        self.btn_robar_otro.grid(row=0, column=1, padx=5)

        self.btn_detener = tk.Button(
            frame_botones, text="Detener turno", font=("Arial", 11, "bold"),
            command=self.detener_turno, bg="#f44336", fg="white", width=16
        )
        self.btn_detener.grid(row=0, column=2, padx=5)

        self.label_mensaje = tk.Label(
            self.frame_juego, text="", font=("Arial", 11, "italic"), bg="#f0e6d2", fg="#333"
        )
        self.label_mensaje.pack(pady=6)

        self.label_mazo = tk.Label(
            self.frame_juego, text="", font=("Arial", 10), bg="#f0e6d2", fg="#777"
        )
        self.label_mazo.pack(pady=2)

        # Barra inferior de opciones extra
        frame_opciones_extra = tk.Frame(self.frame_juego, bg="#f0e6d2")
        frame_opciones_extra.pack(pady=10)

        btn_reiniciar = tk.Button(
            frame_opciones_extra, text="🔄 Reiniciar partida", font=("Arial", 9, "bold"),
            command=self._reiniciar_partida, bg="#ff9800", fg="white", width=18
        )
        btn_reiniciar.grid(row=0, column=0, padx=10)

        btn_salir = tk.Button(
            frame_opciones_extra, text="⚙️ Cambiar Jugadores / Salir", font=("Arial", 9, "bold"),
            command=self._volver_al_menu, bg="#607d8b", fg="white", width=22
        )
        btn_salir.grid(row=0, column=1, padx=10)

    def _deshabilitar_botones_accion(self):
        """Deshabilita los botones durante transiciones o derrotas"""
        self.btn_robar.config(state="disabled", bg="#cccccc")
        self.btn_robar_otro.config(state="disabled", bg="#cccccc")
        self.btn_detener.config(state="disabled", bg="#cccccc")

    def _habilitar_botones_accion(self):
        """Habilita los botones de acción para el nuevo turno"""
        self.btn_robar.config(state="normal", bg="#4caf50")
        self.btn_robar_otro.config(state="normal", bg="#2196f3")
        # El botón detener se maneja individualmente en _actualizar_interfaz (mínimo 3 cartas)

    def jugador_actual(self):
        return self.jugadores[self.turno_actual]

    def _otros_jugadores(self):
        return [j for i, j in enumerate(self.jugadores) if i != self.turno_actual]

    def _iniciar_turno(self):
        jugador = self.jugador_actual()
        aspiradas = jugador.aspirar()
        self.ultima_carta_robada = None
        
        # Volver a habilitar los botones para el jugador que inicia turno
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

        puntajes = "   |   ".join(
            f"{j.nombre}: {j.puntos_totales} pts ({len(j.banco)} c)" for j in self.jugadores
        )
        self.label_puntajes.config(text=puntajes)

        numeros_turno = [str(c.numero) for c in jugador.zona_activa]
        suma_actual_turno = sum(c.numero for c in jugador.zona_activa)
        texto_turno = ", ".join(numeros_turno) if numeros_turno else "(ninguna)"
        
        cant_cartas = len(jugador.zona_activa)
        self.label_cartas_turno.config(
            text=f"Zona activa (en riesgo): {texto_turno}   "
                 f"[{cant_cartas} cartas | Suma actual: {suma_actual_turno} pts]"
        )

        partes = []
        for j in self._otros_jugadores():
            nums = ", ".join(str(c.numero) for c in j.zona_activa) or "(nada)"
            partes.append(f"{j.nombre}: {nums}")
        self.label_otros.config(text="Otros jugadores -> " + "   |   ".join(partes))

        self.label_mazo.config(text=f"Pelusas restantes en el mazo: {len(self.mazo.cartas)}")

        # Mínimo de 3 cartas para poder plantarse (solo si los botones están activos)
        if self.btn_robar['state'] != "disabled":
            if cant_cartas >= 3:
                self.btn_detener.config(state="normal", bg="#f44336")
            else:
                self.btn_detener.config(state="disabled", bg="#cccccc")

    def _mostrar_carta(self, carta):
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
            image="", text=str(carta.numero), font=("Arial", 60, "bold"), fg="#333"
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
            # DESHABILITAR BOTONES INMEDIATAMENTE AL PERDER
            self._deshabilitar_botones_accion()

            self.label_mensaje.config(
                text=f"💥 ¡OH NO! {jugador.nombre} repitió el {carta.numero} a partir de su 4ª carta. "
                     f"¡Pierde sus pelusas de este turno!"
            )
            jugador.zona_activa = []
            self._actualizar_interfaz()
            # Esperar 2 segundos antes de reactivar botones con el siguiente jugador
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


if __name__ == "__main__":
    root = tk.Tk()
    juego = JuegoPelusas(root)
    root.mainloop()