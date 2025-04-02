import cv2
import numpy as np
import moderngl_window as mglw
from moderngl_window import WindowConfig

class OpenCVControlledApp(WindowConfig):
    title = "OpenCV + ModernGL"
    window_size = (512, 512)
    gl_version = (3, 3)
    aspect_ratio = 1.6
    resizable = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # OpenCV webcam
        self.cap = cv2.VideoCapture(0)
        self.scale = 1.0
        self.prog = self.ctx.program(
            vertex_shader="""
            #version 330

            in vec2 in_vert;
            in vec3 in_color;
            
            out vec3 v_color;

            void main() {
                v_color = in_color;
                gl_Position = vec4(in_vert, 0.0, 1.0);
            }
        """,
            fragment_shader="""
            #version 330

            in vec3 v_color;

            out vec3 f_color;

            void main() {
                f_color = v_color;
            }
        """,
        )

        vertices = np.array([
            -0.75, -0.75, 1, 0, 0,
             0.75, -0.75, 0, 1, 0,
             0.0,  0.649, 0, 0, 1
        ], dtype='f4')

        vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, vbo, 'in_vert', 'in_color')

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
        self.vao.render()

    def destroy(self):
        # Clean up OpenCV when window closes
        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    mglw.run_window_config(OpenCVControlledApp)
