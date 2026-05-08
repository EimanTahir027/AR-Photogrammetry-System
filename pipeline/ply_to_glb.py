import trimesh, os

PLY = 'reconstruction/sparse_mesh.ply'
OBJ = 'models/obj/model_mesh.obj'
GLB = 'models/glb/model.glb'

os.makedirs('models/obj', exist_ok=True)
os.makedirs('models/glb', exist_ok=True)

print('Loading mesh...')
mesh = trimesh.load(PLY)
print(f'  Vertices: {len(mesh.vertices)}, Faces: {len(mesh.faces)}')

print('Saving OBJ...')
mesh.export(OBJ)

print('Saving GLB...')
mesh.export(GLB)

print(f'Done!\n  OBJ -> {OBJ}\n  GLB -> {GLB}')