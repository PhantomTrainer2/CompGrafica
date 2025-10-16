import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import *

import glm
from camera3d import *
from light import *
from shader import *
from material import *
from transform import *
from node import *
from scene import *
from sphere import * 
from texture import * 
from skybox import *
from variable import *
from engine import Engine

def main():
    # Initialize the library
    if not glfw.init():
        return
    # Create a windowed mode window and its OpenGL context
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR,4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR,1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT,GL_TRUE)
    win = glfw.create_window(960, 720, "Proj2 - Mini Sistema Solar 3D", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.set_key_callback(win,keyboard)

    # Make the window's context current
    glfw.make_context_current(win)
    print("OpenGL version: ",glGetString(GL_VERSION))

    initialize(win)

    # Loop until the user closes the window
    while not glfw.window_should_close(win):
        # Render here, e.g. using pyOpenGL
        display(win)

        # Swap front and back buffers
        glfw.swap_buffers(win)

        # Poll for and process events
        glfw.poll_events()

viewer_pos = glm.vec3(10.0, 8.0, 12.0)

def initialize (win):
  # set background color: white 
  glClearColor(1.0,1.0,1.0,1.0)
  # enable depth test 
  glEnable(GL_DEPTH_TEST)
  # cull back faces
  glEnable(GL_CULL_FACE)  

  # create camera
  global camera, camera_follow, active_camera
  camera = Camera3D(viewer_pos[0],viewer_pos[1],viewer_pos[2])
  arcball = camera.CreateArcball(); arcball.Attach(win)
  camera_follow = Camera3D(0.0,0.0,0.0)
  active_camera = camera

  # light at sun position (eye space)
  light = Light(0.0,0.0,0.0,1.0,"camera")

  # paths
  import os
  script_dir = os.path.dirname(os.path.abspath(__file__))
  shaders_dir = os.path.join(script_dir, '..', 'shaders', 'ilum_vert')
  images_dir = os.path.join(script_dir, '..', 'images')

  # shaders (per-fragment textured with optional normal map)
  sh_tex = Shader(light, "camera")
  sh_tex.AttachVertexShader(os.path.join(shaders_dir, 'vertex_texture.glsl'))
  sh_tex.AttachFragmentShader(os.path.join(shaders_dir, 'fragment_texture.glsl'))
  sh_tex.Link()

  # textures
  tex_sun = Texture("decal", os.path.join(images_dir, 'sun.jpg'))
  tex_earth = Texture("decal", os.path.join(images_dir, 'earthfull.jpg'))
  tex_moon = Texture("decal", os.path.join(images_dir, 'moon.jpeg'))
  tex_venus = Texture("decal", os.path.join(images_dir, 'venus.jpg'))
  tex_space = Texture("decal", os.path.join(images_dir, 'space.jpg'))
  tex_earth_normal = Texture("normalMap", os.path.join(images_dir, 'earth-normal.png'))

  # materials
  sun_mat = Material(5.0, 5.0, 5.0)
  sun_mat.SetDiffuse(0.0,0.0,0.0)
  sun_mat.SetSpecular(0.0,0.0,0.0)
  earth_mat = Material(1.0,1.0,1.0)
  earth_mat.SetSpecular(0.4,0.4,0.4)
  earth_mat.SetShininess(32.0)
  moon_mat = Material(0.9,0.9,0.9)
  moon_mat.SetSpecular(0.2,0.2,0.2)
  moon_mat.SetShininess(8.0)
  venus_mat = Material(1.0,1.0,1.0)
  venus_mat.SetSpecular(0.3,0.3,0.3)
  venus_mat.SetShininess(16.0)

  # shapes
  sphere = Sphere()
  sky = SkyBox()

  # transforms
  global sun_scale, sun_spin
  global earth_orbit, earth_translate, earth_scale, earth_spin
  global venus_orbit, venus_translate, venus_scale, venus_spin
  global moon_orbit, moon_translate, moon_scale
  sun_scale = Transform(); sun_scale.Scale(2.2,2.2,2.2); sun_spin = Transform()
  earth_orbit = Transform(); earth_translate = Transform(); earth_translate.Translate(8.0,0.0,0.0); earth_scale = Transform(); earth_scale.Scale(1.0,1.0,1.0); earth_spin = Transform()
  venus_orbit = Transform(); venus_translate = Transform(); venus_translate.Translate(5.0,0.0,0.0); venus_scale = Transform(); venus_scale.Scale(0.6,0.6,0.6); venus_spin = Transform()
  moon_orbit = Transform(); moon_translate = Transform(); moon_translate.Translate(1.6,0.0,0.0); moon_scale = Transform(); moon_scale.Scale(0.27,0.27,0.27)

  # space background (skybox drawn first)
  space_trf = Transform(); space_trf.Scale(90.0,90.0,90.0)

  # scene graph
  root = Node()

  # skybox node (reuse textured shader but with high ambient and no specular)
  sky_mat = Material(1.0,1.0,1.0)
  sky_mat.SetSpecular(0.0,0.0,0.0)
  sky_node = Node(shader=sh_tex, trf=space_trf, apps=[sky_mat, tex_space,
                    Variable("lamb", glm.vec4(1.0,1.0,1.0,1.0)),
                    Variable("ldif", glm.vec4(0.0,0.0,0.0,1.0)),
                    Variable("lspe", glm.vec4(0.0,0.0,0.0,1.0)),
                    Variable("useNormalMap", 0)
                 ], shps=[sky])
  root.AddNode(sky_node)

  # sun (emissive)
  sun_node = Node(shader=sh_tex, trf=sun_spin, apps=[sun_mat, tex_sun], shps=[sphere])
  sun_scale_node = Node(trf=sun_scale, nodes=[sun_node])

  # moon
  global moon_leaf
  moon_leaf = Node(shader=sh_tex, trf=moon_scale, apps=[moon_mat, tex_moon, Variable("useNormalMap", 0), Variable("debugNormals", 0)], shps=[sphere])
  moon_tr_node = Node(trf=moon_translate, nodes=[moon_leaf])
  moon_orbit_node = Node(trf=moon_orbit, nodes=[moon_tr_node])

  # earth (with normal map)
  global earth_leaf
  earth_leaf = Node(shader=sh_tex, trf=earth_spin, apps=[earth_mat, tex_earth, tex_earth_normal, Variable("useNormalMap", 1), Variable("debugNormals", 0)], shps=[sphere])
  earth_scale_node = Node(trf=earth_scale, nodes=[earth_leaf])
  earth_tr_node = Node(trf=earth_translate, nodes=[earth_scale_node, moon_orbit_node])
  earth_orbit_node = Node(trf=earth_orbit, nodes=[earth_tr_node])

  # venus/mercury
  venus_leaf = Node(shader=sh_tex, trf=venus_spin, apps=[venus_mat, tex_venus, Variable("useNormalMap", 0), Variable("debugNormals", 0)], shps=[sphere])
  venus_scale_node = Node(trf=venus_scale, nodes=[venus_leaf])
  venus_tr_node = Node(trf=venus_translate, nodes=[venus_scale_node])
  venus_orbit_node = Node(trf=venus_orbit, nodes=[venus_tr_node])

  root.AddNode(sun_scale_node)
  root.AddNode(earth_orbit_node)
  root.AddNode(venus_orbit_node)

  # build scene
  global scene 
  scene = Scene(root)

  # engines: animation + camera follow (set in display)
  from luxor.animation import SolarSystemAnimation
  engine = SolarSystemAnimation(earth_orbit, moon_orbit, earth_spin, sun_spin, venus_orbit, venus_spin)
  scene.AddEngine(engine)

  class FollowMoonCameraEngine(Engine):
    def __init__(self):
      self.prev_dir = None
      self.prev_side = None
    def Update(self, time):
      try:
        origin = glm.vec4(0,0,0,1)
        M_earth = earth_orbit.GetMatrix() * earth_translate.GetMatrix()
        earth_pos = glm.vec3(M_earth * origin)
        M_moon = earth_orbit.GetMatrix() * earth_translate.GetMatrix() * moon_orbit.GetMatrix() * moon_translate.GetMatrix()
        moon_pos = glm.vec3(M_moon * origin)

        cam_dir_raw = glm.normalize(moon_pos - earth_pos)
        # smooth cam direction a bit to avoid jitter
        if self.prev_dir is None:
          cam_dir = cam_dir_raw
        else:
          beta = 0.12
          cam_dir = glm.normalize(self.prev_dir * (1.0 - beta) + cam_dir_raw * beta)
        world_up = glm.vec3(0.0, 1.0, 0.0)

        # Parallel-transport previous side to new direction to avoid roll flips
        if self.prev_side is None:
          side = glm.cross(world_up, cam_dir)
          if glm.length(side) < 1e-5:
            side = glm.cross(glm.vec3(1.0,0.0,0.0), cam_dir)
          side = glm.normalize(side)
        else:
          # project previous side onto plane orthogonal to cam_dir
          side = self.prev_side - cam_dir * glm.dot(self.prev_side, cam_dir)
          if glm.length(side) < 1e-5:
            side = glm.cross(world_up, cam_dir)
            if glm.length(side) < 1e-5:
              side = glm.cross(glm.vec3(1.0,0.0,0.0), cam_dir)
          side = glm.normalize(side)
        up = glm.normalize(glm.cross(cam_dir, side))
        # store for next frame
        self.prev_dir = cam_dir
        self.prev_side = side
        earth_radius = 1.0
        moon_radius = 0.27
        # keep safe distance from Moon to avoid entering its surface
        moon_dist = glm.length(moon_pos - earth_pos)
        safety = moon_radius * 2.0
        earth_offset = earth_radius * 1.6
        # never exceed the safe distance to Moon along the line of sight
        along = min(earth_offset, max(0.0, moon_dist - safety))
        cam_eye = earth_pos + cam_dir * along + up * (earth_radius * 0.2)
        # enforce safety after adding vertical offset
        v_eye_moon = moon_pos - cam_eye
        dist_eye_moon = glm.length(v_eye_moon)
        if dist_eye_moon < safety and dist_eye_moon > 1e-4:
          push_back = (safety - dist_eye_moon) * (1.0 + 1e-3)
          cam_eye -= cam_dir * push_back
        camera_follow.SetEye(cam_eye.x, cam_eye.y, cam_eye.z)
        camera_follow.SetCenter(moon_pos.x, moon_pos.y, moon_pos.z)
        camera_follow.SetUpDir(up.x, up.y, up.z)
        # fixed FOV to avoid jitter
        camera_follow.SetAngle(90.0)
      except Exception:
        pass

  scene.AddEngine(FollowMoonCameraEngine())

def display (win):
  global scene
  global camera
  global camera_follow
  global active_camera
  global paused
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) 
  # advance animation engines
  current_time = glfw.get_time()
  if not paused:
    for e in scene.engines:
      e.Update(current_time)
  # render
  scene.Render(active_camera)

