#!/usr/bin/env python3
"""
Resource Lifecycle Manager (V1).

Gestiona los ciclos de vida de OpenCode y Ollama para YouTubeTradingAgent:
- Inicio y cierre ordenado de OpenCode
- Carga y descarga automática de modelos Ollama
- Coordinación de solicitudes entre agentes
- Verificación de procesos activos/inactivos
- Registro de consumo RAM, CPU y swap
- Detección y respuesta conservadora ante presión térmica/memoria
- Recuperación segura ante interrupciones

Dirigido a ser usado por Hermes (el orquestador) y YouTubeTradingAgent.

Principio: "Los modelos y servicios se utilizan cuando hacen falta y se liberan
cuando terminan su trabajo. No mantener recursos cargados por inercia."
"""

from __future__ import annotations

import json
import os
import re
import signal
import subprocess
import time
import urllib.request
import urllib.error
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional, Dict, Any, List

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

DEFAULT_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
DEFAULT_OLLAMA_PORT = 11434
DEFAULT_OPENCODE_PORT = 1817

DEFAULT_STATE_FILENAME = "resource_lifecycle_state.json"
DEFAULT_LOCK_FILENAME = "resource_lifecycle.lock"

API_GENERATE = "/api/generate"
API_CHAT = "/api/chat"
API_EMBEDDINGS = "/api/embeddings"
API_PS = "/api/ps"
API_TAGS = "/api/tags"

# Tiempo de espera por petición Ollama (segundos)
OLLAMA_TIMEOUT = 300

# Tiempo de espera por petición HTTP genérica (segundos)
HTTP_TIMEOUT = 30

# Tiempo de espera para inicio/cierre de OpenCode (segundos)
OPENCODE_START_TIMEOUT = 30
OPENCODE_STOP_TIMEOUT = 30

# Número de veces que se intentará descargar un modelo antes de fallar
MAX_MODEL_LOAD_RETRIES = 3

# Intervalo de verificación (segundos)
POLL_INTERVAL = 10

# ---- Preferencias de configuración (sobreponibles con variables de entorno) ----
OLLAMA_URL = os.getenv("OLLAMA_URL", DEFAULT_OLLAMA_URL)
OLLAMA_PORT = int(os.getenv("OLLAMA_PORT", str(DEFAULT_OLLAMA_PORT)))
OPENCODE_PORT = int(os.getenv("OPENCODE_PORT", str(DEFAULT_OPENCODE_PORT)))


@dataclass
class ResourceSnapshot:
    """Instantánea de recursos (RAM, CPU, swap)."""
    ram_used_gb: float
    ram_free_gb: float
    ram_total_gb: float
    swap_used_gb: float
    swap_free_gb: float
    swap_total_gb: float
    cpu_used_percent: float
    timestamp: float


@dataclass
class ModelTrack:
    """Registro de un modelo Ollama cargado."""
    model_name: str
    loaded_at: float
    last_access: float
    source: str = "unknown"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ModelTrack":
        return cls(
            model_name=d["model_name"],
            loaded_at=d["loaded_at"],
            last_access=d["last_access"],
            source=d.get("source", "unknown"),
        )


@dataclass
class ProcessTrack:
    """Registro de un proceso del gestor."""
    pid: int
    name: str
    start_time: float
    exit_time: Optional[float] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "ProcessTrack":
        return cls(
            pid=d["pid"],
            name=d["name"],
            start_time=d["start_time"],
            exit_time=d.get("exit_time"),
            error=d.get("error"),
        )


