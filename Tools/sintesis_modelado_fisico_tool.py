from dearpygui.dearpygui import output_frame_buffer

from Tool import *
from Instrument import *
import numpy as np
from scipy.io.wavfile import write
import scipy.signal

class InstrumentoKPstrong(Instrument):
    def __init__(self):
        self.RL = None
        self.sustain = None
        self.decay = None
        self.release = None


    def Play(self, frequency: float):

        return 0 #karplus_strong()

class KPStrongTool(Tool):
    def __init__(self, editor, uuid, signal=None, tab: bool = True):
        Tool.__init__(self, name="KPstrongTool", editor=editor, uuid=uuid)
        self.noise = "blanco"
        self.filterFunction = self.filter_avg
        self.pitch = 200
        self.L = 1024
        self.fs = 44100
        self.duration = 1.0
        self.contador_sonido = 0
        self.blendFactor = 1
        self.R = 1
        if tab:
            self.Init(self.Run)



    def Run(self):

        img.add_text("Seleccionar tipo de ruido:")

        # Opciones para el combo
        opciones_ruido = ["blanco", "uniforme", "opcion 2", "opcion 3"]

        # Callback para actualizar la variable `ruido`
        def seleccionar_ruido(sender, app_data, user_data):
            global noise
            noise = app_data
            print(f"Tipo de ruido seleccionado: {noise}")

        # Combo box para seleccionar el tipo de ruido
        self.ruido_combo_tag = img.add_combo(
            items=opciones_ruido,
            default_value="blanco",
            label="Tipo de Ruido",
            callback=seleccionar_ruido
        )

        img.add_text("Seleccione el Pitch:")
        img.add_slider_float(label="", default_value=self.pitch, min_value=0.0, max_value=2000.0,
                             callback=self.update_var,
                             user_data="pitch")

        img.add_text("Seleccione el Blend Factor")
        img.add_slider_float(label="", default_value=self.blendFactor, min_value=0, max_value=1.0,
                             callback=self.update_var,
                             user_data="blendFactor")

        img.add_text("Seleccione la ganancia R")
        img.add_slider_int(label="", default_value=self.R, min_value=0, max_value=10000, callback=self.update_var, user_data="R")

        img.add_text("Seleccione la Frecuencia de Muestreo")
        img.add_slider_int(label="", default_value=self.fs, min_value=1000, max_value=96000, callback=self.update_var,
                           user_data="fs")

        img.add_text("Seleccione la Duración")
        img.add_slider_float(label="", default_value=self.duration, min_value=0.1, max_value=10.0, callback=self.update_var,
                             user_data="duration")

        img.add_button(label="Generar Sonido", callback=self.generarsonido)

    def update_var(self, sender, app_data, user_data):
        setattr(self, user_data, app_data)


    def guardar_wav(self,filename, señal, fs=44100):
        señal_int16 = np.int16(señal / np.max(np.abs(señal)) * 32767)
        write(filename, fs, señal_int16)

    def generarsonido(self):
        print("Generando sonido...")

        print(self.blendFactor)

        N = int(self.duration * self.fs)  # numero total de muestras

        print(self.noise)

        # Generador de ruido según el tipo
        if self.noise == "blanco":
            waveTable = 2 * np.random.rand(int(self.pitch)) - 1  # Uniforme [-1, 1]

        else:
            raise ValueError("Tipo de ruido no soportado. Usar 'blanco' o 'gaussiano'.")

        output = np.zeros(N)  # Output es N ceros

        for i in range(N):
            y = waveTable[0]
            output[i] = y
            avg = 0.5 * (waveTable[0] + waveTable[1])  # Aplicamos el filtro definido
            next_sample = self.R * avg
            waveTable = np.append(waveTable[1:], next_sample)


        print(f"Los valores son Pitch = {self.pitch}, R = {self.R}, b = {self.blendFactor}, fs = {self.fs}, duration = {self.duration}")

        #código para guardar en wav
        ruta_base = r"D:\Escritorio\sonido"
        ruta = f"{ruta_base}{self.contador_sonido}.wav"
        self.guardar_wav(ruta, output)
        print(f"Guardado en: {ruta}")
        self.contador_sonido += 1

    # ruidos
    def ruido_blanco(self, pitch):
        return 2 * np.random.rand(pitch) - 1  # Uniforme entre -1 y 1

    def ruido_filtrado(self, l):
        base = 2 * np.random.rand(l) - 1
        return np.convolve(base, [0.5, 0.5], mode='same')

    # filtros
    def filter_avg(self, buffer):
        return 0.5 * (buffer[0] + buffer[1])

    def filtro_media_3(self, buffer):
        return (buffer[0] + buffer[1] + buffer[2]) / 3

    def filtro_iir(self, buffer, prev=[0]):
        # Pasa bajos IIR simple (requiere estado previo)
        alpha = 0.9
        y = alpha * prev[0] + (1 - alpha) * buffer[0]
        prev[0] = y
        return y