def keyboard (win, key, scancode, action, mods):
   global active_camera
   global earth_leaf, moon_leaf, venus_leaf
   global paused
   if key == glfw.KEY_Q and action == glfw.PRESS:
      glfw.set_window_should_close(win,glfw.TRUE)
   if key == glfw.KEY_C and action == glfw.PRESS:
      # toggle camera
      active_camera = camera if active_camera is not camera else camera_follow
   # toggle pause (P)
   if key == glfw.KEY_P and action == glfw.PRESS:
      paused = not paused
   # toggle debug normals (N)
   if key == glfw.KEY_N and action == glfw.PRESS:
      try:
        for node in [earth_leaf, moon_leaf, venus_leaf]:
          if not node: continue
          found = False
          for i, app in enumerate(node.apps):
            if isinstance(app, Variable) and app.name == "debugNormals":
              val = 0 if app.value == 1 else 1
              node.apps[i] = Variable("debugNormals", val)
              found = True
              break
          if not found:
            node.apps.append(Variable("debugNormals", 1))
      except Exception:
        pass
   # toggle normal map on earth (B)
   if key == glfw.KEY_B and action == glfw.PRESS:
      try:
        found = False
        for i, app in enumerate(earth_leaf.apps):
          if isinstance(app, Variable) and app.name == "useNormalMap":
            val = 0 if app.value == 1 else 1
            earth_leaf.apps[i] = Variable("useNormalMap", val)
            found = True
            break
        if not found:
          earth_leaf.apps.append(Variable("useNormalMap", 1))
      except Exception:
        pass

active_camera = None
paused = False

if __name__ == "__main__":
    active_camera = None
    main()
