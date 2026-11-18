# FASE 3.7 — DIAGNÓSTICO DE OCR

## 1. Estado del OCR en el pipeline

### Hallazgo principal
**El pipeline vision_analyzer.py NO invoca OCR.** El OCR fue diseñado en prototype.py pero nunca integrado en el pipeline principal de visión.

### Evidencia
- `grep -rn "tesseract\|ocr\|pytesseract" experimental/scripts/` → sin resultados
- `data/ocr_results.json` → no existe
- `vision_analysis.json` → no tiene campo "ocr_text"

### Conclusión
La afirmación "OCR retorna vacío" en FASE 3.6 era incorrecta. El OCR simplemente no se ejecutaba. No es un problema de configuración ni de preprocesamiento.

## 2. Prueba manual de Tesseract

### Comando
```bash
tesseract frames/scene_009_463.4s.jpg stdout
```

### Resultado
```
Tain aten ter lak ag bone Rece tae elation
lun método claro, disciplinado y paso
```

### Interpretación
- Tesseract 5.5.4 funciona correctamente
- Detecta texto en español ("método claro, disciplinado")
- La calidad del OCR es moderada (errores de reconocimiento)
- El texto es legible para un humano

### Idiomas disponibles
- spa (español) ✓
- eng (inglés) ✓
- 162 idiomas en total

## 3. Prueba con diferentes configuraciones PSM

### PSM 3 (default - auto page segmentation)
```
$ tesseract frames/scene_009_463.4s.jpg stdout --psm 3
Tain aten ter lak ag bone Rece tae elation
lun método claro, disciplinado y paso
```

### PSM 6 (uniform block of text)
```
$ tesseract frames/scene_009_463.4s.jpg stdout --psm 6
Tain aten ter lak ag bone Rece tae elation
lun método claro, disciplinado y paso
```

### PSM 11 (sparse text)
```
$ tesseract frames/scene_009_463.4s.jpg stdout --psm 11
Tain aten ter lak ag bone Rece tae elation
lun método claro, disciplinado y paso
```

### Conclusión
PSM no cambia significativamente el resultado. El texto es detectable pero con errores de OCR típicos.

## 4. Preprocesamiento y OCR

### Prueba con imagen original (640x352)
- Resultado: texto detectado (moderada calidad)

### Prueba con resize 2x (1280x704)
```bash
# (requiere PIL para resize)
```
- Resultado esperado: mejor calidad de OCR por mayor resolución

### Recomendación
- Usar spa+eng como idiomas
- PSM 6 para bloques uniformes de texto
- Preprocesamiento: resize 2x para mejorar calidad
- No es necesario reemplazar Tesseract

## 5. Integración propuesta

### Código a agregar en vision_analyzer.py
```python
import subprocess

def run_ocr(image_path, languages="spa+eng"):
    try:
        result = subprocess.run(
            ["tesseract", image_path, "stdout", "-l", languages, "--psm", "6"],
            capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception as e:
        return f"OCR_ERROR: {e}"
```

### Campos a agregar en vision_analysis.json
```json
{
    "ocr_text": "texto extraído por Tesseract",
    "ocr_language": "spa+eng",
    "ocr_psm": 6,
    "ocr_time_seconds": 1.2
}
```

## 6. Lo que NO es causa raíz
- Tesseract funciona correctamente
- Los idiomas spa y eng están disponibles
- Las imágenes tienen resolución suficiente (640x352)
- El preprocesamiento no elimina información (no se aplica actualmente)

## 7. Conclusión
El OCR no estaba roto. Estaba ausente del pipeline. La solución es integrar Tesseract en vision_analyzer.py con la configuración correcta. No se necesita instalar ningún motor alternativo.