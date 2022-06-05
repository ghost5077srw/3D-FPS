from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import lit_with_shadows_shader

app = Ursina()


window.fps_counter.enabled=False
window.exit_button.enabled=True



random.seed(0)

lable = Text(text='Pause / Map', scale=3, x=-0.85,
             y=0.45,visible=False ,color=rgb(255, 48, 33))


Entity.default_shader = lit_with_shadows_shader

ground = Entity(model='plane', collider='box', scale=64,
                texture='grass', texture_scale=(4,4))

editor_camera = EditorCamera(enabled=False, ignore_paused=True)
player = FirstPersonController(origin_y=-.5, speed=5, origin_x = 6)
player.collider = BoxCollider(player, Vec3(0,1,0), Vec3(1,2,1))


player.cursor.color = color.white
player.cursor.texture='assets\\scope'
player.cursor.scale=(0.1)
player.cursor.rotation_z = (90)

gun = Entity(model='assets/M1', parent=camera, position=(.5,-.25,.45),
             scale=(0.07),rotation_y=190, origin_z=2.5, texture='assets/M1',
             on_cooldown=False,collider='mesh')

gun.muzzle_flash = Entity(parent=gun, z=1, world_scale=.5, model='quad',
                          color=color.yellow, enabled=False)

shootables_parent = Entity()
mouse.traverse_target = shootables_parent


for i in range(16):
    Entity(model='cube', origin_y=-.5, scale=2, texture='box', texture_scale=(1,2),
        x=random.uniform(-8,8),
        z=random.uniform(-8,8) + 8,
        collider='mesh',
        scale_y = random.uniform(2,3),
        )

def update():
    if held_keys['right mouse']:
        shoot()

def shoot():
    if not gun.on_cooldown:
        # print('shoot')
        gun.on_cooldown = True
        gun.muzzle_flash.enabled=True
        from ursina.prefabs.ursfx import ursfx
        ursfx([(0.0, 0.0), (0.1, 0.9), (0.15, 0.75), (0.3, 0.14), (0.6, 0.0)],
              volume=0.5, wave='noise', pitch=random.uniform(-13,-12),
              pitch_change=-12, speed=3.0)

        invoke(gun.muzzle_flash.disable, delay=.05)
        invoke(setattr, gun, 'on_cooldown', False, delay=.15)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 10
            mouse.hovered_entity.blink(color.red)


from ursina.prefabs.health_bar import HealthBar

class Enemy(Entity):
    def __init__(self, **kwargs):
        super().__init__(parent=shootables_parent, model='assets\man\man.fbx',
                         scale=0.1,double_sided=True, origin_y=-.5,
                         texture='assets\man\orc', collider='mesh', **kwargs)

        self.health_bar = Entity(parent=self, y=18, model='cube', color=color.red,
                                 world_scale=(1.5,.1,.1))
        self.max_hp = 100
        self.hp = self.max_hp

    def update(self):

        dist = distance_xz(player.position, self.position)
        if dist > 40:
            return

        self.health_bar.alpha = max(0, self.health_bar.alpha - time.dt)


        self.look_at_2d(player.position, 'y')
        hit_info = raycast(self.world_position + Vec3(0,1,0), self.forward, 30, ignore=(self,))
        if hit_info.entity == player:
            if dist > 2:
                self.position += self.forward * time.dt * 19

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value
        if value <= 0:
            destroy(self)
            player.cursor.color = color.white
            player.cursor.shake(duration=0.8)

            return
        if value <= 10:
            player.cursor.color = color.red
            return
        else:
            player.cursor.color = color.white


        self.health_bar.world_scale_x = self.hp / self.max_hp * 1.5
        self.health_bar.alpha = 1

# Enemy()
enemies = [Enemy(x=x*4) for x in range(4)]


def pause_input(key):
    if key == 'tab':    # press tab to toggle edit/play mode
        editor_camera.enabled = not editor_camera.enabled
        lable.visible = not lable.visible

        player.visible_self = editor_camera.enabled
        player.cursor.enabled = not editor_camera.enabled
        gun.enabled = not editor_camera.enabled
        mouse.locked = not editor_camera.enabled
        editor_camera.position = player.position

        application.paused = editor_camera.enabled
    if key == 'right mouse down':
        gun.position=(.5,-.24,.40)
        player.cursor.shake(duration=0.3)
    else:
        gun.position = (.5, -.25, .45)



pause_handler = Entity(ignore_paused=True, input=pause_input)


sun = DirectionalLight()
sun.look_at(Vec3(1,-1,-1))
Sky(texture='assets\skybox')

app.run()