import subprocess

# Percorso allo script shell
shell_script = "./prova.sh"

try:
    # Esegue lo script e cattura output
    result = subprocess.run(["bash", shell_script], check=True, text=True, capture_output=True)
    
    print("Output dello script:")
    print(result.stdout)

    if result.stderr:
        print("Errori (stderr):")
        print(result.stderr)

except subprocess.CalledProcessError as e:
    print(f"Errore durante l'esecuzione dello script: {e}")