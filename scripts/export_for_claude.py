import os
import zipfile

def export_clean_bundle(output_zip="CLUMSY_PROJECT_BUNDLE.zip"):
    # Exclude heavy binaries, models, caches, and git directory
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.vercel', 'scratch', 'workspace_output'}
    exclude_exts = {'.gguf', '.bin', '.onnx', '.pyc', '.log', '.zip'}

    total_files = 0
    total_bytes = 0

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Prune excluded directories in-place
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in exclude_exts or file.startswith('.'):
                    continue
                
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, '.')

                zipf.write(full_path, rel_path)
                total_files += 1
                total_bytes += os.path.getsize(full_path)

    zip_size_mb = os.path.getsize(output_zip) / (1024 * 1024)
    print(f"✅ Successfully exported clean Claude bundle: {output_zip}")
    print(f"📦 Files included: {total_files}")
    print(f"📊 Total uncompressed size: {total_bytes / (1024 * 1024):.2f} MB")
    print(f"🗜️ Compressed bundle size: {zip_size_mb:.2f} MB")

if __name__ == "__main__":
    export_clean_bundle()
