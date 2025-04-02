import cv2
import numpy as np
import moderngl_window as mglw
from pyrr import Matrix44
from moderngl_window import WindowConfig
from pathlib import Path


# pip install moderngl moderngl_window pywavefront


class OpenCVControlledApp(WindowConfig):
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

        vertices = np.array([
		# x, y, z, u, v

		# front face
		-1.0,  1.0,  1.0, 0.0, 1.0,
		 1.0, -1.0,  1.0, 1.0, 0.0,
		 1.0,  1.0,  1.0, 1.0, 1.0,
		-1.0,  1.0,  1.0, 0.0, 1.0,
		-1.0, -1.0,  1.0, 0.0, 0.0,
		 1.0, -1.0,  1.0, 1.0, 0.0,

		# back face
		-1.0,  1.0, -1.0, 0.0, 1.0,
		 1.0, -1.0, -1.0, 1.0, 0.0,
		 1.0,  1.0, -1.0, 1.0, 1.0,
		-1.0,  1.0, -1.0, 0.0, 1.0,
		-1.0, -1.0, -1.0, 0.0, 0.0,
		 1.0, -1.0, -1.0, 1.0, 0.0,

		# left face
		-1.0,  1.0, -1.0, 0.0, 1.0,
		-1.0, -1.0,  1.0, 1.0, 0.0,
		-1.0,  1.0,  1.0, 1.0, 1.0,
		-1.0,  1.0, -1.0, 0.0, 1.0,
		-1.0, -1.0, -1.0, 0.0, 0.0,
		-1.0, -1.0,  1.0, 1.0, 0.0,

		# right face
		 1.0,  1.0,  1.0, 0.0, 1.0,
		 1.0, -1.0, -1.0, 1.0, 0.0,
		 1.0,  1.0, -1.0, 1.0, 1.0,
		 1.0,  1.0,  1.0, 0.0, 1.0,
		 1.0, -1.0,  1.0, 0.0, 0.0,
		 1.0, -1.0, -1.0, 1.0, 0.0,

		 # top face
		-1.0,  1.0, -1.0, 0.0, 1.0,
		 1.0,  1.0,  1.0, 1.0, 0.0,
		 1.0,  1.0, -1.0, 1.0, 1.0,
		-1.0,  1.0, -1.0, 0.0, 1.0,
		-1.0,  1.0,  1.0, 0.0, 0.0,
		 1.0,  1.0,  1.0, 1.0, 0.0,

		 # bottom face
		-1.0, -1.0,  1.0, 0.0, 1.0,
		 1.0, -1.0, -1.0, 1.0, 0.0,
		 1.0, -1.0,  1.0, 1.0, 1.0,
		-1.0, -1.0,  1.0, 0.0, 1.0,
		-1.0, -1.0, -1.0, 0.0, 0.0,
		 1.0, -1.0, -1.0, 1.0, 0.0,
	
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [(self.vbo, '3f 2f', 'in_position', 'in_texcoord')])
        self.cube_pos = Matrix44.from_translation([0, 0, -5])
        self.start_time = 0.0
        

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
        
        
        self.ctx.clear(0.0, 0.0, 0.0)
        self.ctx.enable(self.ctx.DEPTH_TEST)
        
        angle = time * 50
        rotation = Matrix44.from_y_rotation(np.radians(angle))
        model = self.cube_pos * rotation

        view = Matrix44.look_at(
            eye=[0, 0, 0],
            target=[0, 0, -1],
            up=[0, 1, 0]
        )

        proj = Matrix44.perspective_projection(
            fovy=45.0,
            aspect=self.wnd.aspect_ratio,
            near=0.1,
            far=100.0
        )


        self.prog['model'].write(model.astype('f4').tobytes())
        self.prog['view'].write(view.astype('f4').tobytes())
        self.prog['proj'].write(proj.astype('f4').tobytes())
        self.prog["Texture"] = 0
        
        self.vao.render()
        
        # self.mesh.render()

    def destroy(self):
        # Clean up OpenCV when window closes
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    mglw.run_window_config(OpenCVControlledApp)
