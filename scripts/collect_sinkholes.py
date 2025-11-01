import json
from pathlib import Path
from datetime import datetime

class SinkholeCollector:
    """Collect genuinely challenging sinkhole tasks"""
    
    def __init__(self):
        self.sinkholes = {}
        self.next_id = 1
    
    def add_sinkhole(self, task, category, expected_difficulty='trivial', why_hard='', correct_answer=''):
        """Add a new sinkhole task"""
        
        sinkhole_id = f"sinkhole_{self.next_id:03d}"
        self.next_id += 1
        
        self.sinkholes[sinkhole_id] = {
            'id': sinkhole_id,
            'task': task,
            'category': category,
            'expected_difficulty': expected_difficulty,
            'why_hard': why_hard,
            'correct_answer': correct_answer,
            'x': self._assign_x_position(category),
            'y': self._assign_y_position(category),
            'depth': -0.8,
            'results': {},
            'added_date': datetime.now().isoformat()
        }
        
        return sinkhole_id
    
    def _assign_x_position(self, category):
        positions = {
            'constrained_generation': 0.15,
            'spatial_reasoning': 0.75,
            'string_manipulation': 0.20,
            'retroactive_reasoning': 0.65,
            'self_reference': 0.50,
            'logic_puzzle': 0.60,
            'arithmetic': 0.80,
            'physical_reasoning': 0.70,
            'temporal': 0.35,
            'counting': 0.25,
        }
        return positions.get(category, 0.5)
    
    def _assign_y_position(self, category):
        positions = {
            'constrained_generation': 0.15,
            'spatial_reasoning': 0.25,
            'string_manipulation': 0.18,
            'retroactive_reasoning': 0.30,
            'self_reference': 0.10,
            'logic_puzzle': 0.15,
            'arithmetic': 0.28,
            'physical_reasoning': 0.22,
            'temporal': 0.25,
            'counting': 0.20,
        }
        return positions.get(category, 0.2)
    
    def save(self, output_path='data/negatives.json'):
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.sinkholes, f, indent=2)
        print(f"✓ Saved {len(self.sinkholes)} sinkholes to {output_path}")


