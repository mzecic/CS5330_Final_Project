import cv2
import numpy as np
import moderngl_window as mglw
from pyrr import Matrix44, Vector3  # For matrix math
from moderngl_window import WindowConfig, geometry
from pathlib import Path
from math import radians, cos, sin # For orbit camera


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

        # vertices = np.array([
		# # x, y, z, u, v

		# # front face
		# -1.0,  1.0,  1.0, 0.0, 1.0,
		#  1.0, -1.0,  1.0, 1.0, 0.0,
		#  1.0,  1.0,  1.0, 1.0, 1.0,
		# -1.0,  1.0,  1.0, 0.0, 1.0,
		# -1.0, -1.0,  1.0, 0.0, 0.0,
		#  1.0, -1.0,  1.0, 1.0, 0.0,

		# # back face
		# -1.0,  1.0, -1.0, 0.0, 1.0,
		#  1.0, -1.0, -1.0, 1.0, 0.0,
		#  1.0,  1.0, -1.0, 1.0, 1.0,
		# -1.0,  1.0, -1.0, 0.0, 1.0,
		# -1.0, -1.0, -1.0, 0.0, 0.0,
		#  1.0, -1.0, -1.0, 1.0, 0.0,

		# # left face
		# -1.0,  1.0, -1.0, 0.0, 1.0,
		# -1.0, -1.0,  1.0, 1.0, 0.0,
		# -1.0,  1.0,  1.0, 1.0, 1.0,
		# -1.0,  1.0, -1.0, 0.0, 1.0,
		# -1.0, -1.0, -1.0, 0.0, 0.0,
		# -1.0, -1.0,  1.0, 1.0, 0.0,

		# # right face
		#  1.0,  1.0,  1.0, 0.0, 1.0,
		#  1.0, -1.0, -1.0, 1.0, 0.0,
		#  1.0,  1.0, -1.0, 1.0, 1.0,
		#  1.0,  1.0,  1.0, 0.0, 1.0,
		#  1.0, -1.0,  1.0, 0.0, 0.0,
		#  1.0, -1.0, -1.0, 1.0, 0.0,

		#  # top face
		# -1.0,  1.0, -1.0, 0.0, 1.0,
		#  1.0,  1.0,  1.0, 1.0, 0.0,
		#  1.0,  1.0, -1.0, 1.0, 1.0,
		# -1.0,  1.0, -1.0, 0.0, 1.0,
		# -1.0,  1.0,  1.0, 0.0, 0.0,
		#  1.0,  1.0,  1.0, 1.0, 0.0,

		#  # bottom face
		# -1.0, -1.0,  1.0, 0.0, 1.0,
		#  1.0, -1.0, -1.0, 1.0, 0.0,
		#  1.0, -1.0,  1.0, 1.0, 1.0,
		# -1.0, -1.0,  1.0, 0.0, 1.0,
		# -1.0, -1.0, -1.0, 0.0, 0.0,
		#  1.0, -1.0, -1.0, 1.0, 0.0,
	
        # ], dtype='f4')

        self.mesh = geometry.cube(attr_names=geometry.AttributeNames('in_position', texcoord_0='in_texcoord'))
        # self.vbo = self.ctx.buffer(vertices.tobytes())
        # self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '3f 2f', 'in_position', 'in_texcoord')])
        self.cube_pos = Matrix44.from_translation([0, 0, 0])
        self.start_time = 0.0
        
        # Setup orbit camera params
        self.orbit_center = Vector3([0.0, 0.0, 0.0])
        self.orbit_radius = 5.0
        self.orbit_yaw = -90.0
        self.orbit_pitch = 0.0
        self.cam_up = Vector3([0., 1., 0.])

        # Mouse settings

        self.cam_speed = 2.5 # Camera speed when moving

        # OpenCV webcam
        self.cap = cv2.VideoCapture(0)

    def update_orbit_cam(self):
        yaw_rad = radians(self.orbit_yaw)
        pitch_rad = radians(self.orbit_pitch)

        x = self.orbit_radius * cos(pitch_rad) * sin(yaw_rad)
        y = self.orbit_radius * sin(pitch_rad)
        z = self.orbit_radius * cos(pitch_rad) * cos(yaw_rad)

        self.cam_pos = self.orbit_center + Vector3([x, y, z])
        self.cam_tgt = self.orbit_center

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
        self.update_orbit_cam()

        self.ctx.clear(0.1, 0.1, 0.1)
        self.ctx.enable(self.ctx.DEPTH_TEST)
        
        angle = time * 50
        rotation = Matrix44.from_y_rotation(np.radians(angle))
        model = self.cube_pos * rotation


        view = Matrix44.look_at(
            eye=self.cam_pos,
            target=self.cam_tgt,
            up=self.cam_up
        )

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
        pan_vel = self.orbit_radius * 0.5 * dt
        zoom_vel = 2.0 * dt

        # Orbit cam pan control
        shift = self.wnd.is_key_pressed(keys.LEFT_SHIFT)
        if shift:
            yaw_rad = radians(self.orbit_yaw)
            right = Vector3([cos(yaw_rad + np.pi / 2), 0, sin(yaw_rad + np.pi / 2)])
            up = Vector3([0.0, 1.0, 0.0])

            if self.wnd.is_key_pressed(keys.W):
                self.orbit_center += up * pan_vel
            if self.wnd.is_key_pressed(keys.S):
                self.orbit_center -= up * pan_vel
            if self.wnd.is_key_pressed(keys.A):
                self.orbit_center -= right * pan_vel
            if self.wnd.is_key_pressed(keys.D):
                self.orbit_center += right * pan_vel

        # Orbit cam rotation control
        if self.wnd.is_key_pressed(keys.W):
            self.orbit_pitch += rot_vel
        if self.wnd.is_key_pressed(keys.S):
            self.orbit_pitch -= rot_vel
        if self.wnd.is_key_pressed(keys.A):
            self.orbit_yaw -= rot_vel
        if self.wnd.is_key_pressed(keys.D):
            self.orbit_yaw += rot_vel

        # Clamp pitch to [-89, 89]
        self.orbit_pitch = max(-89.0, min(89.0, self.orbit_pitch))

        # Zoom Controls
        if self.wnd.is_key_pressed(keys.Q):
            self.orbit_radius = max(1.0, self.orbit_radius - zoom_vel)
        if self.wnd.is_key_pressed(keys.E):
            self.orbit_radius += zoom_vel

    def destroy(self):
        # Clean up OpenCV when window closes
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    mglw.run_window_config(Scene)
