import numpy as np
import random
import skfuzzy as fuzz
from skfuzzy import control as ctrl

'''Fuzzy logic system for a fruit sweetness comparison game.'''

def generate_sweetness_game_question():
    '''Generates a question for a fruit sweetness comparison game.'''

    fruit_sweetness_values = {
        "acerolas": 9, "apples": 6, "apricots": 7, "avocados": 2, "bananas": 8,
        "blackberries": 7, "blueberries": 6, "cantaloupes": 8, "cherries": 7, "coconuts": 4,
        "figs": 8, "grapefruits": 4, "grapes": 7, "guava": 8, "kiwifruit": 6,
        "lemons": 2, "limes": 2, "mangos": 9, "olives": 1, "oranges": 7,
        "passionfruit": 8, "peaches": 7, "pears": 6, "pineapples": 8, "plums": 6,
        "pomegranates": 7, "raspberries": 6, "strawberries": 8, "tomatoes": 3, "watermelons": 8
    }

    quantity_input = ctrl.Antecedent(np.arange(0, 4, 1), 'quantity')
    base_sweetness_input = ctrl.Antecedent(np.arange(0, 11, 1), 'base_sweetness')
    total_sweetness_output = ctrl.Consequent(np.arange(0, 31, 1), 'total_sweetness')

    quantity_input['low'] = fuzz.trimf(quantity_input.universe, [0, 1, 2])
    quantity_input['medium'] = fuzz.trimf(quantity_input.universe, [1, 2, 3])
    quantity_input['high'] = fuzz.trimf(quantity_input.universe, [2, 3, 3])

    base_sweetness_input['low'] = fuzz.trimf(base_sweetness_input.universe, [0, 3, 5])
    base_sweetness_input['medium'] = fuzz.trimf(base_sweetness_input.universe, [4, 6, 8])
    base_sweetness_input['high'] = fuzz.trimf(base_sweetness_input.universe, [7, 9, 10])

    total_sweetness_output['low'] = fuzz.trimf(total_sweetness_output.universe, [0, 8, 15])
    total_sweetness_output['moderate'] = fuzz.trimf(total_sweetness_output.universe, [10, 17, 23])
    total_sweetness_output['high'] = fuzz.trimf(total_sweetness_output.universe, [18, 25, 30])

    fuzzy_rules = [
        ctrl.Rule(quantity_input['low'] & base_sweetness_input['low'], total_sweetness_output['low']),
        ctrl.Rule(quantity_input['low'] & base_sweetness_input['medium'], total_sweetness_output['low']),
        ctrl.Rule(quantity_input['low'] & base_sweetness_input['high'], total_sweetness_output['moderate']),
        ctrl.Rule(quantity_input['medium'] & base_sweetness_input['low'], total_sweetness_output['low']),
        ctrl.Rule(quantity_input['medium'] & base_sweetness_input['medium'], total_sweetness_output['moderate']),
        ctrl.Rule(quantity_input['medium'] & base_sweetness_input['high'], total_sweetness_output['high']),
        ctrl.Rule(quantity_input['high'] & base_sweetness_input['low'], total_sweetness_output['moderate']),
        ctrl.Rule(quantity_input['high'] & base_sweetness_input['medium'], total_sweetness_output['high']),
        ctrl.Rule(quantity_input['high'] & base_sweetness_input['high'], total_sweetness_output['high'])
    ]

    fuzzy_sweetness_system = ctrl.ControlSystem(fuzzy_rules)
    sweetness_simulation = ctrl.ControlSystemSimulation(fuzzy_sweetness_system)

    def compute_total_sweetness(fruit_quantity, fruit_base_sweetness):
        '''Computes the total sweetness using a fuzzy logic system.'''

        sweetness_simulation.input['quantity'] = fruit_quantity
        sweetness_simulation.input['base_sweetness'] = fruit_base_sweetness
        sweetness_simulation.compute()
        return sweetness_simulation.output['total_sweetness']

    fruit_name_1 = random.choice(list(fruit_sweetness_values.keys()))
    fruit_quantity_1 = random.randint(1, 3)
    fruit_is_ripe_1 = random.random() < 0.8
    fruit_base_sweetness_1 = fruit_sweetness_values[fruit_name_1] * (1 if fruit_is_ripe_1 else 0.9)
    fruit_total_sweetness_1 = compute_total_sweetness(fruit_quantity_1, fruit_base_sweetness_1)
    fruit_description_1 = f"{fruit_quantity_1} {fruit_name_1}" + ("" if fruit_is_ripe_1 else " (unripe)")

    fruit_name_2 = random.choice(list(fruit_sweetness_values.keys()))
    fruit_quantity_2 = random.randint(1, 3)
    fruit_is_ripe_2 = random.random() < 0.8
    fruit_base_sweetness_2 = fruit_sweetness_values[fruit_name_2] * (1 if fruit_is_ripe_2 else 0.9)
    fruit_total_sweetness_2 = compute_total_sweetness(fruit_quantity_2, fruit_base_sweetness_2)
    fruit_description_2 = f"{fruit_quantity_2} {fruit_name_2}" + ("" if fruit_is_ripe_2 else " (unripe)")

    if abs(fruit_total_sweetness_1 - fruit_total_sweetness_2) < 0.5:
        correct_answer = "equal"
    else:
        correct_answer = "1" if fruit_total_sweetness_1 > fruit_total_sweetness_2 else "2"

    question_text = (
        f"Which is sweeter?\n"
        f"1. {fruit_description_1}\n"
        f"2. {fruit_description_2}\n"
        f"Just type 1 or 2."
    )

    return {
        "question": question_text,
        "correct": correct_answer,
        "overall1": fruit_total_sweetness_1,
        "overall2": fruit_total_sweetness_2
    }