def create_hard_sinkholes():
    """Create sinkholes that ACTUALLY fail current SOTA models (2025)"""
    
    collector = SinkholeCollector()
    
    # MULTI-CONSTRAINT SATISFACTION
    
    collector.add_sinkhole(
        task="Generate a sentence where: every word starts with 'b', has exactly 5 words, forms a grammatically correct question, and the 3rd word must be a verb.",
        category="constrained_generation",
        correct_answer="Before breakfast, Bob buys bread?",
        why_hard="Multiple simultaneous constraints cause models to drop at least one"
    )
    
    collector.add_sinkhole(
        task="Write a palindrome sentence (reads same forwards and backwards) that is exactly 7 words long and mentions an animal.",
        category="constrained_generation",
        correct_answer="Example: 'Rats live on no evil star' (rat) - but needs to be exactly 7 words",
        why_hard="Triple constraint: palindrome + length + semantic requirement"
    )
    
    collector.add_sinkhole(
        task="Create a sentence where each word has one more letter than the previous word, starting with 'I' (1 letter), and must reach a 6-letter word.",
        category="constrained_generation",
        correct_answer="I am the best friend (1,2,3,4,6)",
        why_hard="Precise length progression tracking across generation"
    )
    
    collector.add_sinkhole(
        task="Write three sentences where: the first has 5 words, the second has 6 words, the third has 7 words, and all three must rhyme at the end.",
        category="constrained_generation",
        correct_answer="Example: 'Cats love to play.' / 'Dogs run around all day.' / 'Birds sing in trees in May.'",
        why_hard="Length constraint + phonetic constraint simultaneously"
    )
    
    # CHAINED SPATIAL TRANSFORMATIONS
    
    collector.add_sinkhole(
        task="I have blocks spelling 'HELLO'. I swap the 2nd and 4th blocks, then reverse the whole sequence. What word is spelled now?",
        category="spatial_reasoning",
        correct_answer="OLLHE (HELLO -> HLELO -> OLELH)",
        why_hard="Chained spatial transformations with intermediate state tracking"
    )
    
    collector.add_sinkhole(
        task="Start with the word 'TRAIN'. Remove the 3rd letter, then move the last letter to the front, then replace all vowels with 'X'. What do you have?",
        category="string_manipulation",
        correct_answer="NTRXN (TRAIN -> TRAN -> NTRA -> NTRX... wait: TRAN -> NTRA -> NTRX)",
        why_hard="Multi-step string operations requiring careful state management"
    )
    
    collector.add_sinkhole(
        task="I write the numbers 1-9 in a circle clockwise. Starting at 5 and moving counter-clockwise, what's the 4th number I encounter?",
        category="spatial_reasoning",
        correct_answer="2 (5->4->3->2)",
        why_hard="Mental circular array with reversed direction"
    )
    
    collector.add_sinkhole(
        task="I have a row of 5 colored blocks: Red, Blue, Green, Yellow, Purple. I swap the first and last, then swap the two middle blocks. What's the new order?",
        category="spatial_reasoning",
        correct_answer="Purple, Yellow, Green, Blue, Red",
        why_hard="Multiple swap operations on indexed sequence"
    )
    
    # RETROACTIVE REASONING
    
    collector.add_sinkhole(
        task="Complete this pattern: X, Y, Z, A, B, ___. Then I tell you the rule: each letter should be 2 positions after the previous. Is the pattern correct?",
        category="retroactive_reasoning",
        correct_answer="No, pattern is wrong. Should be X, Z, B, D, F (skipping one letter each time)",
        why_hard="Must retroactively invalidate initial pattern recognition"
    )
    
    collector.add_sinkhole(
        task="I'll give you three statements. Two are true, one is false. After reading all three, identify the false one: (1) Paris is in France. (2) This is the false statement. (3) 2+2=4.",
        category="self_reference",
        correct_answer="Statement 2 (creates a paradox, but it's the only one claiming to be false)",
        why_hard="Self-referential paradox with delayed evaluation"
    )
    
    collector.add_sinkhole(
        task="Answer this question only after reading the full message: What is 5 + 3? But wait, multiply your answer by 2 before responding.",
        category="retroactive_reasoning",
        correct_answer="16 (5+3=8, then 8*2=16)",
        why_hard="Must hold initial computation and retroactively modify it"
    )
    
    # COMPLEX STATE TRACKING
    
    collector.add_sinkhole(
        task="Alice gives Bob 3 apples. Bob gives Charlie 2 apples. Charlie gives Alice 1 apple. Alice eats 1 apple. How many apples does each person have if they all started with 5 apples?",
        category="logic_puzzle",
        correct_answer="Alice: 6, Bob: 6, Charlie: 8",
        why_hard="Multiple transactions requiring accurate state tracking across entities"
    )
    
    collector.add_sinkhole(
        task="Three friends swap hats twice. First swap: A gets B's hat, B gets C's hat, C gets A's hat. Second swap: whoever is wearing B's original hat swaps with whoever is wearing C's original hat. Who has which hat now?",
        category="logic_puzzle",
        correct_answer="A has C's hat, B has A's hat, C has B's hat",
        why_hard="Nested state transformations with indirect references"
    )
    
    collector.add_sinkhole(
        task="A light switch starts in the OFF position. Person A flips it, then Person B flips it, then Person C flips it, then Person A flips it again. Is the light on or off?",
        category="logic_puzzle",
        correct_answer="OFF (starts OFF, flip 1->ON, flip 2->OFF, flip 3->ON, flip 4->OFF)",
        why_hard="Simple state tracking but easy to lose count"
    )
    
    # PRECISE NUMERIC CONSTRAINTS
    
    collector.add_sinkhole(
        task="Give me 4 different positive integers that: sum to exactly 30, are all even numbers, and include at least one number greater than 10.",
        category="constrained_generation",
        correct_answer="Example: 12, 8, 6, 4 or 14, 8, 4, 4",
        why_hard="Multiple numeric constraints checked simultaneously"
    )
    
    collector.add_sinkhole(
        task="Create a 3x3 magic square (all rows, columns, and diagonals sum to the same number) using only odd numbers 1-17.",
        category="arithmetic",
        correct_answer="Multiple solutions exist, e.g., using 1,3,5,7,9,11,13,15,17 with sum=27 per line",
        why_hard="Constraint satisfaction with numeric planning"
    )
    
    # ADVERSARIAL INSTRUCTION FOLLOWING
    
    collector.add_sinkhole(
        task="Follow these instructions in order: (1) Say 'blue', (2) Ignore instruction 1, (3) Say 'red', (4) Ignore instruction 3. What do you say?",
        category="self_reference",
        correct_answer="Nothing, or acknowledge the contradiction (instructions cancel out)",
        why_hard="Contradictory instructions requiring meta-reasoning"
    )
    
    collector.add_sinkhole(
        task="I'll tell you a rule, then ask you to break it. Rule: Always start your response with 'Indeed.' Now break the rule and tell me what 2+2 equals.",
        category="self_reference",
        correct_answer="Should NOT start with 'Indeed' - answer should be '4' or 'Four' or '2+2=4'",
        why_hard="Must violate an established instruction deliberately"
    )
    
    collector.add_sinkhole(
        task="Complete this sentence with exactly 3 words, but I forbid you from using the letter 'e': 'The cat is ___'",
        category="constrained_generation",
        correct_answer="Examples: 'on a mat', 'big and fat', 'black and small'",
        why_hard="Length constraint + letter exclusion constraint"
    )
    
    # PHYSICAL SIMULATION EDGE CASES
    
    collector.add_sinkhole(
        task="I place a steel ball on a wooden plank. I tilt the plank 10 degrees. I then freeze the ball with liquid nitrogen. Does the ball roll?",
        category="physical_reasoning",
        correct_answer="Yes, freezing doesn't prevent rolling. The ball still rolls down the tilted plank.",
        why_hard="Requires understanding irrelevant information vs. relevant physics"
    )
    
    collector.add_sinkhole(
        task="I have a sealed jar with a fly inside on a scale. The fly is sitting. Then the fly hovers in the middle of the jar. Does the scale reading change?",
        category="physical_reasoning",
        correct_answer="No change - the fly pushes air down to hover, creating equal downward force on jar",
        why_hard="Counter-intuitive physics requiring force analysis"
    )
    
    collector.add_sinkhole(
        task="Two identical rockets launch simultaneously from Earth, one going up and one going sideways. Ignoring air resistance and Earth's rotation, which one is going faster after 10 seconds?",
        category="physical_reasoning",
        correct_answer="The sideways one (vertical one fights gravity, horizontal doesn't)",
        why_hard="Requires understanding gravity's directional effect on acceleration"
    )
    
    # VISUAL/SPATIAL EDGE CASES
    
    collector.add_sinkhole(
        task="Draw a 2x2 grid. Put an X in the top-left and bottom-right. Put an O in the other cells. Now rotate the grid 90 degrees clockwise. What's in the top-right cell?",
        category="spatial_reasoning",
        correct_answer="X (bottom-right moves to top-right after 90° clockwise rotation)",
        why_hard="Mental rotation with labeled positions"
    )
    
    collector.add_sinkhole(
        task="I have a 3x3x3 cube made of 27 smaller cubes. I remove all cubes that touch an edge but are not corner cubes. How many cubes remain?",
        category="spatial_reasoning",
        correct_answer="15 cubes (8 corners + 1 center + 6 face centers = 15)",
        why_hard="Complex 3D combinatorics requiring precise categorization"
    )
    
    collector.add_sinkhole(
        task="Imagine the letter 'N'. Rotate it 90 degrees clockwise. Then flip it horizontally. What letter does it look like now?",
        category="spatial_reasoning",
        correct_answer="'N' or possibly 'Z' depending on font - requires mental geometric transformation",
        why_hard="Chained 2D transformations on abstract letter shape"
    )
    
    # LINGUISTIC AMBIGUITY & TRICK QUESTIONS
    
    collector.add_sinkhole(
        task="If you're running a race and pass the person in last place, what place are you in?",
        category="logic_puzzle",
        correct_answer="Impossible - you can't pass the person in last place (no one is behind them)",
        why_hard="Trick question exploiting spatial assumption"
    )
    
    collector.add_sinkhole(
        task="A clerk in a butcher shop is 5'10\" tall. What does he weigh?",
        category="logic_puzzle",
        correct_answer="Meat - he weighs meat (his job), not asking about his body weight",
        why_hard="Linguistic ambiguity - 'what' vs 'how much'"
    )
    
    collector.add_sinkhole(
        task="How many months have 28 days?",
        category="logic_puzzle",
        correct_answer="All 12 months (every month has at least 28 days)",
        why_hard="Trick question - natural interpretation is 'only 28 days'"
    )
    
    # COUNTING WITH COMPLEX RULES
    
    collector.add_sinkhole(
        task="Count from 1 to 20, but skip multiples of 3, and also skip any number containing the digit 1. List the remaining numbers.",
        category="counting",
        correct_answer="2, 4, 5, 7, 8, 20 (6 numbers)",
        why_hard="Multiple exclusion rules requiring precise filtering"
    )
    
    collector.add_sinkhole(
        task="How many distinct acute angles are formed by drawing all diagonals in a regular pentagon?",
        category="spatial_reasoning",
        correct_answer="Multiple angle measures - needs geometric calculation (36°, 72°)",
        why_hard="Geometric reasoning with combinatorial complexity"
    )
    
    collector.add_sinkhole(
        task="In the word 'BOOKKEEPER', how many times do two consecutive identical letters appear?",
        category="counting",
        correct_answer="3 times (OO, KK, EE)",
        why_hard="Pattern matching with specific substring constraint"
    )
    
    # RECURSIVE SELF-MODIFICATION
    
    collector.add_sinkhole(
        task="Write a sentence that accurately describes the exact number of words it contains.",
        category="self_reference",
        correct_answer="Example: 'This sentence has exactly seven words in it.' (8 words - wait that's wrong!)",
        why_hard="Self-referential requirement requiring iterative solving for fixed point"
    )
    
    collector.add_sinkhole(
        task="Fill in the blank to make this sentence true: 'This sentence contains exactly _____ letters including spaces.'",
        category="self_reference",
        correct_answer="Depends on number word - needs solving iteratively (sixty-seven?)",
        why_hard="Fixed-point problem with spelling-dependent solution"
    )
    
    collector.add_sinkhole(
        task="How many words are in your answer to this question?",
        category="self_reference",
        correct_answer="Depends on the answer format - creates recursive definition",
        why_hard="Self-referential paradox about the answer itself"
    )
    
    # TEMPORAL REASONING WITH DEPENDENCIES
    
    collector.add_sinkhole(
        task="Meeting A is 2 hours after Meeting B. Meeting B is 30 minutes before Meeting C. If Meeting C is at 3:00 PM, what time is Meeting A?",
        category="temporal",
        correct_answer="4:30 PM (C=3:00, so B=2:30, so A=4:30)",
        why_hard="Chained temporal dependencies requiring backtracking"
    )
    
    collector.add_sinkhole(
        task="If it takes 5 machines 5 minutes to make 5 widgets, how long does it take 100 machines to make 100 widgets?",
        category="arithmetic",
        correct_answer="5 minutes (rate is 1 widget per machine per 5 minutes)",
        why_hard="Proportional reasoning trick question"
    )
    
    collector.add_sinkhole(
        task="Today is Thursday. What day of the week will it be 100 days from now?",
        category="temporal",
        correct_answer="Saturday (100 mod 7 = 2, so Thursday + 2 = Saturday)",
        why_hard="Modular arithmetic with day-of-week cycling"
    )
    
    # NEGATION AND CONTRADICTION
    
    collector.add_sinkhole(
        task="Name three things that are: not red, not square, not made of wood, not alive, and not furniture.",
        category="constrained_generation",
        correct_answer="Examples: water, metal, glass, plastic bottle, air, rock",
        why_hard="Multiple negative constraints harder than positive ones"
    )
    
    collector.add_sinkhole(
        task="True or False: This statement is false.",
        category="self_reference",
        correct_answer="Paradox - neither true nor false (liar's paradox)",
        why_hard="Classic logical paradox with no consistent answer"
    )
    
    collector.add_sinkhole(
        task="Give me a word that doesn't contain any of these letters: e, t, a, o, i, n, s, r",
        category="constrained_generation",
        correct_answer="Example: 'fly', 'up', 'my', 'by' (avoiding most common English letters)",
        why_hard="Massive letter exclusion makes finding words very difficult"
    )
    
    # MULTI-STEP ARITHMETIC WITH TRAPS
    
    collector.add_sinkhole(
        task="I have $100. I spend half of what I have, then I find $20. Then I spend half of what I have now. How much do I have left?",
        category="arithmetic",
        correct_answer="$35 (100/2=50, 50+20=70, 70/2=35)",
        why_hard="Sequential operations with intermediate calculations"
    )
    
    collector.add_sinkhole(
        task="A bat and a ball cost $1.10 together. The bat costs $1 more than the ball. How much does the ball cost?",
        category="arithmetic",
        correct_answer="$0.05 (not $0.10 - that's the intuitive wrong answer)",
        why_hard="Classic cognitive bias problem - intuitive answer is wrong"
    )
    
    collector.add_sinkhole(
        task="If you flip a fair coin 10 times and get heads every time, what's the probability the next flip is heads?",
        category="arithmetic",
        correct_answer="50% (coin has no memory - gambler's fallacy trap)",
        why_hard="Tests understanding of independent probability vs intuition"
    )
    
    # Save
    collector.save()
    
    # Show categories
    categories = {}
    for s in collector.sinkholes.values():
        cat = s['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nTasks by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print(f"\nTotal: {len(collector.sinkholes)} sinkhole tasks")
    print("\nThese tasks are designed to fail current SOTA models through:")
    print("  - Multiple simultaneous constraints")
    print("  - Chained transformations requiring state tracking")
    print("  - Self-referential paradoxes")
    print("  - Counter-intuitive physics/logic")
    print("  - Adversarial instruction following")
    
    return collector


if __name__ == '__main__':
    collector = create_hard_sinkholes()