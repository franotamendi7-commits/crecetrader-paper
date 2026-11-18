import torch, sys, os, platform, shutil, subprocess

print("=== ENTORNO KAGGLE (sonda, sin material del proyecto) ===")
print("python:", sys.version)
print("platform:", platform.platform())
print("torch:", torch.__version__)
print("cuda disponible:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("cuda version:", torch.version.cuda)
    print("gpu:", torch.cuda.get_device_name(0))
    print("vram GB:", round(torch.cuda.get_device_properties(0).total_memory / 1024**3, 2))
else:
    print("GPU: NO")
try:
    print("cpu count:", os.cpu_count())
    mem = open('/proc/meminfo').readline()
    print("meminfo:", mem.strip())
except Exception as e:
    print("meminfo error:", e)
total, used, free = shutil.disk_usage('/kaggle')
print("disco /kaggle GB (total/used/free):", [round(x / 1024**3, 1) for x in (total, used, free)])
for mod in ('transformers', 'accelerate', 'qwen_vl_utils', 'PIL'):
    try:
        m = __import__(mod)
        print(f"deps {mod}:", getattr(m, '__version__', 'ok'))
    except Exception as e:
        print(f"deps {mod}: NO ({type(e).__name__})")
