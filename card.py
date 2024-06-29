class Card:
    def __init__(self, name, placement_cost, image, pawn_placement, strength, power_up_positions=None, power_up_value=0):
        self.name = name
        self.placement_cost = placement_cost
        self.image = image
        self.pawn_placement = pawn_placement
        self.strength = strength
        self.power_up_positions = power_up_positions or []
        self.power_up_value = power_up_value
