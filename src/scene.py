import cv2
import numpy as np
import moderngl_window as mglw
from pyrr import Matrix44, Vector3  # For matrix math
from moderngl_window import WindowConfig
from pathlib import Path
from orbit_camera import OrbitCamera
from shader_program import ShaderProgram
from scene_object import SceneObject
from imgui_bundle import imgui
from moderngl_window.integrations.imgui_bundle import ModernglWindowRenderer


# pip install moderngl moderngl-window pywavefront moderngl-window[imgui]



class Scene(WindowConfig):
    title = "OpenCV + ModernGL"
    window_size = (1024, 768)
    gl_version = (3, 3)
    resource_dir = (Path(__file__).parent.parent / 'data' / 'modernGL').resolve()
    sampels = 4 # multi-sampling
    resizable = False
    vsync = True
    use_imgui = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.wnd.ctx.error
        
        self.shader_program = ShaderProgram(self.ctx)
        assert Path(self.resource_dir, "shaders/vertex.glsl").exists(), "Vertex shader program not found"
        assert Path(self.resource_dir, "shaders/fragment.glsl").exists(), "Fragment shader program not found"

        self.prog = self.shader_program.load_shader(
            name = "crate",
            vertex_path=self.resource_dir / 'shaders' / 'vertex.glsl',
            fragment_path=self.resource_dir / 'shaders' / 'fragment.glsl'
        )

        print(f"Loaded shader program successfully")

        # Verify the model and texture exist
        # assert Path(self.resource_dir, "models/crate.obj").exists(), "Model not found"
        assert Path(self.resource_dir, "textures/bunny.jpg").exists(), "Bunny texture not found"

        # Load the crate
        crate_mesh = self.load_scene("models/bunny.obj").root_nodes[0].mesh.vao
        crate_tex = self.load_texture_2d("textures/bunny.jpg")
        self.object = SceneObject(crate_mesh, crate_tex, editable=True)

        # Load the floor
        floor_mesh = self.load_scene("models/floor.obj").root_nodes[0].mesh.vao
        floor_tex = self.load_texture_2d("textures/tile_floor.jpg")
        self.floor = SceneObject(floor_mesh, floor_tex, position=Vector3([0, -0.01, 0]))
        
        # Setup orbit camera params
        self.cam = OrbitCamera()
        self.cam_speed = 2.5 # Camera speed when moving

        # OpenCV webcam
        self.cap = cv2.VideoCapture(0)

    def on_render(self, time, frame_time) -> None:
        # Read a frame from webcam
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.wnd.close()
        
        self.handle_movement(frame_time)
        # Todo: Handle object works good one position, but adjusts both scales and rotations for some reason
        self.handle_object(self.object, frame_time)

        self.ctx.clear(0.1, 0.1, 0.1)
        self.ctx.enable(self.ctx.DEPTH_TEST)
        
        view = self.cam.get_view_matrix()
        proj = Matrix44.perspective_projection(
            fovy=45.0,
            aspect=self.wnd.aspect_ratio,
            near=0.1,
            far=100.0,
            dtype='f4'
        )

        self.prog['view'].write(view.astype('f4').tobytes())
        self.prog['proj'].write(proj.astype('f4').tobytes())
                
        self.object.render(self.prog, texture_unit=0)
        self.floor.render(self.prog, texture_unit=1, uv_scale=1)
        print(f"Object: Position: {self.object.position}, Rotation: {self.object.rotation}, Scale: {self.object.scale}")
        print(f"Floor: Position: {self.floor.position}, Rotation: {self.floor.rotation}, Scale: {self.floor.scale}")

    def handle_object(self, object: SceneObject, dt):
        keys = self.wnd.keys
        speed = 2.0 * dt
        rot_speed = 45.0 * dt
        scale_speed = 0.5 * dt

        if self.wnd.is_key_pressed(keys.I): object.position[2] -= speed # Forward
        if self.wnd.is_key_pressed(keys.K): object.position[2] += speed # Back
        if self.wnd.is_key_pressed(keys.J): object.position[0] -= speed # Left
        if self.wnd.is_key_pressed(keys.L): object.position[0] += speed # Right
        if self.wnd.is_key_pressed(keys.U): object.position[1] += speed # Up
        if self.wnd.is_key_pressed(keys.O): object.position[1] -= speed # Down

        if self.wnd.is_key_pressed(keys.COMMA): object.rotation[1] += rot_speed # ',' Rotate about Y axis
        if self.wnd.is_key_pressed(keys.PERIOD): object.rotation[1] -= rot_speed # '.' Rotate about Y axis
            
        if self.wnd.is_key_pressed(keys.N):  
            for i in range(3):
                object.scale[i] = max(0.1, object.scale[i] - scale_speed)
        if self.wnd.is_key_pressed(keys.M): 
            for i in range(3):
                object.scale[i] = min(10.0, object.scale[i] + scale_speed)

        if self.wnd.is_key_pressed(keys.BACKSPACE):
            object.position = [0, 0, 0]
            object.rotation = [0, 0, 0]
            object.scale = [1, 1, 1]


    def handle_movement(self, dt):
        keys = self.wnd.keys
        speed = self.cam_speed * dt
        rot_speed = 90.0 * dt
        zoom_speed = 2.0 * dt

        # Pan control        
        if self.wnd.is_key_pressed(keys.UP):
            self.cam.pan(0, 0, 1, speed)
        if self.wnd.is_key_pressed(keys.DOWN):
            self.cam.pan(0, 0, -1, speed)
        if self.wnd.is_key_pressed(keys.LEFT):
            self.cam.pan(-1, 0, 0, speed)
        if self.wnd.is_key_pressed(keys.RIGHT):
            self.cam.pan(1, 0, 0, speed)

        # Orbit cam rotation control
        if self.wnd.is_key_pressed(keys.W):
            self.cam.rotate(0, -rot_speed)
        if self.wnd.is_key_pressed(keys.S):
            self.cam.rotate(0, rot_speed)
        if self.wnd.is_key_pressed(keys.A):
            self.cam.rotate(-rot_speed, 0)
        if self.wnd.is_key_pressed(keys.D):
            self.cam.rotate(rot_speed, 0)

        # Zoom Controls
        if self.wnd.is_key_pressed(keys.Q):
            self.cam.zoom(-zoom_speed)
        if self.wnd.is_key_pressed(keys.E):
            self.cam.zoom(zoom_speed)

    def destroy(self):
        # Clean up OpenCV when window closes
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    mglw.run_window_config(Scene)
