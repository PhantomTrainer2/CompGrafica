import sys
from OpenGL.GL import *
from OpenGL.GLUT import *
import glm

# Importa as classes do grafo de cena
from camera3d import Camera3D
from eyelight import EyeLight
from scene import Scene
from node import Node
from cube import Cube
from sphere import Sphere
from material import Material
from appearance import Appearance
from shader import Shader

# Variáveis globais
camera = None
arcball = None
light = None
scene = None
mouse_button = None
mouse_x = 0
mouse_y = 0

def create_materials():
    """Cria diferentes materiais para os objetos"""
    materials = {}
    
    # Material vermelho
    mat_red = Material()
    mat_red.SetAmbient(0.3, 0.0, 0.0, 1.0)
    mat_red.SetDiffuse(0.8, 0.1, 0.1, 1.0)
    mat_red.SetSpecular(1.0, 1.0, 1.0, 1.0)
    mat_red.SetShininess(32.0)
    materials['red'] = mat_red
    
    # Material verde
    mat_green = Material()
    mat_green.SetAmbient(0.0, 0.3, 0.0, 1.0)
    mat_green.SetDiffuse(0.1, 0.8, 0.1, 1.0)
    mat_green.SetSpecular(1.0, 1.0, 1.0, 1.0)
    mat_green.SetShininess(32.0)
    materials['green'] = mat_green
    
    # Material azul
    mat_blue = Material()
    mat_blue.SetAmbient(0.0, 0.0, 0.3, 1.0)
    mat_blue.SetDiffuse(0.1, 0.1, 0.8, 1.0)
    mat_blue.SetSpecular(1.0, 1.0, 1.0, 1.0)
    mat_blue.SetShininess(32.0)
    materials['blue'] = mat_blue
    
    # Material amarelo
    mat_yellow = Material()
    mat_yellow.SetAmbient(0.3, 0.3, 0.0, 1.0)
    mat_yellow.SetDiffuse(0.9, 0.9, 0.1, 1.0)
    mat_yellow.SetSpecular(1.0, 1.0, 1.0, 1.0)
    mat_yellow.SetShininess(64.0)
    materials['yellow'] = mat_yellow
    
    # Material ciano
    mat_cyan = Material()
    mat_cyan.SetAmbient(0.0, 0.3, 0.3, 1.0)
    mat_cyan.SetDiffuse(0.1, 0.8, 0.8, 1.0)
    mat_cyan.SetSpecular(1.0, 1.0, 1.0, 1.0)
    mat_cyan.SetShininess(64.0)
    materials['cyan'] = mat_cyan
    
    # Material magenta
    mat_magenta = Material()
    mat_magenta.SetAmbient(0.3, 0.0, 0.3, 1.0)
    mat_magenta.SetDiffuse(0.8, 0.1, 0.8, 1.0)
    mat_magenta.SetSpecular(1.0, 1.0, 1.0, 1.0)
    mat_magenta.SetShininess(64.0)
    materials['magenta'] = mat_magenta
    
    return materials

def create_scene_objects(materials, shader):
    """Cria a cena com cubos e esferas"""
    global scene
    scene = Scene()
    
    # Esfera central grande (amarela)
    sphere_center = Node()
    sphere_center.SetScale(2, 2, 2)
    sphere_center.SetShape(Sphere())
    sphere_center.SetAppearance(Appearance(materials['yellow'], shader))
    scene.Add(sphere_center)
    
    # Cubos ao redor (4 cubos)
    cube_positions = [
        (-4, 2, 0, 'red'),      # Esquerda superior
        (4, 2, 0, 'green'),     # Direita superior
        (-4, -2, 0, 'blue'),    # Esquerda inferior
        (4, -2, 0, 'cyan'),     # Direita inferior
    ]
    
    for pos_x, pos_y, pos_z, color in cube_positions:
        cube = Node()
        cube.SetPosition(pos_x, pos_y, pos_z)
        cube.SetScale(1.5, 1.5, 1.5)
        cube.SetShape(Cube())
        cube.SetAppearance(Appearance(materials[color], shader))
        scene.Add(cube)
    
    # Esferas menores (4 esferas)
    sphere_positions = [
        (0, 4, 2, 'magenta'),
        (0, -4, 2, 'cyan'),
        (-6, 0, -2, 'green'),
        (6, 0, -2, 'red'),
    ]
    
    for pos_x, pos_y, pos_z, color in sphere_positions:
        sphere = Node()
        sphere.SetPosition(pos_x, pos_y, pos_z)
        sphere.SetScale(1.2, 1.2, 1.2)
        sphere.SetShape(Sphere())
        sphere.SetAppearance(Appearance(materials[color], shader))
        scene.Add(sphere)
    
    # Cubo no fundo
    cube_back = Node()
    cube_back.SetPosition(0, 0, -5)
    cube_back.SetScale(2, 2, 2)
    cube_back.SetShape(Cube())
    cube_back.SetAppearance(Appearance(materials['blue'], shader))
    scene.Add(cube_back)

