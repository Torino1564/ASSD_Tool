from Tool import *
from Instrument import *
from Signal import Signal, MathExpr
import dearpygui.dearpygui as img
import numpy as np
from scipy.signal import convolve


class Effect:
    def __init__(self, name, processor=None):
        self.name = name

        self.alpha = processor.alpha
        self.D = processor.D
        self.K = processor.K
    
    def calcular_fs_y_Dmuestras(x, Ds_segundos):
        dt = x[1] - x[0]  # Supone x uniformemente espaciado
        fs = 1.0 / dt
        Ds_muestras = [int(D * fs) for D in Ds_segundos]
        return fs, Ds_muestras

    def applyEffect(self, x):
        return self.processor.applyEffect(x)



class EcoSimple(Effect):
    def __init__(self, alpha=0.5, D=1000, K=1):
        self.alpha = [alpha]
        self.D = [D]
        self.K=1

    def applyEffect(self, signal):
        y = signal.GetYData()
        y_out = np.copy(y)
        x = signal.GetXData()
        
        fs, D_muestras = self.calcular_fs_y_Dmuestras(x, self.D)
        
        if D_muestras < len(y):
            y_out[D_muestras:] += self.alpha[0] * y[:-D_muestras]
        return y_out

class ReverberadorPlano(Effect):
    def __init__(self, K=5,
                 alpha=[0.5 / k for k in range(1, 5 + 1)], 
                 D=[1000 * k for k in range(1, 5 + 1)]
                 ):
        self.alpha = alpha
        self.D = D
        self.K = K

    def applyEffect(self, signal):
        y = signal.GetYData()
        y_out = np.copy(y)
        x = signal.GetXData()
        
        fs, D_muestras = self.calcular_fs_y_Dmuestras(x, self.D)
        
        for alpha, D in zip(self.alpha, self.D):
            if D < len(y):
                y_out[D:] += alpha * y[:-D]
        return y_out
        
    
EFFECTS_PRESETS = [
    Effect("Eco Simple", EcoSimple()),
    Effect("Reverberador Plano", ReverberadorPlano())
]
    
class EffectsTool(Tool):
    def __init__(self, editor, uuid, signal=None):
        Tool.__init__(self, name="Effects Tool", editor=editor, uuid=uuid)
        self.signal = signal
        self.effectChosen = None
        self.Init(self.Run)

    def Run(self):
        
        # IDs para widgets dinámicos
        self.K_SLIDER_ID = "K_slider"
        self.ALPHA_CONTAINER_ID = "alpha_container"
        self.D_CONTAINER_ID = "D_container"

        # Interfaz principal
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
        self.on_k_changed(None, None, None)
        
        
        img.add_text("Efectos:")
        with img.group(horizontal=True):
            for preset in EFFECTS_PRESETS:
                def make_callback(preset):
                    return lambda sender, app_data: self.set_preset(preset)

                img.add_button(label=preset.name, callback=make_callback(preset))
        
        
        img.add_button(label="Copiar efecto", callback=self.choose_effect)
        img.add_button(label="Calcular efecto", callback=lambda: self.calculate_effect())
        
        
    def on_k_changed(self, sender, app_data, user_data):
        k_value = img.get_value(self.K_SLIDER_ID)
        print(k_value)

        # Eliminar sliders antiguos
        img.delete_item(self.ALPHA_CONTAINER_ID, children_only=True)
        img.delete_item(self.D_CONTAINER_ID, children_only=True)

        # Crear nuevos sliders según K
        for i in range(1, k_value + 1):
            img.add_slider_float(
                label=f"Alpha {i}",
                tag=f"alpha_{i}",
                default_value=0.5,
                min_value=0.0, max_value=1.0,
                parent=self.ALPHA_CONTAINER_ID,
                callback=lambda s, a, u: self.update_parameters()
            )
            img.add_slider_int(
                label=f"D {i}",
                tag=f"D_{i}",
                default_value=1000,
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
                default_value= alpha[i - 1],
                min_value=0.0, max_value=1.0,
                parent=self.ALPHA_CONTAINER_ID
            )
            img.add_slider_int(
                label=f"D {i}",
                tag=f"D_{i}",
                default_value= d[i - 1],
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

    def calculate_effect(self):
        self.signal = self.editor.selected_signal
        signal = self.signal
        if(self.signal is None):
            print("No signal provided")
            return
        
        print("Previous signal: ", signal.Ydata)
        if self.effectChosen is None:
            print("No effect chosen")
            return signal
        
        y_out = self.effectChosen.applyEffect(signal)
        signal.Ydata = y_out
        print("Effect applied to signal: ", signal.Ydata)
        return signal