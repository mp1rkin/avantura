extends Node2D

@onready var victory_label = $UI/VictoryLabel

func _on_finish_point_body_entered(body):
	if body.name == "Player":
		victory_label.visible = true
		get_tree().paused = true
