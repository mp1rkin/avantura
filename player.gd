extends CharacterBody2D

const MOVE_SPEED = 300.0
const JUMP_VELOCITY = -750.0
const MAX_JUMP_CHARGE = 0.8
const MIN_JUMP_CHARGE = 0.15

var gravity = ProjectSettings.get_setting("physics/2d/default_gravity")
var jump_charge_time = 0.0
var is_charging_jump = false

@onready var animated_sprite = $AnimatedSprite2D

func _physics_process(delta):
	if not is_on_floor():
		velocity.y += gravity * delta

	var direction = Input.get_axis("move_left", "move_right")

	if is_on_floor():
		if Input.is_action_pressed("jump"):
			is_charging_jump = true
			jump_charge_time = min(jump_charge_time + delta, MAX_JUMP_CHARGE)
			velocity.x = 0
			animated_sprite.play("idle")
		elif Input.is_action_just_released("jump") and is_charging_jump:
			var charge_factor = clamp(jump_charge_time / MAX_JUMP_CHARGE, MIN_JUMP_CHARGE / MAX_JUMP_CHARGE, 1.0)
			velocity.y = JUMP_VELOCITY * charge_factor
			velocity.x = direction * MOVE_SPEED * charge_factor
			is_charging_jump = false
			jump_charge_time = 0.0
		else:
			is_charging_jump = false
			jump_charge_time = 0.0

			if direction != 0:
				velocity.x = direction * MOVE_SPEED
				animated_sprite.play("run")
				animated_sprite.flip_h = direction < 0
			else:
				velocity.x = move_toward(velocity.x, 0, MOVE_SPEED)
				animated_sprite.play("idle")
	else:
		animated_sprite.play("idle")

	move_and_slide()
