"""
¡Pelusas! - Juego de cartas
---------------------------
Juego para 2 jugadores en la misma computadora (hot-seat).

Reglas implementadas:
- El mazo tiene cartas numeradas del 1 al 10, con varias copias de cada número.
- En su turno, el jugador roba cartas una por una.
- Si sale un número que ya tenía acumulado en ESE turno, pierde todas las
  cartas de ese turno y pasa el turno al siguiente jugador.
- Si el jugador decide "Detener turno" antes de eso, suma los puntos
  (la suma de los números de las cartas que acumuló) a su puntaje total.
- El juego termina cuando se acaba el mazo. Gana quien tenga más puntos.

Cómo instalar lo necesario, ver el archivo LEEME.txt que va junto a este script.
"""

import tkinter as tk
from tkinter import messagebox
import random
import os

# PIL (Pillow) permite mostrar imágenes .jpg/.png con buena calidad.
# Si no está instalado, el juego sigue funcionando pero muestra el
# número de la carta en texto grande en vez de la imagen.
try:
    from PIL import Image, ImageTk
    PIL_DISPONIBLE = True
except ImportError:
    PIL_DISPONIBLE = False


# ============================================================
#                       CONFIGURACIÓN
# ============================================================

# Carpeta (relativa a este script) donde van las imágenes de las cartas.
# Aquí es donde pones los nombres/archivos de las imágenes.
CARPETA_IMAGENES = "cartas"

# Patrón del nombre de archivo esperado para cada número de carta.
# Con este patrón, la carta número 3 debe llamarse "Pelusa_3.jpg"
PATRON_NOMBRE_IMAGEN = "Pelusa_{numero}.jpg"

NUMEROS = list(range(1, 11))     # cartas del 1 al 10
COPIAS_POR_NUMERO = 4            # cuántas copias de cada número hay en el mazo

TAMANO_IMAGEN = (160, 230)       # ancho x alto en píxeles al mostrar la carta


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
        self.puntaje_total = 0
        self.cartas_turno = []  # cartas acumuladas en el turno actual

    def reiniciar_turno(self):
        self.cartas_turno = []

    def tiene_numero(self, numero):
        return any(c.numero == numero for c in self.cartas_turno)


