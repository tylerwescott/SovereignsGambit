class Card:
    def __init__(self, name, strength, image, pawn_placement, placement_cost,
                 power_up_positions=None, power_up_value=0,
                 power_down_positions=None, power_down_value=0,
                 generate_card_when_played=False, generated_card_when_played=None):
        self.name = name
        self.strength = strength
        self.image = image
        self.pawn_placement = pawn_placement
        self.placement_cost = placement_cost
        self.power_up_positions = power_up_positions if power_up_positions is not None else []
        self.power_up_value = power_up_value
        self.power_down_positions = power_down_positions if power_down_positions is not None else []
        self.power_down_value = power_down_value
        self.generate_card_when_played = generate_card_when_played
        self.generated_card_when_played = generated_card_when_played
