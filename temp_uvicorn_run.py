import subprocess, time
proc = subprocess.Popen([
    'uvicorn',
    'app.main:app',
    '--reload',
], cwd=r'D:\aps\fast-api-learn_FastAPI_Supabase_JS_CSS_Trae_BAY\fast-api-learn', stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
try:
    time.sleep(5)
finally:
    proc.terminate()
out, _ = proc.communicate(timeout=5)
print(out)