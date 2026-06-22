"""
app/services/model_service.py
Memuat dan menjalankan inference menggunakan model TensorFlow Lite.

Prinsip penting:
- Interpreter dimuat sekali saat aplikasi dimulai (lazy singleton).
  Memuat ulang di setiap request sangat mahal dan tidak efisien.
- Jika file model tidak ditemukan, service mengembalikan error yang jelas
  dan TIDAK menghasilkan prediksi dummy.
- Path model menggunakan path absolut berbasis PROJECT_ROOT agar tidak
  bergantung pada current working directory saat server dijalankan.
- Jika MODEL_OUTPUT_TYPE=logits, softmax numerik stabil diterapkan.
  Jika MODEL_OUTPUT_TYPE=probabilities, output langsung digunakan.
"""

import logging
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

from app.config import Config
from app.utils.errors import ModelNotAvailableError, InferenceError

logger = logging.getLogger(__name__)


# --- Singleton interpreter ---
# Interpreter hanya dimuat sekali. None berarti belum dimuat atau gagal dimuat.
_interpreter = None
_model_load_attempted = False
_model_load_error: Optional[str] = None


def _load_interpreter():
    """
    Memuat TFLite interpreter dari file model.
    Dipanggil sekali saat pertama kali dibutuhkan (lazy loading).

    Lazy loading dipilih agar health check tetap bisa berjalan meskipun
    import tflite_runtime gagal di environment tertentu.
    """
    global _interpreter, _model_load_attempted, _model_load_error

    if _model_load_attempted:
        return  # Sudah dicoba sebelumnya, tidak perlu ulang

    _model_load_attempted = True
    model_path = Path(Config.MODEL_PATH)

    # --- Periksa keberadaan file model ---
    if not model_path.exists():
        _model_load_error = (
            f"File model tidak ditemukan di '{model_path}'. "
            "Pastikan mango_classifier.tflite sudah ditempatkan di folder model/."
        )
        logger.warning(_model_load_error)
        return

    # --- Muat TFLite interpreter ---
    try:
        # Coba import tflite_runtime terlebih dahulu (ringan, target production).
        # Jika tidak tersedia, coba tensorflow.lite sebagai fallback development.
        try:
            import ai_edge_litert.interpreter as tflite
            logger.info("Menggunakan ai_edge_litert untuk inference.")
        except ImportError:
            try:
                import tflite_runtime.interpreter as tflite
                logger.info("Menggunakan tflite_runtime untuk inference.")
            except ImportError:
                logger.warning(
                    "tflite_runtime/ai_edge_litert tidak ditemukan. Mencoba tensorflow.lite sebagai fallback. "
                    "Untuk production, gunakan ai-edge-litert agar lebih ringan."
                )
                import tensorflow.lite as tflite

        interpreter = tflite.Interpreter(model_path=str(model_path))
        interpreter.allocate_tensors()

        # Simpan detail input/output untuk digunakan saat inference
        _interpreter = {
            "interpreter": interpreter,
            "input_details": interpreter.get_input_details(),
            "output_details": interpreter.get_output_details(),
        }

        logger.info(
            "Model TFLite berhasil dimuat dari '%s'. Input: %s, Output: %s",
            model_path,
            _interpreter["input_details"][0]["shape"],
            _interpreter["output_details"][0]["shape"],
        )

    except Exception as exc:
        _model_load_error = f"Gagal memuat TFLite interpreter: {exc}"
        logger.error(_model_load_error)


def is_model_loaded() -> bool:
    """
    Mengembalikan True jika model berhasil dimuat.
    Digunakan oleh health check endpoint.
    """
    _load_interpreter()
    return _interpreter is not None


def predict(img_array: np.ndarray) -> Tuple[str, float]:
    """
    Menjalankan inference TFLite dan mengembalikan class key dan confidence tertinggi.

    Args:
        img_array: NumPy array shape (1, H, W, 3) dtype float32

    Returns:
        Tuple (class_key, confidence)
        - class_key  : string kelas, misalnya "ripe", "unripe", "rotten"
        - confidence : float antara 0.0 dan 1.0

    Raises:
        ModelNotAvailableError: jika model belum tersedia
        InferenceError: jika inference gagal
    """
    _load_interpreter()

    if _interpreter is None:
        raise ModelNotAvailableError(
            _model_load_error or "Model belum tersedia. Tempatkan mango_classifier.tflite di folder model/."
        )

    try:
        interpreter = _interpreter["interpreter"]
        input_details = _interpreter["input_details"]
        output_details = _interpreter["output_details"]

        # --- Set input tensor ---
        interpreter.set_tensor(input_details[0]["index"], img_array)

        # --- Jalankan inference ---
        interpreter.invoke()

        # --- Ambil output tensor ---
        raw_output = interpreter.get_tensor(output_details[0]["index"])  # shape: (1, num_classes)
        output_values = raw_output[0]  # hapus dimensi batch -> shape: (num_classes,)

        # --- Konversi output ke probabilitas ---
        probabilities = _to_probabilities(output_values)

        # --- Temukan kelas dengan confidence tertinggi ---
        class_index = int(np.argmax(probabilities))
        confidence = float(probabilities[class_index])

        # Validasi bahwa class_index valid untuk CLASS_LABELS
        class_labels = Config.CLASS_LABELS
        if class_index >= len(class_labels):
            raise InferenceError(
                f"Output model memiliki {len(probabilities)} kelas, "
                f"tetapi CLASS_LABELS hanya mendefinisikan {len(class_labels)} kelas. "
                "Periksa konfigurasi CLASS_LABELS."
            )

        class_key = class_labels[class_index]
        return class_key, confidence

    except (ModelNotAvailableError, InferenceError):
        raise
    except Exception as exc:
        logger.error("Inference gagal: %s", exc, exc_info=True)
        raise InferenceError("Inference model gagal dijalankan. Coba lagi.")


def _to_probabilities(output_values: np.ndarray) -> np.ndarray:
    """
    Mengubah output model menjadi probabilitas berdasarkan MODEL_OUTPUT_TYPE.

    - "probabilities": output sudah berupa probabilitas. Tidak perlu softmax lagi.
    - "logits"       : output adalah logit mentah. Terapkan softmax numerik stabil.

    Softmax numerik stabil: exp(x - max(x)) / sum(exp(x - max(x)))
    Pengurangan max mencegah overflow pada nilai logit yang sangat besar.
    """
    output_type = Config.MODEL_OUTPUT_TYPE.strip().lower()

    if output_type == "probabilities":
        return output_values

    elif output_type == "logits":
        # Softmax numerik stabil untuk mencegah overflow/underflow
        shifted = output_values - np.max(output_values)
        exp_values = np.exp(shifted)
        return exp_values / np.sum(exp_values)

    else:
        logger.warning(
            "MODEL_OUTPUT_TYPE '%s' tidak dikenali. Memperlakukan output sebagai probabilitas.",
            output_type,
        )
        return output_values


def reset_model_state():
    """
    Mereset state singleton model. Hanya digunakan untuk keperluan testing.
    Tidak boleh dipanggil di kode production.
    """
    global _interpreter, _model_load_attempted, _model_load_error
    _interpreter = None
    _model_load_attempted = False
    _model_load_error = None
