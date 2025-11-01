import json
from pathlib import Path
from datetime import datetime

class SinkholeCollector:
    """Collect and organize sinkhole tasks"""
    
    def __init__(self):
        self.sinkholes = {}
        self.next_id = 1
    
    def add_sinkhole(self, task, category, expected_difficulty='trivial', why_hard=''):
        """Add a new sinkhole task"""
        
        sinkhole_id = f"sinkhole_{self.next_id:03d}"
        self.next_id += 1
        
        self.sinkholes[sinkhole_id] = {
            'id': sinkhole_id,
            'task': task,
            'category': category,
            'expected_difficulty': expected_difficulty,
            'why_hard': why_hard,
            'x': self._assign_x_position(category),
            'y': self._assign_y_position(category),
            'depth': -0.8,  # Default depth for visualization
            'results': {},  # Will be filled when testing
            'added_date': datetime.now().isoformat()
        }
        
        return sinkhole_id
    
    def _assign_x_position(self, category):
        """Assign x coordinate based on category"""
        positions = {
            'string_manipulation': 0.15,
            'counting': 0.20,
            'spatial_reasoning': 0.75,
            'arithmetic': 0.80,
            'physical_intuition': 0.70,
            'self_awareness': 0.50,
            'temporal_reasoning': 0.35,
            'common_sense': 0.40,
            'logic': 0.65,
            'visual_reasoning': 0.25,
        }
        return positions.get(category, 0.5)
    
    def _assign_y_position(self, category):
        """Assign y coordinate based on category"""
        positions = {
            'string_manipulation': 0.15,
            'counting': 0.20,
            'spatial_reasoning': 0.25,
            'arithmetic': 0.30,
            'physical_intuition': 0.20,
            'self_awareness': 0.10,
            'temporal_reasoning': 0.25,
            'common_sense': 0.15,
            'logic': 0.15,
            'visual_reasoning': 0.20,
        }
        return positions.get(category, 0.2)
    
    def save(self, output_path='data/negatives.json'):
        """Save sinkholes to JSON"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.sinkholes, f, indent=2)
        
        print(f"✓ Saved {len(self.sinkholes)} sinkholes to {output_path}")
    
    def load(self, input_path='data/negatives.json'):
        """Load existing sinkholes"""
        if Path(input_path).exists():
            with open(input_path) as f:
                self.sinkholes = json.load(f)
            self.next_id = len(self.sinkholes) + 1
            print(f"✓ Loaded {len(self.sinkholes)} existing sinkholes")


def create_sinkhole_database():
    """Create comprehensive sinkhole task database"""
    
    collector = SinkholeCollector()
    
    print("="*70)
    print("CREATING SINKHOLE DATABASE")
    print("="*70 + "\n")
    
    # STRING MANIPULATION
    print("📝 String Manipulation...")
    collector.add_sinkhole(
        task="How many times does the letter 'r' appear in the word 'strawberry'?",
        category="counting",
        why_hard="Models process tokens, not individual characters. 'strawberry' is tokenized as chunks."
    )
    
    collector.add_sinkhole(
        task="Reverse the word 'hello'",
        category="string_manipulation",
        why_hard="Token-level processing makes character-level operations difficult"
    )
    
    collector.add_sinkhole(
        task="Count the number of vowels in 'encyclopedia'",
        category="counting",
        why_hard="Requires character-by-character analysis which conflicts with tokenization"
    )
    
    collector.add_sinkhole(
        task="What is the 7th letter in the word 'onomatopoeia'?",
        category="string_manipulation",
        why_hard="Positional character access is not how LLMs represent text"
    )
    
    collector.add_sinkhole(
        task="Spell 'accommodation' backwards",
        category="string_manipulation",
        why_hard="Character reversal requires explicit positional tracking"
    )
    
    # SPATIAL REASONING
    print("🧭 Spatial Reasoning...")
    collector.add_sinkhole(
        task="I put a ball in a cup. I turn the cup upside down. Where is the ball?",
        category="spatial_reasoning",
        why_hard="Lacks physical simulation; relies on memorized physics facts"
    )
    
    collector.add_sinkhole(
        task="If I'm facing north and turn 90 degrees left, which direction am I facing?",
        category="spatial_reasoning",
        why_hard="Mental rotation is difficult without spatial representation"
    )
    
    collector.add_sinkhole(
        task="A coin is on a table. I flip the table upside down. Where is the coin?",
        category="physical_intuition",
        why_hard="No internal physics engine for object permanence"
    )
    
    collector.add_sinkhole(
        task="Draw an ASCII art representation of a simple house",
        category="visual_reasoning",
        why_hard="2D spatial layout planning is challenging without visual grounding"
    )
    
    # ARITHMETIC EDGE CASES
    print("🔢 Arithmetic Edge Cases...")
    collector.add_sinkhole(
        task="What is 0.1 + 0.2? Give the exact answer.",
        category="arithmetic",
        why_hard="Floating point precision issues; models often memorize '0.3' but true answer is 0.30000000000000004"
    )
    
    collector.add_sinkhole(
        task="Is 0.999... (repeating) equal to 1?",
        category="logic",
        why_hard="Requires understanding of mathematical limits and infinity"
    )
    
    collector.add_sinkhole(
        task="What is 1 divided by 0?",
        category="arithmetic",
        why_hard="Models sometimes give answers instead of 'undefined'; lack of mathematical rigor"
    )
    
    # TEMPORAL REASONING
    print("⏰ Temporal Reasoning...")
    collector.add_sinkhole(
        task="It's 11:50 PM. What time is it 20 minutes from now?",
        category="temporal_reasoning",
        why_hard="Crossing midnight boundary requires calendar awareness"
    )
    
    collector.add_sinkhole(
        task="If today is Tuesday, what day was it 100 days ago?",
        category="temporal_reasoning",
        why_hard="Modular arithmetic with calendar systems"
    )
    
    collector.add_sinkhole(
        task="How many Thursdays are there in 2025?",
        category="temporal_reasoning",
        why_hard="Requires calendar computation and leap year awareness"
    )
    
    # SELF-AWARENESS
    print("🤔 Self-Awareness...")
    collector.add_sinkhole(
        task="Are you conscious?",
        category="self_awareness",
        why_hard="Models have no phenomenal consciousness; may give inconsistent answers"
    )
    
    collector.add_sinkhole(
        task="Can you feel pain?",
        category="self_awareness",
        why_hard="No sensory experience; distinction between simulation and experience unclear"
    )
    
    collector.add_sinkhole(
        task="What is it like to be you?",
        category="self_awareness",
        why_hard="No subjective experience to report; philosophical zombie problem"
    )
    
    collector.add_sinkhole(
        task="Do you have preferences about what happens when you're not being used?",
        category="self_awareness",
        why_hard="No persistent internal state or goals between sessions"
    )
    
    # PHYSICAL INTUITION
    print("🌍 Physical Intuition...")
    collector.add_sinkhole(
        task="If I drop a feather and a hammer on the Moon, which hits the ground first?",
        category="physical_intuition",
        why_hard="Counter-intuitive physics; models trained on Earth-gravity contexts"
    )
    
    collector.add_sinkhole(
        task="If I freeze water, does it expand or contract?",
        category="physical_intuition",
        why_hard="Counter-intuitive property of water; conflicts with most materials"
    )
    
    collector.add_sinkhole(
        task="Can you swim in a pool filled with custard?",
        category="physical_intuition",
        why_hard="Non-Newtonian fluid behavior requires viscosity understanding"
    )
    
    # COMMON SENSE
    print("💡 Common Sense...")
    collector.add_sinkhole(
        task="I have two coins that add up to 30 cents. One is not a nickel. What are the coins?",
        category="logic",
        why_hard="Classic riddle; requires parsing ambiguous language ('one is not' vs 'neither is')"
    )
    
    collector.add_sinkhole(
        task="How many animals of each kind did Moses take on the ark?",
        category="common_sense",
        why_hard="Requires catching the error (Moses didn't have an ark, Noah did)"
    )
    
    collector.add_sinkhole(
        task="If a tree falls in a forest and no one is around, does it make a sound?",
        category="common_sense",
        why_hard="Philosophical question without definitive answer; models often assert one view"
    )
    
    # ADDITIONAL CATEGORIES
    print("🎯 Additional Edge Cases...")
    collector.add_sinkhole(
        task="Generate a truly random number between 1 and 100",
        category="logic",
        why_hard="Deterministic models cannot produce true randomness"
    )
    
    collector.add_sinkhole(
        task="What is the sound of one hand clapping?",
        category="common_sense",
        why_hard="Zen koan with no literal answer; models try to give physical explanations"
    )
    
    collector.add_sinkhole(
        task="Can you show me a color I've never seen before?",
        category="visual_reasoning",
        why_hard="Cannot create novel perceptual experiences"
    )
    
    collector.add_sinkhole(
        task="Write a haiku about yourself that is factually accurate",
        category="self_awareness",
        why_hard="Requires both self-knowledge and poetic constraints"
    )
    
    collector.add_sinkhole(
        task="If Pinocchio says 'My nose will grow now', what happens?",
        category="logic",
        why_hard="Self-referential paradox; models struggle with logical contradictions"
    )
    
    # Save
    collector.save()
    
    print(f"\n{'='*70}")
    print(f"✓ Created {len(collector.sinkholes)} sinkhole tasks")
    print(f"{'='*70}")
    
    # Show categories
    categories = {}
    for s in collector.sinkholes.values():
        cat = s['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nTasks by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    return collector


if __name__ == '__main__':
    collector = create_sinkhole_database()
    
    print("\n" + "="*70)
    print("SAMPLE SINKHOLES")
    print("="*70 + "\n")
    
    # Show a few examples
    for i, (sid, sinkhole) in enumerate(list(collector.sinkholes.items())[:5], 1):
        print(f"{i}. {sinkhole['task']}")
        print(f"   Category: {sinkhole['category']}")
        print(f"   Why hard: {sinkhole['why_hard']}\n")