def display():
    """Função de renderização"""
    global camera, light, scene
    
    # Limpa buffers
    glClearColor(0.1, 0.1, 0.15, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Desenha a cena
    scene.Draw(camera, light)
    
    # Troca buffers
    glutSwapBuffers()

def reshape(width, height):
    """Callback de redimensionamento"""
    glViewport(0, 0, width, height)
    glutPostRedisplay()

def mouse(button, state, x, y):
    """Callback de mouse"""
    global mouse_button, mouse_x, mouse_y, arcball
    
    mouse_button = button
    mouse_x = x
    mouse_y = y
    
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            arcball.StartDrag(x, y)
        else:
            arcball.EndDrag()
            
    glutPostRedisplay()

def motion(x, y):
    """Callback de movimento do mouse"""
    global mouse_button, mouse_x, mouse_y, arcball
    
    if mouse_button == GLUT_LEFT_BUTTON:
        arcball.Drag(x, y)
        glutPostRedisplay()
        
    mouse_x = x
    mouse_y = y

def keyboard(key, x, y):
    """Callback de teclado"""
    global arcball
    
    if key == b'\x1b':  # ESC
        sys.exit(0)
    elif key == b'r' or key == b'R':
        # Reset da câmera
        arcball.Reset()
        glutPostRedisplay()

def init():
    """Inicialização"""
    global camera, arcball, light
    
    # Habilita depth test
    glEnable(GL_DEPTH_TEST)
    
    # Configura a câmera
    camera = Camera3D(0, 0, 15)
    camera.SetCenter(0, 0, 0)
    camera.SetAngle(45)
    camera.SetZPlanes(0.1, 1000)
    
    # Cria arcball
    arcball = camera.CreateArcball()
    
    # Configura a luz
    light = EyeLight(5, 5, 5, 1)  # Luz pontual
    light.SetAmbient(0.2, 0.2, 0.2, 1.0)
    light.SetDiffuse(0.8, 0.8, 0.8, 1.0)
    light.SetSpecular(1.0, 1.0, 1.0, 1.0)
    
    # Cria os shaders para iluminação por fragmento
    shader = Shader('shaders/ilum_vert/vertex.glsl', 
                    'shaders/ilum_vert/fragment.glsl')
    
    # Cria os materiais e objetos da cena
    materials = create_materials()
    create_scene_objects(materials, shader)

def main():
    """Função principal"""
    # Inicializa GLUT
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Tarefa 2.1 - Cena 3D com Iluminacao por Fragmento")
    
    # Inicializa a cena
    init()
    
    # Configura callbacks
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    
    # Mensagem de instruções
    print("=" * 50)
    print("Tarefa 2.1 - Cena 3D com Iluminacao por Fragmento")
    print("=" * 50)
    print("Controles:")
    print("  - Arraste com o botao esquerdo: Rotacionar camera (arcball)")
    print("  - Tecla 'R': Resetar camera")
    print("  - Tecla 'ESC': Sair")
    print("=" * 50)
    
    # Loop principal
    glutMainLoop()

if __name__ == "__main__":
    main()