class Mazo:
    def __init__(self):
        self.cartas = []
        self.generar()

    def generar(self):
        self.cartas = []
        for numero in NUMEROS:
            for _ in range(COPIAS_POR_NUMERO):
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
        self.root.geometry("700x560")
        self.root.configure(bg="#f0e6d2")
        self.root.resizable(False, False)

        self.mazo = Mazo()
        self.jugadores = [Jugador("Jugador 1"), Jugador("Jugador 2")]
        self.turno_actual = 0
        self.imagenes_cache = {}  # evita recargar la misma imagen varias veces

        self._crear_interfaz()
        self._actualizar_interfaz()

        if not PIL_DISPONIBLE:
            self.label_mensaje.config(
                text="(Pillow no está instalado: se mostrarán números en vez de imágenes. "
                     "Revisa LEEME.txt)"
            )

    # ---------------- Construcción de la interfaz ----------------

    def _crear_interfaz(self):
        self.label_turno = tk.Label(
            self.root, text="", font=("Arial", 18, "bold"), bg="#f0e6d2"
        )
        self.label_turno.pack(pady=10)

        self.label_puntajes = tk.Label(
            self.root, text="", font=("Arial", 12), bg="#f0e6d2"
        )
        self.label_puntajes.pack(pady=5)

        self.frame_carta = tk.Frame(self.root, bg="#ffffff", width=200, height=260,
                                     relief="ridge", bd=2)
        self.frame_carta.pack(pady=15)
        self.frame_carta.pack_propagate(False)

        self.label_imagen = tk.Label(self.frame_carta, bg="#ffffff")
        self.label_imagen.pack(expand=True)

        self.label_cartas_turno = tk.Label(
            self.root, text="", font=("Arial", 11), bg="#f0e6d2", wraplength=600
        )
        self.label_cartas_turno.pack(pady=10)

        frame_botones = tk.Frame(self.root, bg="#f0e6d2")
        frame_botones.pack(pady=15)

        self.btn_robar = tk.Button(
            frame_botones, text="Robar carta", font=("Arial", 12),
            command=self.robar_carta, bg="#4caf50", fg="white", width=15
        )
        self.btn_robar.grid(row=0, column=0, padx=10)

        self.btn_detener = tk.Button(
            frame_botones, text="Detener turno", font=("Arial", 12),
            command=self.detener_turno, bg="#f44336", fg="white", width=15
        )
        self.btn_detener.grid(row=0, column=1, padx=10)

        self.label_mensaje = tk.Label(
            self.root, text="", font=("Arial", 12, "italic"), bg="#f0e6d2", fg="#555"
        )
        self.label_mensaje.pack(pady=10)

        self.label_mazo = tk.Label(
            self.root, text="", font=("Arial", 10), bg="#f0e6d2", fg="#777"
        )
        self.label_mazo.pack(pady=5)

    # ---------------- Utilidades ----------------

    def jugador_actual(self):
        return self.jugadores[self.turno_actual]

    def _actualizar_interfaz(self):
        jugador = self.jugador_actual()
        self.label_turno.config(text=f"Turno de: {jugador.nombre}")

        puntajes = "   |   ".join(
            f"{j.nombre}: {j.puntaje_total} pts" for j in self.jugadores
        )
        self.label_puntajes.config(text=puntajes)

        numeros_turno = [str(c.numero) for c in jugador.cartas_turno]
        texto_turno = ", ".join(numeros_turno) if numeros_turno else "(ninguna todavía)"
        self.label_cartas_turno.config(text=f"Cartas acumuladas este turno: {texto_turno}")

        self.label_mazo.config(text=f"Cartas restantes en el mazo: {len(self.mazo.cartas)}")

    def _mostrar_carta(self, carta):
        """Muestra la imagen de la carta si existe; si no, muestra el número en grande."""
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
                pass  # si la imagen está corrupta o el formato falla, usamos el texto

        # Si no hay Pillow, o el archivo no existe, mostramos el número como respaldo
        self.label_imagen.config(
            image="", text=str(carta.numero), font=("Arial", 60, "bold"), fg="#333"
        )

    # ---------------- Acciones del juego ----------------

    def robar_carta(self):
        if not self.mazo.quedan_cartas():
            self._terminar_juego()
            return

        jugador = self.jugador_actual()
        carta = self.mazo.robar()
        self._mostrar_carta(carta)

        if jugador.tiene_numero(carta.numero):
            self.label_mensaje.config(
                text=f"¡Salió otro {carta.numero}! Pierdes las cartas de este turno."
            )
            jugador.reiniciar_turno()
            self._actualizar_interfaz()
            self.root.after(1500, self._pasar_turno)
        else:
            jugador.cartas_turno.append(carta)
            self.label_mensaje.config(text="")
            self._actualizar_interfaz()

        if not self.mazo.quedan_cartas():
            self.root.after(1600, self._terminar_juego)

    def detener_turno(self):
        jugador = self.jugador_actual()
        puntos_ganados = sum(c.numero for c in jugador.cartas_turno)
        jugador.puntaje_total += puntos_ganados
        jugador.reiniciar_turno()
        self.label_mensaje.config(text=f"Te detuviste y sumaste {puntos_ganados} puntos.")
        self._actualizar_interfaz()
        self.root.after(1200, self._pasar_turno)

    def _pasar_turno(self):
        if not self.mazo.quedan_cartas():
            self._terminar_juego()
            return
        self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
        self.label_imagen.config(image="", text="")
        self.label_mensaje.config(text="")
        self._actualizar_interfaz()

    def _terminar_juego(self):
        ganador = max(self.jugadores, key=lambda j: j.puntaje_total)
        mensaje = "Fin del juego\n\n"
        for j in self.jugadores:
            mensaje += f"{j.nombre}: {j.puntaje_total} puntos\n"
        mensaje += f"\n¡Ganador: {ganador.nombre}!"
        messagebox.showinfo("Fin de la partida", mensaje)
        self.btn_robar.config(state="disabled")
        self.btn_detener.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    juego = JuegoPelusas(root)
    root.mainloop()