class ResourceLifecycleManager:
    """
    Gestor centralizado de recursos para YouTubeTradingAgent.

    Administra el ciclo de vida de OpenCode y los modelos Ollama, con:
    - Bloqueos propios para coordinación
    - Estado persistente (JSON)
    - Recuperación segura tras interrupciones
    - Registro de consumo de recursos
    - Detección de presión térmica/memoria
    """

    def __init__(self, base_dir: Path, state_file: Optional[Path] = None,
                 lock_file: Optional[Path] = None, poll_interval: int = POLL_INTERVAL):
        self.base_dir = Path(base_dir).resolve()
        self.work_dir = self.base_dir / "experimental" / "results"
        self.state_file = state_file or self.work_dir / DEFAULT_STATE_FILENAME
        self.lock_file = lock_file or self.work_dir / DEFAULT_LOCK_FILENAME
        self.poll_interval = poll_interval
        self._last_save_time = 0.0  # Última hora de guardado (atributo de instancia)

        # Estado interno
        self.state: Dict[str, Any] = self._load_state()
        self._lock_fd: Optional[int] = None
        self._lock_pid: Optional[int] = None
        self._ollama_connected = False
        self._opencode_running = False

        # Asegurar directorios
        self.work_dir.mkdir(parents=True, exist_ok=True)
        if self._last_save_time != self.state.get("last_update"):
            self.save_state()

    # ---------------------------------------------------------------------
    # Estado persistente
    # ---------------------------------------------------------------------

    def _load_state(self) -> Dict[str, Any]:
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        return data
            except Exception:
                pass
        return self._default_state()

    def _default_state(self) -> Dict[str, Any]:
        return {
            "version": 1,
            "managed_at": time.time(),
            "state": "idle",
            "last_update": None,
            "last_error": None,
            "models": [],
            "processes": [],
            "resources_before": None,
            "resources_after": None,
            "checkpoints": {},
            "pressure": {
                "temperature": None,
                "memory_pressure": None,
                "cpu_pressure": None,
                "swap_used": None,
            },
            "history": [],
        }

    def save_state(self, force: bool = False) -> bool:
        """Guarda el estado persistente. Devuelve True si se guardó."""
        if not force and self.state.get("last_update") == self._last_save_time:
            return True
        self.state["last_update"] = time.time()
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2)
            self._last_save_time = self.state["last_update"]
            return True
        except Exception as e:
            self.state["last_error"] = f"failed to save state: {e}"
            return False

    # ---------------------------------------------------------------------
    # Bloqueo propio (coordinación)
    # ---------------------------------------------------------------------

    def acquire_lock(self, timeout: int = 30) -> bool:
        """
        Intenta adquirir el bloqueo atómico.

        Usa `os.O_CREAT | os.O_EXCL | os.O_WRONLY` para garantizar que solo
        un proceso puede poseer el bloqueo. Si el bloqueo existe, se retorna
        False y el segundo proceso omite/suspende la ejecución.

        Returns:
            True si el bloqueo fue adquirido, False en caso contrario.
        """
        import os as _os

        # Generar PID
        pid = os.getpid()

        # Abrir el archivo con O_CREAT | O_EXCL | O_WRONLY para atomicidad
        # Esto garantiza que solo un proceso puede crear el bloqueo
        try:
            fd = os.open(
                str(self.lock_file),
                os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                0o644
            )
        except FileExistsError:
            # Otro proceso ya posee el bloqueo
            return False
        except Exception:
            raise

        try:
            # Guardar PID en el archivo de bloqueo
            with os.fdopen(fd, "w") as f:
                f.write(f"pid {pid}\n")
                f.flush()
                os.fsync(f.fileno())

            self._lock_fd = fd
            self._lock_pid = pid
            return True

        except Exception:
            # Si falla, cerrar el descriptor y limpiar
            try:
                os.close(fd)
            except Exception:
                pass
            raise

    def release_lock(self) -> bool:
        """Libera el bloqueo. Solo el dueño debe liberarlo."""
        if self._lock_fd is not None:
            try:
                os.close(self._lock_fd)
            except Exception:
                pass
            self._lock_fd = None

        if self._lock_pid is not None:
            try:
                os.unlink(self.lock_file)
            except FileNotFoundError:
                pass
            except Exception as e:
                self.state["last_error"] = f"failed to remove lock file: {e}"
            self._lock_pid = None
            return True

        return False

    def is_locked(self) -> bool:
        """Verifica si el bloqueo está en posesión."""
        try:
            if not self.lock_file.exists():
                return False
            with open(self.lock_file, "r") as f:
                content = f.read()
            return True
        except Exception:
            return False

    def get_lock_owner(self) -> Optional[Dict[str, Any]]:
        """Devuelve los metadatos del propietario del bloqueo."""
        if not self.lock_file.exists():
            return None
        try:
            with open(self.lock_file, "r") as f:
                content = f.read()
            m = re.search(r"pid (\d+)", content)
            return {"pid": int(m.group(1)) if m else None, "file": str(self.lock_file)}
        except Exception:
            return None

    # ---------------------------------------------------------------------
    # Conexión a Ollama
    # ---------------------------------------------------------------------

    def is_ollama_available(self) -> bool:
        """Verifica si Ollama está disponible en el puerto."""
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}{API_TAGS}", method="GET",
                                         headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    self._ollama_connected = True
                    return True
        except Exception:
            self._ollama_connected = False
        return False

    def get_models(self) -> List[Dict[str, Any]]:
        """Lista los modelos Ollama disponibles."""
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}{API_TAGS}", method="GET",
                                         headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("models", [])
        except Exception as e:
            self.state["last_error"] = f"failed to list Ollama models: {e}"
            return []

    def get_running_models(self) -> List[Dict[str, Any]]:
        """Lista los modelos en memoria (loaded) actualmente."""
        try:
            req = urllib.request.Request(f"{OLLAMA_URL}{API_PS}", method="GET",
                                         headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("models", [])
        except Exception as e:
            self.state["last_error"] = f"failed to get running models: {e}"
            return []

    def load_model(self, model_name: str, keep_alive: int = 0,
                   timeout: int = OLLAMA_TIMEOUT) -> bool:
        """
        Carga un modelo Ollama.

        Args:
            model_name: Nombre del modelo (ej. 'qwen2.5vl:3b')
            keep_alive: Tiempo en segundos para mantener cargado el modelo.
                        Si 0, el modelo se descargará inmediatamente después de la
                        primera request. Para mantenerlo recomendamos un valor
                        positivo.
            timeout: Tolerancia de petición en segundos.

        Returns:
            True si el modelo se pudo cargar, False en caso contrario.
        """
        if not self.is_ollama_available():
            self.state["last_error"] = "Ollama no está disponible en el puerto"
            return False

        # Verificar si ya está cargado
        running = self.get_running_models()
        for r in running:
            if r.get("name") == model_name:
                self.state["last_error"] = None
                return True

        # Cargar el modelo
        for attempt in range(1, MAX_MODEL_LOAD_RETRIES + 1):
            try:
                payload: Dict[str, Any] = {
                    "model": model_name,
                    "prompt": "",
                }
                if keep_alive > 0:
                    payload["keep_alive"] = keep_alive

                req = urllib.request.Request(
                    f"{OLLAMA_URL}{API_GENERATE}",
                    data=json.dumps(payload).encode("utf-8"),
                    method="POST",
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = resp.read()
                    try:
                        response_json = json.loads(data)
                        self.state["last_error"] = None
                        return True
                    except Exception:
                        self.state["last_error"] = "Respuesta de Ollama inesperada"
                        return False

            except urllib.error.HTTPError as e:
                error_body = e.read().decode("utf-8", errors="replace")
                self.state["last_error"] = f"HTTP error loading model: {e.code} {error_body}"
                if e.code == 404:
                    self.state["last_error"] += " (modelo no encontrado)"
                return False
            except Exception as e:
                if attempt < MAX_MODEL_LOAD_RETRIES:
                    time.sleep(2)
                    continue
                self.state["last_error"] = f"Error loading model: {e}"
                return False

        return False

    def unload_model(self, model_name: str, keep_alive: int = 0) -> bool:
        """
        Descarga un modelo Ollama de memoria.

        Usa keep_alive: 0 para descargar el modelo inmediatamente.
        No utiliza 'ollama rm' (según política).
        No genera inferencias artificiales.

        Args:
            model_name: Nombre del modelo a descargar.
            keep_alive: Tiempo en segundos para mantener cargado el modelo
                        antes de descargar. 0 = inmediato.

        Returns:
            True si el modelo se descargó correctamente, False en caso contrario.
        """
        # Verificar si el modelo está cargado usando /api/ps
        # (los modelos que aparecen en /api/ps están en memoria)
        running = self.get_running_models()
        model_found = any(r.get("name") == model_name for r in running)

        if not model_found:
            self.state["last_error"] = "Modelo no está cargado"
            return True  # No está cargado, no hay nada que descargar

        # Modelo está cargado, proceder a descargar
        try:
            payload: Dict[str, Any] = {
                "model": model_name,
                "prompt": "",
                "keep_alive": 0,  # Descargar inmediatamente
            }
            req = urllib.request.Request(
                f"{OLLAMA_URL}{API_GENERATE}",
                data=json.dumps(payload).encode("utf-8"),
                method="POST",
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                # El modelo debería descargarse después de la respuesta
                # Verificar después de un breve retraso
                time.sleep(5)  # Esperar más tiempo para descarga segura

            # Verificar que el modelo ya no está en memoria
            if not self.is_model_loaded(model_name):
                self.state["last_error"] = None
                return True
            else:
                self.state["last_error"] = "Modelo no descargado correctamente"
                return False
        except Exception as e:
            self.state["last_error"] = f"Error unloading model: {e}"
            return False

    def is_model_loaded(self, model_name: str) -> bool:
        """Verifica si el modelo está actualmente cargado en memoria."""
        running = self.get_running_models()
        for r in running:
            if r.get("name") == model_name:
                return True
        return False

    def cleanup_models(self, models: List[str]) -> int:
        """
        Descarga una lista de modelos de memoria.

        Args:
            models: Lista de nombres de modelo a descargar.

        Returns:
            Número de modelos descargados exitosamente.
        """
        loaded_count = 0
        for model_name in models:
            if self.is_model_loaded(model_name):
                if self.unload_model(model_name):
                    loaded_count += 1
        return loaded_count

    # ---------------------------------------------------------------------
    # Integración con OpenCode
    # ---------------------------------------------------------------------

    def is_opencode_available(self) -> bool:
        """Verifica si OpenCode está escuchando en su puerto."""
        try:
            req = urllib.request.Request(f"http://localhost:{OPENCODE_PORT}", method="GET")
            with urllib.request.urlopen(req, timeout=5) as resp:
                if resp.status == 200:
                    self._opencode_running = True
                    return True
        except Exception:
            self._opencode_running = False
        return False

    def is_opencode_running(self) -> bool:
        """Verifica si OpenCode está en ejecución."""
        return self._opencode_running

    # ---------------------------------------------------------------------
    # Registro de recursos (RAM, CPU, swap)
    # ---------------------------------------------------------------------

    def get_memory_snapshot(self) -> ResourceSnapshot:
        """
        Obtiene una instantánea de los recursos del sistema.
        Usa vm_stat en macOS.
        """
        try:
            # Leer vm_stat
            with open("/proc/vmstat", "r") as f:
                vmstat = f.read()

            # Calcular páginas usadas
            ram_total = None
            try:
                out = subprocess.run(["sysctl", "-n", "hw.memsize"],
                                     capture_output=True, text=True, check=True)
                ram_total = int(out.stdout.strip()) / (1024 ** 3)
            except Exception:
                ram_total = 8.0

            # Estimación por páginas
            free = active = inactive = wired = 0.0
            try:
                out = subprocess.run(["vm_stat"], capture_output=True, text=True, check=True)
                vm_lines = out.stdout
                for line in vm_lines.splitlines():
                    if "Pages free" in line:
                        vm_page_size = 16384  # bytes por página (4 KiB x 4)
                        free_pages = int(line.split(":")[1].strip())
                        free = free_pages * (vm_page_size / 1024)
                    if "Pages active" in line:
                        vm_page_size = 16384
                        active_pages = int(line.split(":")[1].strip())
                        active = active_pages * (vm_page_size / 1024)
                    if "Pages inactive" in line:
                        vm_page_size = 16384
                        inactive_pages = int(line.split(":")[1].strip())
                        inactive = inactive_pages * (vm_page_size / 1024)
                    if "Pages wired down" in line:
                        vm_page_size = 16384
                        wired_pages = int(line.split(":")[1].strip())
                        wired = wired_pages * (vm_page_size / 1024)
            except Exception:
                pass

            ram_free = free
            ram_used = active + inactive + wired
            ram_total_gb = ram_total
            ram_free_gb = ram_free / 1024
            ram_used_gb = ram_used / 1024

            # Swap
            swap_used = 0.0
            swap_total = 0.0
            try:
                out = subprocess.run(["swapinfo"], capture_output=True, text=True, check=True)
                for line in out.stdout.splitlines():
                    if line.startswith("/"):
                        parts = line.split()
                        if len(parts) >= 4:
                            swap_used = float(parts[2]) / 1024
                            swap_total = float(parts[3]) / 1024
                            break
            except Exception:
                pass

            cpu_used = self.get_cpu_percent()

            return ResourceSnapshot(
                ram_used_gb=ram_used_gb,
                ram_free_gb=ram_free_gb,
                ram_total_gb=ram_total_gb,
                swap_used_gb=swap_used,
                swap_free_gb=swap_total - swap_used,
                swap_total_gb=swap_total,
                cpu_used_percent=cpu_used,
                timestamp=time.time(),
            )

        except Exception as e:
            self.state["last_error"] = f"Error getting memory snapshot: {e}"
            return ResourceSnapshot(
                ram_used_gb=0.0, ram_free_gb=0.0, ram_total_gb=8.0,
                swap_used_gb=0.0, swap_free_gb=0.0, swap_total_gb=0.0,
                cpu_used_percent=0.0, timestamp=time.time(),
            )

    def get_cpu_percent(self) -> float:
        """Obtiene el uso general de CPU."""
        try:
            out = subprocess.run(["ps", "-A", "-o", "pcpu"], capture_output=True, text=True, check=True)
            lines = out.stdout.strip().splitlines()
            if len(lines) > 1:
                avg = sum(float(l.split()[0]) for l in lines[1:]) / len(lines[1:])
                return round(avg, 2)
        except Exception:
            pass
        return 0.0

    # ---------------------------------------------------------------------
    # Detección de presión térmica/memoria
    # ---------------------------------------------------------------------

    def detect_thermal_pressure(self) -> Optional[Dict[str, Any]]:
        """
        Detecta presión térmica del sistema mediante logs de macOS.

        Returns:
            Dict con detalles de presión, o None si no hay eventos.
        """
        try:
            out = subprocess.run(
                ["log", "show", "--last", "1h",
                 "--predicate", 'eventMessage CONTAINS "thermal" OR processImagePath CONTAINS "thermalmonitord"'],
                capture_output=True, text=True, check=True
            )
            lines = out.stdout.splitlines()
            for line in lines:
                if "thermal" in line.lower() or "thermalmonitord" in line:
                    return {"raw": line.strip(), "timestamp": time.time()}
        except Exception:
            pass
        return None

    def detect_memory_pressure(self, snapshot: Optional[ResourceSnapshot] = None) -> str:
        """
        Determina el nivel de presión de memoria.

        Returns:
            "OK", "WARNING" o "CRITICAL".
        """
        if snapshot is None:
            snapshot = self.get_memory_snapshot()

        free_gb = snapshot.ram_free_gb
        total_gb = snapshot.ram_total_gb
        if total_gb <= 0:
            return "WARNING"

        usage_percent = (snapshot.ram_used_gb / total_gb) * 100

        if usage_percent < 70:
            return "OK"
        elif usage_percent < 90:
            return "WARNING"
        else:
            return "CRITICAL"

    def record_resource_snapshot(self, snapshot: Optional[ResourceSnapshot] = None) -> Dict[str, Any]:
        """
        Registra una instantánea de recursos.

        Returns:
            Diccionario con la instantánea.
        """
        if snapshot is None:
            snapshot = self.get_memory_snapshot()

        self.state["resources_before"] = {
            "ram_used_gb": snapshot.ram_used_gb,
            "ram_free_gb": snapshot.ram_free_gb,
            "ram_total_gb": snapshot.ram_total_gb,
            "swap_used_gb": snapshot.swap_used_gb,
            "cpu_used_percent": snapshot.cpu_used_percent,
            "timestamp": snapshot.timestamp,
        }
        return {"timestamp": snapshot.timestamp, "ram_used_gb": snapshot.ram_used_gb,
                "ram_free_gb": snapshot.ram_free_gb, "ram_total_gb": snapshot.ram_total_gb}

    # ---------------------------------------------------------------------
    # Gestión de checkpoints
    # ---------------------------------------------------------------------

    def create_checkpoint(self, task_id: str, checkpoint_data: Dict[str, Any]) -> bool:
        """
        Crea un checkpoint persistente.

        Args:
            task_id: Identificador de la tarea (ej. video_id, job_id)
            checkpoint_data: Datos del checkpoint.

        Returns:
            True si se guardó correctamente.
        """
        self.state["checkpoints"][task_id] = {
            "data": checkpoint_data,
            "created_at": time.time(),
            "updated_at": time.time(),
        }
        self.save_state(force=True)
        return True

    def load_checkpoint(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Carga un checkpoint guardado desde el archivo de estado.
        """
        # Cargar el estado desde el archivo
        loaded = self._load_state()
        if task_id in loaded.get("checkpoints", {}):
            return loaded["checkpoints"][task_id].get("data")
        return None

    def cleanup_checkpoints(self, older_than: float) -> int:
        """
        Elimina checkpoints antiguos.

        Args:
            older_than: Tiempo (segundos) desde el que se consideran obsoletos.

        Returns:
            Cantidad de checkpoints eliminados.
        """
        count = 0
        for task_id, ckpt in list(self.state.get("checkpoints", {}).items()):
            if time.time() - ckpt.get("updated_at", 0) > older_than:
                del self.state["checkpoints"][task_id]
                count += 1
        if count > 0:
            self.save_state(force=True)
        return count

    # ---------------------------------------------------------------------
    # Recuperación
    # ---------------------------------------------------------------------

    def auto_recover(self) -> bool:
        """
        Intenta recuperar una sesión interrumpida.

        Returns:
            True si la recuperación fue exitosa.
        """
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    self.state = json.load(f)
                self.state["managed_at"] = time.time()
                return True
        except Exception as e:
            self.state["last_error"] = f"Auto-recovery failed: {e}"
        return False

    def safe_shutdown(self) -> bool:
        """
        Realiza un cierre seguro del gestor.

        Guarda el estado y libera el bloqueo.

        Returns:
            True si el cierre fue exitoso.
        """
        self.save_state(force=True)
        success = self.release_lock()
        return success

    # ---------------------------------------------------------------------
    # Verificación de procesos
    # ---------------------------------------------------------------------

    def get_process_info(self, pid: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información de un proceso.

        Returns:
            Dict con información del proceso, o None si no existe.
        """
        try:
            out = subprocess.run(
                ["ps", "-p", str(pid), "-o", "%p,%c,%t,%r,%s"],
                capture_output=True, text=True, check=True
            )
            lines = out.stdout.strip().splitlines()
            if len(lines) > 1:
                parts = lines[1].split()
                return {"pid": int(parts[0]), "name": parts[1],
                        "etime": parts[2], "rss": parts[3], "cpu": parts[4]}
        except Exception:
            pass
        return None

    def find_processes(self, name_pattern: str) -> List[Dict[str, Any]]:
        """
        Busca procesos que coincidan con un patrón.

        Returns:
            Lista de dicts con información del proceso.
        """
        result = []
        try:
            out = subprocess.run(
                ["ps", "-A", "-o", "pid,%c,%t,%r,%s"],
                capture_output=True, text=True, check=True
            )
            for line in out.stdout.strip().splitlines()[1:]:
                parts = line.split()
                if len(parts) >= 5 and name_pattern in parts[1]:
                    result.append({
                        "pid": int(parts[0]), "name": parts[1],
                        "etime": parts[2], "rss": parts[3], "cpu": parts[4]
                    })
        except Exception:
            pass
        return result

    # ---------------------------------------------------------------------
    # Utilidades
    # ---------------------------------------------------------------------

    def is_official_ollama(self) -> bool:
        """Verifica que Ollama esté instalado oficialmente."""
        try:
            out = subprocess.run(["which", "ollama"], capture_output=True, text=True, check=True)
            return out.stdout.strip() != ""
        except Exception:
            return False

    def get_ollama_version(self) -> Optional[str]:
        """Devuelve la versión de Ollama."""
        try:
            out = subprocess.run(["ollama", "--version"], capture_output=True, text=True, check=True)
            return out.stdout.strip()
        except Exception:
            return None

    def verify_ollama_service(self) -> bool:
        """Verifica que Ollama esté funcionando correctamente."""
        return self.is_ollama_available() and self.get_models() != []

    def stop(self) -> None:
        """Detiene el gestor."""
        self.safe_shutdown()
