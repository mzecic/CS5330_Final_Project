from pyrr import Matrix44, Vector3
from moderngl import Context, Program, Texture
from math import radians

class SceneObject:
    def __init__(self, vao, texture: Texture, position=list([0, 0, 0]), scale=list([1, 1, 1]), rotation=list([0, 0, 0]), editable=False):
        self.vao = vao
        self.texture = texture
        self.position = position
        self.scale = scale
        self.rotation = rotation
        self.editable = editable 

    def get_model_matrix(self):
        Txyz = Matrix44.from_translation(self.position)
        Rx = Matrix44.from_x_rotation(radians(self.rotation[0]))
        Ry = Matrix44.from_y_rotation(radians(self.rotation[1]))
        Rz = Matrix44.from_z_rotation(radians(self.rotation[2]))
        Sxyz = Matrix44.from_scale(self.scale)

        return Txyz @ Rz @ Ry @ Rx @ Sxyz

    def render(self, prog:Program, texture_unit=0, uv_scale=1.0):
        self.texture.use(location=texture_unit)
        prog["Texture"] = texture_unit
        prog["uv_scale"].value = uv_scale
        prog["model"].write(self.get_model_matrix().astype('f4').tobytes())
        self.vao.render(prog)
