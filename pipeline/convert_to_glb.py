import subprocess, os

OBJ = 'reconstruction/model_mesh_texture.obj'
GLB = 'models/glb/model.glb'
os.makedirs('models/glb', exist_ok=True)

subprocess.run([
    'gltf-pipeline', '-i', OBJ, '-o', GLB, '--draco.compressionLevel', '7'
], check=True)
print(f'GLB saved to {GLB}')
