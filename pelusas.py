"""
¡Pelusas! - Juego de cartas (v2)
--------------------------------
Juego para 3 jugadores en la misma computadora (hot-seat).

Reglas implementadas:
- El mazo tiene cartas numeradas del 1 al 10, con varias copias de cada número.
- En su turno, el jugador roba cartas una por una.
- Las primeras 3 cartas que roba en un turno son SIEMPRE seguras, aunque
  se repita el número. A partir de la 4ta carta robada en ese turno, si
  sale un número que ya tenía acumulado, pierde TODAS las cartas de ese turno.
- Si el jugador decide "Detener turno" antes de perder, suma los puntos
  (la suma de los números de las cartas que acumuló) a su puntaje total.
- Robo: en su turno, un jugador puede robar una carta de la pila (de este
  turno) de otro jugador, siempre que el número coincida con una carta
  que él ya tiene acumulada en su propio turno. Esa carta pasa a su pila
  y desaparece de la pila del otro jugador.
- El juego termina cuando se acaba el mazo. Gana quien tenga más puntos.

Cómo instalar lo necesario, ver el archivo LEEME.txt que va junto a este script.
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
COPIAS_POR_NUMERO = 4

TAMANO_IMAGEN = (160, 230)

CARTAS_SEGURAS_POR_TURNO = 3

NOMBRES_JUGADORES = ["Jugador 1", "Jugador 2", "Jugador 3"]


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
        self.cartas_turno = []
        self.cartas_robadas_turno = 0
        self.detenido = False  # True si ya jugó su turno esta ronda y se detuvo (cartas en la mesa)

    def reiniciar_turno(self):
        self.cartas_turno = []
        self.cartas_robadas_turno = 0
        self.detenido = False

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
        self.root.geometry("760x620")
        self.root.configure(bg="#f0e6d2")
        self.root.resizable(False, False)

        self.mazo = Mazo()
        self.jugadores = [Jugador(nombre) for nombre in NOMBRES_JUGADORES]
        self.turno_actual = 0
        self.imagenes_cache = {}

        self._crear_interfaz()
        self._actualizar_interfaz()

        if not PIL_DISPONIBLE:
            self.label_mensaje.config(
                text="(Pillow no está instalado: se mostrarán números en vez de imágenes. "
                     "Revisa LEEME.txt)"
            )

    def _crear_interfaz(self):
        self.label_turno = tk.Label(
            self.root, text="", font=("Arial", 18, "bold"), bg="#f0e6d2"
        )
        self.label_turno.pack(pady=8)

        self.label_puntajes = tk.Label(
            self.root, text="", font=("Arial", 12), bg="#f0e6d2"
        )
        self.label_puntajes.pack(pady=5)

        self.frame_carta = tk.Frame(self.root, bg="#ffffff", width=200, height=260,
                                     relief="ridge", bd=2)
        self.frame_carta.pack(pady=10)
        self.frame_carta.pack_propagate(False)

        self.label_imagen = tk.Label(self.frame_carta, bg="#ffffff")
        self.label_imagen.pack(expand=True)

        self.label_cartas_turno = tk.Label(
            self.root, text="", font=("Arial", 11), bg="#f0e6d2", wraplength=680
        )
        self.label_cartas_turno.pack(pady=8)

        self.label_otros = tk.Label(
            self.root, text="", font=("Arial", 10), bg="#f0e6d2", fg="#555", wraplength=680
        )
        self.label_otros.pack(pady=4)

        frame_botones = tk.Frame(self.root, bg="#f0e6d2")
        frame_botones.pack(pady=15)

        self.btn_robar = tk.Button(
            frame_botones, text="Robar carta del mazo", font=("Arial", 12),
            command=self.robar_carta, bg="#4caf50", fg="white", width=18
        )
        self.btn_robar.grid(row=0, column=0, padx=8)

        self.btn_robar_otro = tk.Button(
            frame_botones, text="Robar a otro jugador", font=("Arial", 12),
            command=self.abrir_dialogo_robo, bg="#2196f3", fg="white", width=18
        )
        self.btn_robar_otro.grid(row=0, column=1, padx=8)

        self.btn_detener = tk.Button(
            frame_botones, text="Detener turno", font=("Arial", 12),
            command=self.detener_turno, bg="#f44336", fg="white", width=18
        )
        self.btn_detener.grid(row=0, column=2, padx=8)

        self.label_mensaje = tk.Label(
            self.root, text="", font=("Arial", 12, "italic"), bg="#f0e6d2", fg="#555"
        )
        self.label_mensaje.pack(pady=10)

        self.label_mazo = tk.Label(
            self.root, text="", font=("Arial", 10), bg="#f0e6d2", fg="#777"
        )
        self.label_mazo.pack(pady=5)

    def jugador_actual(self):
        return self.jugadores[self.turno_actual]

    def _otros_jugadores(self):
        return [j for i, j in enumerate(self.jugadores) if i != self.turno_actual]

    def _actualizar_interfaz(self):
        jugador = self.jugador_actual()
        self.label_turno.config(text=f"Turno de: {jugador.nombre}")

        partes_puntaje = []
        for j in self.jugadores:
            texto = f"{j.nombre}: {j.puntaje_total} pts"
            if j.detenido and j.cartas_turno:
                pendiente = sum(c.numero for c in j.cartas_turno)
                texto += f" (+{pendiente} en la mesa)"
            partes_puntaje.append(texto)
        self.label_puntajes.config(text="   |   ".join(partes_puntaje))

        numeros_turno = [str(c.numero) for c in jugador.cartas_turno]
        texto_turno = ", ".join(numeros_turno) if numeros_turno else "(ninguna todavía)"
        cartas_seguras_restantes = max(0, CARTAS_SEGURAS_POR_TURNO - jugador.cartas_robadas_turno)
        self.label_cartas_turno.config(
            text=f"Cartas acumuladas este turno: {texto_turno}   "
                 f"(cartas seguras que faltan: {cartas_seguras_restantes})"
        )

        partes = []
        for j in self._otros_jugadores():
            nums = ", ".join(str(c.numero) for c in j.cartas_turno) or "(nada)"
            etiqueta = " [detenido, en la mesa]" if j.detenido and j.cartas_turno else ""
            partes.append(f"{j.nombre}: {nums}{etiqueta}")
        self.label_otros.config(text="Otros jugadores tienen -> " + "   |   ".join(partes))

        self.label_mazo.config(text=f"Cartas restantes en el mazo: {len(self.mazo.cartas)}")

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
        jugador.cartas_robadas_turno += 1
        self._mostrar_carta(carta)

        es_carta_segura = jugador.cartas_robadas_turno <= CARTAS_SEGURAS_POR_TURNO
        repetido = jugador.tiene_numero(carta.numero)

        if repetido and not es_carta_segura:
            self.label_mensaje.config(
                text=f"¡Salió otro {carta.numero} después de tus cartas seguras! "
                     f"Pierdes las cartas de este turno."
            )
            jugador.reiniciar_turno()
            self._actualizar_interfaz()
            self.root.after(1600, self._pasar_turno)
        else:
            jugador.cartas_turno.append(carta)
            if repetido and es_carta_segura:
                self.label_mensaje.config(
                    text=f"Salió otro {carta.numero}, pero todavía estás en tus cartas seguras. ¡Tranquilo!"
                )
            else:
                self.label_mensaje.config(text="")
            self._actualizar_interfaz()

        if not self.mazo.quedan_cartas():
            self.root.after(1700, self._terminar_juego)

    def detener_turno(self):
        jugador = self.jugador_actual()
        jugador.detenido = True          # sus cartas quedan en la mesa, robables
        jugador.cartas_robadas_turno = 0  # listo para su próxima ronda
        puntos_en_mesa = sum(c.numero for c in jugador.cartas_turno)
        self.label_mensaje.config(
            text=f"{jugador.nombre} se detuvo con {puntos_en_mesa} puntos en la mesa "
                 f"(se cuentan hasta que termine la ronda)."
        )
        self._actualizar_interfaz()
        self.root.after(1200, self._pasar_turno)

    def _pasar_turno(self):
        if not self.mazo.quedan_cartas():
            self._terminar_juego()
            return
        self.turno_actual = (self.turno_actual + 1) % len(self.jugadores)
        self.label_imagen.config(image="", text="")

        if self.turno_actual == 0:
            self._finalizar_ronda()
        else:
            self.label_mensaje.config(text="")

        self._actualizar_interfaz()

    def _finalizar_ronda(self):
        """Se llama cuando el turno completa la vuelta y regresa al Jugador 1.
        Aquí SÍ se cuentan de verdad los puntos de quienes se detuvieron,
        y se limpia la mesa para la nueva ronda."""
        resumen = []
        for j in self.jugadores:
            if j.cartas_turno:
                puntos = sum(c.numero for c in j.cartas_turno)
                j.puntaje_total += puntos
                resumen.append(f"{j.nombre} +{puntos}")
            j.cartas_turno = []
            j.cartas_robadas_turno = 0
            j.detenido = False

        if resumen:
            self.label_mensaje.config(text="Fin de ronda -> " + ", ".join(resumen))
        else:
            self.label_mensaje.config(text="Fin de ronda (nadie tenía cartas en la mesa).")

    def _opciones_de_robo(self):
        jugador = self.jugador_actual()
        numeros_propios = set(c.numero for c in jugador.cartas_turno)
        opciones = []
        for objetivo in self._otros_jugadores():
            for carta in objetivo.cartas_turno:
                if carta.numero in numeros_propios:
                    opciones.append((objetivo, carta))
        return opciones

    def abrir_dialogo_robo(self):
        opciones = self._opciones_de_robo()
        if not opciones:
            messagebox.showinfo(
                "Robar carta",
                "No hay ninguna carta de otro jugador que coincida con las tuyas."
            )
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Elige a quién robarle")
        ventana.configure(bg="#f0e6d2")
        ventana.geometry("320x260")

        tk.Label(
            ventana, text="Puedes robar estas cartas:", font=("Arial", 12, "bold"), bg="#f0e6d2"
        ).pack(pady=10)

        for objetivo, carta in opciones:
            texto = f"{objetivo.nombre}  ->  carta {carta.numero}"
            tk.Button(
                ventana, text=texto, font=("Arial", 11), width=25,
                command=lambda o=objetivo, c=carta, v=ventana: self._robar_de_jugador(o, c, v)
            ).pack(pady=4)

    def _robar_de_jugador(self, objetivo, carta, ventana):
        jugador = self.jugador_actual()
        objetivo.cartas_turno.remove(carta)
        jugador.cartas_turno.append(carta)
        ventana.destroy()
        self.label_mensaje.config(
            text=f"¡Robaste la carta {carta.numero} de {objetivo.nombre}!"
        )
        self._mostrar_carta(carta)
        self._actualizar_interfaz()

    def _terminar_juego(self):
        ganador = max(self.jugadores, key=lambda j: j.puntaje_total)
        mensaje = "Fin del juego\n\n"
        for j in self.jugadores:
            mensaje += f"{j.nombre}: {j.puntaje_total} puntos\n"
        mensaje += f"\n¡Ganador: {ganador.nombre}!"
        messagebox.showinfo("Fin de la partida", mensaje)
        self.btn_robar.config(state="disabled")
        self.btn_robar_otro.config(state="disabled")
        self.btn_detener.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    juego = JuegoPelusas(root)
    root.mainloop()