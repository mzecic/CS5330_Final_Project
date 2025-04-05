import cv2
import numpy as np
import moderngl_window as mglw
from pyrr import Matrix44, Vector3  # For matrix math
from moderngl_window import WindowConfig, geometry
from pathlib import Path
from math import radians, cos, sin # For orbit camera
from orbit_camera import OrbitCamera

# pip install moderngl moderngl_window pywavefront


class Scene(WindowConfig):
    title = "OpenCV + ModernGL"
    window_size = (512, 512)
    gl_version = (3, 3)
    resource_dir = (Path(__file__).parent.parent / 'data' / 'modernGL').resolve()
    sampels = 4 # multi-sampling
    resizable = False
    vsync = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Verify the model and texture exist
        # assert Path(self.resource_dir, "models/crate.obj").exists(), "Model not found"
        assert Path(self.resource_dir, "textures/crate.jpg").exists(), "Texture not found"    

        # Load the model / textures
        # self.mesh = self.load_scene("models/crate.obj").root_nodes[0].mesh
        self.texture = self.load_texture_2d("textures/crate.jpg")
        self.texture.use(location=0)

        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330

            uniform mat4 model;
            uniform mat4 view;
            uniform mat4 proj;

            in vec3 in_position;
            in vec2 in_texcoord;
            
            out vec2 v_uv;

            void main() {
                v_uv = in_texcoord;
                gl_Position = proj * view * model * vec4(in_position, 1.0);
            }
        """,
            fragment_shader="""
            #version 330

            uniform sampler2D Texture;

            in vec2 v_uv;
            out vec4 f_color;

            void main() {
                f_color = texture(Texture, v_uv);
            }
        """,
        )

        self.mesh = geometry.cube(attr_names=geometry.AttributeNames('in_position', texcoord_0='in_texcoord'))
        self.cube_pos = Matrix44.from_translation([0, 0, 0])
        self.start_time = 0.0
        
        # Setup orbit camera params
        self.cam = OrbitCamera()
        self.cam_speed = 2.5 # Camera speed when moving

        # OpenCV webcam
        self.cap = cv2.VideoCapture(0)

    def on_render(self, time, frame_time):
        # Read a frame from webcam
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            # Simple control: use brightness to control scale
            

            # Optional: display webcam for debugging
            cv2.imshow("Webcam", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.wnd.close()
        
        self.handle_movement(frame_time)

        self.ctx.clear(0.1, 0.1, 0.1)
        self.ctx.enable(self.ctx.DEPTH_TEST)
        
        model = self.cube_pos
        view = self.cam.get_view_matrix()
        proj = Matrix44.perspective_projection(
            fovy=45.0,
            aspect=self.wnd.aspect_ratio,
            near=0.1,
            far=100.0,
            dtype='f4'
        )


        self.prog['model'].write(model.astype('f4').tobytes())
        self.prog['view'].write(view.astype('f4').tobytes())
        self.prog['proj'].write(proj.astype('f4').tobytes())
        self.prog["Texture"] = 0
        
        self.mesh.render(self.prog)
        
        # self.mesh.render()

    def handle_movement(self, dt):
        keys = self.wnd.keys
        vel = self.cam_speed * dt
        rot_vel = 90.0 * dt
        zoom_vel = 2.0 * dt

        # Pan control        
        if self.wnd.is_key_pressed(keys.UP):
            self.cam.pan(0, 0, 1, vel)
        if self.wnd.is_key_pressed(keys.DOWN):
            self.cam.pan(0, 0, -1, vel)
        if self.wnd.is_key_pressed(keys.LEFT):
            self.cam.pan(-1, 0, 0, vel)
        if self.wnd.is_key_pressed(keys.RIGHT):
            self.cam.pan(1, 0, 0, vel)

        # Orbit cam rotation control
        if self.wnd.is_key_pressed(keys.W):
            self.cam.rotate(0, -rot_vel)
        if self.wnd.is_key_pressed(keys.S):
            self.cam.rotate(0, rot_vel)
        if self.wnd.is_key_pressed(keys.A):
            self.cam.rotate(-rot_vel, 0)
        if self.wnd.is_key_pressed(keys.D):
            self.cam.rotate(rot_vel, 0)

        # Zoom Controls
        if self.wnd.is_key_pressed(keys.Q):
            self.cam.zoom(-zoom_vel)
        if self.wnd.is_key_pressed(keys.E):
            self.cam.zoom(zoom_vel)

    def destroy(self):
        # Clean up OpenCV when window closes
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    mglw.run_window_config(Scene)
