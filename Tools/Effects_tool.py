from Tool import *
from Instrument import *
from Signal import Signal, MathExpr
import dearpygui.dearpygui as img
import numpy as np


class Effect:
    def __init__(self, name, processor=None):
        self.name = name

        self.alpha = processor.alpha
        self.D = processor.D
        self.K = processor.K

    def applyEffect(self, x):
        return self.processor.applyEffect(x)


class EcoSimple(Effect):
    def __init__(self, alpha=0.5, D=1000, K=1):
        self.alpha = [alpha]
        self.D = [D]
        self.K = 1

    def applyEffect(self, signal, fs):
        y = signal.GetYData()
        y_out = np.copy(y)
        x = signal.GetXData()

        # Calcular D_k en muestras (D_k_segundos * fs)
        Ds_muestras = [int(d * fs) for d in self.D]

        D_muestras = Ds_muestras[0]
        alpha = self.alpha[0]

        if D_muestras < len(y):
            y_out[D_muestras:] += alpha * y[:-D_muestras]

        return y_out


class ReverberadorPlano(Effect):
    def __init__(self, K=5,
                 alpha=[0.5 / k for k in range(1, 5 + 1)],
                 D=[1000 * k for k in range(1, 5 + 1)]
                 ):
        self.alpha = alpha
        self.D = D
        self.K = K

    def applyEffect(self, signal, fs):
        y = signal.GetYData()
        y_out = np.copy(y)
        x = signal.GetXData()

        # Convertir D de segundos a muestras
        Ds_muestras = [int(d * fs) for d in self.D]

        # Aplicar cada retardo
        for alpha_k, D_k in zip(self.alpha, Ds_muestras):
            if D_k < len(y):
                y_out[D_k:] += alpha_k * y[:-D_k]

        return y_out


EFFECTS_PRESETS = [
    Effect("Eco Simple", EcoSimple()),
    Effect("Reverberador Plano", ReverberadorPlano())
]


class EffectsTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="Effects Tool", editor=editor, uuid=uuid)
        self.signal = signal
        self.fs_value = 44100
        self.effectChosen = None
        self.selected_parameters = {"alpha": [0.5], "D": [1000], "K": 1}
        self.Init(self.Run)

    def Run(self):

        # IDs para widgets dinámicos
        self.K_SLIDER_ID = "K_slider"
        self.ALPHA_CONTAINER_ID = "alpha_container"
        self.D_CONTAINER_ID = "D_container"
        self.FS_SLIDER_ID = "fs_slider"

        # Interfaz principal
        img.add_slider_int(
            label="fs (Frecuencia de muestreo)",
            tag=self.FS_SLIDER_ID,
            min_value=1, max_value=100000,
            default_value=self.fs_value,
            callback=self.on_fs_changed
        )
        img.add_slider_int(
            label="K (cantidad de ecos)",
            tag=self.K_SLIDER_ID,
            min_value=1, max_value=10,
            default_value=1,
            callback=self.on_k_changed
        )

        img.add_group(tag=self.ALPHA_CONTAINER_ID, label="Alphas")
        img.add_group(tag=self.D_CONTAINER_ID, label="D's")

        # Inicializar sliders
        # self.on_k_changed(None, None, None)

        img.add_text("Efectos:")
        with img.group(horizontal=True):
            for preset in EFFECTS_PRESETS:
                def make_callback(preset):
                    return lambda sender, app_data: self.set_preset(preset)

                img.add_button(label=preset.name, callback=make_callback(preset))

        img.add_button(label="Copiar efecto", callback=self.choose_effect)
        img.add_button(label="Calcular efecto", callback=self.calculate_effect)

        self.update_plot()

    def on_fs_changed(self, sender, app_data, user_data):
        self.fs_value = img.get_value(self.FS_SLIDER_ID)

    def on_k_changed(self, sender, app_data, user_data):
        k_value = img.get_value(self.K_SLIDER_ID)

        # Eliminar sliders antiguos
        img.delete_item(self.ALPHA_CONTAINER_ID, children_only=True)
        img.delete_item(self.D_CONTAINER_ID, children_only=True)

        # Crear nuevos sliders según K
        for i in range(1, k_value + 1):
            if i < len(self.selected_parameters.get("alpha", [])):
                d = self.selected_parameters["D"][i - 1]
                a = self.selected_parameters["alpha"][i - 1]
            else:
                d = 1000
                a = 0.5

            img.add_slider_float(
                label=f"Alpha {i}",
                tag=f"alpha_{i}",
                default_value=a,
                min_value=0.0, max_value=1.0,
                parent=self.ALPHA_CONTAINER_ID,
                callback=lambda s, a, u: self.update_parameters()
            )
            img.add_slider_int(
                label=f"D {i}",
                tag=f"D_{i}",
                default_value=d,
                min_value=0, max_value=10000,
                parent=self.D_CONTAINER_ID,
                callback=lambda s, a, u: self.update_parameters()
            )
        # Actualizar los parámetros seleccionados
        self.update_parameters()

    def set_preset(self, preset):
        self.selected_parameters = {"alpha": preset.alpha, "D": preset.D, "K": preset.K}
        img.set_value(self.K_SLIDER_ID, preset.K)

        self.update_plot()  # Actualizar la interfaz con los nuevos sliders

    def update_plot(self):
        img.delete_item(self.ALPHA_CONTAINER_ID, children_only=True)
        img.delete_item(self.D_CONTAINER_ID, children_only=True)

        k = self.selected_parameters["K"]
        d = self.selected_parameters["D"]
        alpha = self.selected_parameters["alpha"]

        print("k:", k)
        print("d:", d)
        print("alpha:", alpha)

        # Crear sliders nuevos con los valores del preset
        for i in range(1, k + 1):
            img.add_slider_float(
                label=f"Alpha {i}",
                tag=f"alpha_{i}",
                default_value=alpha[i - 1],
                min_value=0.0, max_value=1.0,
                parent=self.ALPHA_CONTAINER_ID
            )
            img.add_slider_int(
                label=f"D {i}",
                tag=f"D_{i}",
                default_value=d[i - 1],
                min_value=0, max_value=10000,
                parent=self.D_CONTAINER_ID
            )

        print("Parametros seleccionados:", self.selected_parameters)

    def update_parameters(self):
        k = img.get_value("K_slider")
        alpha = [img.get_value(f"alpha_{i}") for i in range(1, k + 1)]
        d = [img.get_value(f"D_{i}") for i in range(1, k + 1)]
        self.selected_parameters = {"alpha": alpha, "D": d, "K": k}

        print("Parametros seleccionados:", self.selected_parameters)

    def choose_effect(self):
        if self.selected_parameters["K"] == 1:
            self.effectChosen = EcoSimple(
                alpha=self.selected_parameters["alpha"][0],
                D=self.selected_parameters["D"][0]
            )
        else:
            self.effectChosen = ReverberadorPlano(
                alpha=self.selected_parameters["alpha"],
                D=self.selected_parameters["D"],
                K=self.selected_parameters["K"]
            )

        print("Efecto elegido:", self.effectChosen)

    def calculate_effect(self, signal):
        if (self.signal is None):
            print("No signal provided")
            return

        print("Previous signal: ", signal.Ydata)
        if self.effectChosen is None:
            print("No effect chosen")
            return signal

        y_out = self.effectChosen.applyEffect(signal, self.fs_value)
        signal.Ydata = y_out
        print("Effect applied to signal: ", signal.Ydata)
        return signal