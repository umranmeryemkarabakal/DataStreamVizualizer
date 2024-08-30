from PyQt5.QtGui import QOpenGLWindow
from OpenGL import GL, GLU
from stl import mesh
from global_functions import *
import global_variables as gv

class GLWidget(QOpenGLWindow):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)

        stl_path = "model.stl"
        stl_model = mesh.Mesh.from_file(stl_path)

        self.vectors = stl_model.vectors
        self.normals = stl_model.normals

        self.yaw_list = []
        self.pitch_list = []
        self.roll_list = []

        self.current_yaw = 0.0
        self.current_pitch = 0.0
        self.current_roll = 0.0

        self.t = 0.0

    def updateRotasyon(self):
        global Yaw,Pitch,Roll

        
        """
        Yaw = normalize_angle(Yaw)
        Pitch = normalize_angle(Pitch)
        Roll = normalize_angle(Roll)
        """
        
        self.t += 0.001
        self.t = min(self.t,1.0)
        
        if filter_outliers(Pitch,Yaw,Roll):
            
            self.roll_list.append(Roll)
            self.pitch_list.append(Pitch)
            self.yaw_list.append(Yaw)
        

        self.roll_list.append(Roll)
        self.pitch_list.append(Pitch)
        self.yaw_list.append(Yaw)

        if self.yaw_list:
            self.current_yaw = self.yaw_list[-1]
            self.current_pitch = self.pitch_list[-1]
            self.current_roll = self.roll_list[-1]
            
        self.current_yaw = lerp(self.current_yaw, Yaw, self.t)
        self.current_roll = lerp(self.current_roll, Roll, self.t)
        self.current_pitch = lerp(self.current_pitch, Pitch, self.t)

    def initializeGL(self):
        GL.glClearColor(1,1,1,1)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        if height == 0:
            height = 1

        GL.glViewport(0, 0, width, height)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()

        GLU.gluPerspective(45.0, width / float(height), 1.0, 500.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GLU.gluLookAt(0.0, 0.0, 10.0,  
                    0.0, 0.0, 0.0,   
                    0.0, 1.0, 0.0)

    def paintGL(self):
        global Roll, Pitch, Yaw

        self.updateRotasyon()

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glPushMatrix()

        GL.glTranslatef(0.0, 0.0, -250.0)
        
        GL.glRotatef(round(self.current_pitch), 0.0, 0.0, 1.0)
        GL.glRotatef(round(self.current_yaw), 0.0, 1.0, 0.0)
        GL.glRotatef(round(self.current_roll), 1.0, 0.0, 0.0)
        
        """
        GL.glRotatef(roll, 1.0, 0.0, 0.0)
        GL.glRotatef(pitch, 0.0, 1.0, 0.0)
        GL.glRotatef(yaw, 0.0, 0.0, 1.0)
        """

        GL.glLineWidth(2.0)
        GL.glBegin(GL.GL_LINES)
        # X Ekseni
        GL.glColor3f(0.278,0.302,0.318)
        GL.glVertex3f(-200.0, 0.0, 0.0)
        GL.glVertex3f(200.0, 0.0, 0.0)
        # Y Ekseni
        GL.glColor3f(0.278,0.302,0.318) 
        GL.glVertex3f(0.0, -200.0, 0.0)
        GL.glVertex3f(0.0, 200.0, 0.0)
        # Z Ekseni
        GL.glColor3f(0.278,0.302,0.318)
        GL.glVertex3f(0.0, 0.0, -200.0)
        GL.glVertex3f(0.0, 0.0, 200.0)
        GL.glEnd()

        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)

        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.0, 0.4, 0.5) 
        for triangle in self.vectors:
            for vertex in triangle:
                GL.glVertex3fv(vertex)
        GL.glEnd()

        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

        GL.glLineWidth(1.0)
        GL.glBegin(GL.GL_TRIANGLES)
        GL.glColor3f(0.01960784313, 0.27058823529, 0.41176470588)
        for triangle in self.vectors:
            for vertex in triangle:
                GL.glVertex3fv(vertex)
        GL.glEnd()

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)

        GL.glPopMatrix()
