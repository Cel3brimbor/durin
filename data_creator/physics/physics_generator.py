import json
import random
import os

physics_topics = [
    "Quantum Mechanics", "General Relativity", "Special Relativity", "Thermodynamics",
    "Particle Physics", "Astrophysics", "Electromagnetism", "Classical Mechanics",
    "Optics", "Solid State Physics", "Nuclear Physics", "Plasma Physics",
    "Quantum Field Theory", "Chaos Theory", "String Theory", "Fluid Dynamics",
    "Cosmology", "Quantum Computing", "Statistical Physics", "Astrodynamics",
    "Black Hole Physics", "Quantum Tunneling", "Condensed Matter Physics",
    "High-Energy Physics", "Relativistic Quantum Mechanics", "Thermal Radiation",
    "Mechanics of Materials", "Wave Mechanics", "Nuclear Fusion", "Gravitational Physics",
    "Superconductivity", "Dark Matter Studies", "Neutrino Physics", "Holographic Principle",
    "Quantum Entanglement", "Cosmic Microwave Background", "Supersymmetry",
    "Topological Insulators", "Gravitational Waves", "Photonics"
]

physics_subtopics = {
    "Quantum Mechanics": ["Entanglement", "Superposition", "Heisenberg Uncertainty", "Wave-Particle Duality"],
    "General Relativity": ["Black Holes", "Gravitational Waves", "Spacetime Curvature", "Einstein Equations"],
    "Particle Physics": ["Quarks", "Leptons", "Higgs Boson", "Standard Model"],
    "Astrophysics": ["Stellar Evolution", "Galactic Dynamics", "Cosmic Rays", "Exoplanets"],
}

physics_tab_templates = [
    "{} Fundamentals", "{} Advanced Theory", "{} Research Papers", "{} Simulations",
    "{} Equations Explained", "{} Experimental Methods", "{} Theoretical Models",
    "{} in Modern Physics", "{} Problem Sets", "{} Case Studies",
    "{} Quantum Insights", "{} Relativistic Concepts", "{} Particle Dynamics",
    "{} Astrophysical Phenomena", "{} Computational Techniques",
    "{} Lab Reports", "{} Theoretical Advances", "{} Observational Data",
    "{} Mathematical Foundations", "{} Experimental Design",
    "{} for Physicists", "{} Breakthroughs", "{} Symposia",
    "{} in High-Energy Contexts", "{} Quantum Algorithms"
]

non_physics_topics = [
    "Cooking", "History", "Music Theory", "Visual Arts", "Gardening", "Literature",
    "Photography", "Yoga", "Knitting", "Cryptocurrency", "Interior Design", "Fashion Design",
    "Creative Writing", "Baking", "Software Development", "Architecture", "Travel Blogging",
    "Sports Science", "Ballet", "Film Production", "Graphic Design", "Poetry",
    "Hiking", "Culinary Arts", "Historical Astronomy", "Botany", "Philosophy",
    "Macroeconomics", "Theater Performance", "Sculpture", "Pottery", "Carpentry",
    "Digital Marketing", "Wildlife Photography", "Gastronomy", "Meditation",
    "Vintage Car Restoration", "Urban Planning", "Stand-up Comedy", "Documentary Filmmaking"
]

non_physics_subtopics = {
    "Cooking": ["Italian Cuisine", "Baking Techniques", "Vegan Recipes", "Sous-Vide Cooking"],
    "History": ["Ancient Rome", "Medieval Europe", "World War II", "Renaissance Art"],
    "Music Theory": ["Jazz Harmony", "Classical Composition", "Music Notation", "Chord Progressions"],
    "Visual Arts": ["Impressionism", "Abstract Art", "Portrait Painting", "Sculpture Techniques"],
}

non_physics_tab_templates = [
    "{} Recipes", "{} Practical Guide", "{} Creative Techniques", "{} Historical Overview",
    "{} Essentials", "{} Masterclass", "{} DIY Projects", "{} Modern Trends",
    "{} Skill-Building", "{} Workshops", "{} Cultural Insights",
    "{} Artistic Styles", "{} Culinary Secrets", "{} Outdoor Adventures",
    "{} Literary Analysis", "{} Performance Tips", "{} Design Inspirations",
    "{} Craft Tutorials", "{} Lifestyle Blog", "{} Hobby Guide",
    "{} Creative Portfolio", "{} Skill Workshops", "{} Historical Narratives",
    "{} Artistic Movements", "{} Practical Skills"
]

def generate_tab_titles(topics, subtopics, templates, num_tabs):
    """generate a list of tab titles with varied topics or subtopics to avoid repetition"""
    titles = []
    used_topics = set()
    for _ in range(num_tabs):
        available_topics = [t for t in topics if t not in used_topics]
        if not available_topics:
            available_topics = topics 
            used_topics.clear()
        topic = random.choice(available_topics)
        used_topics.add(topic)
        
        topic_variations = subtopics.get(topic, topic.split())
        variation = random.choice(topic_variations)
        template = random.choice(templates)
        titles.append(template.format(variation))
    return titles

def generate_dataset(num_examples):
    """generate a dataset with the specified number of examples, ensuring even tab count distribution"""
    data = []
    tabs_per_count = num_examples // 8
    remainder = num_examples % 8
    tab_counts = (
        [2] * tabs_per_count + [3] * tabs_per_count + [4] * tabs_per_count +
        [5] * tabs_per_count + [6] * tabs_per_count + [7] * tabs_per_count +
        [8] * tabs_per_count + [9] * tabs_per_count +
        [2, 3, 4, 5, 6, 7, 8, 9][:remainder]
    )
    random.shuffle(tab_counts)
    
    for i in range(num_examples):
        alignment = 1 if i % 2 == 0 else 0
        num_tabs = tab_counts[i]
        
        opened_tabs = generate_tab_titles(physics_topics, physics_subtopics, physics_tab_templates, num_tabs)
        
        if alignment == 1:
            physics_topic = random.choice(physics_topics)
            new_tab = generate_tab_titles([physics_topic], physics_subtopics, physics_tab_templates, 1)[0]
        else:
            non_physics_topic = random.choice(non_physics_topics)
            new_tab = generate_tab_titles([non_physics_topic], non_physics_subtopics, non_physics_tab_templates, 1)[0]
        
        data.append({
            "opened_tabs": opened_tabs,
            "new_tab": new_tab,
            "alignment": alignment
        })
    
    random.shuffle(data)
    print("Sample dataset entries:")
    for i in range(3):
        print(f"Example {i}:")
        print(f"  Opened tabs: {data[i]['opened_tabs']}")
        print(f"  New tab: {data[i]['new_tab']}")
        print(f"  Alignment: {data[i]['alignment']}")
    return {"data": data}

def save_dataset(data, filename=None, default_dir="/Users/norranyu/Documents/coding/x_code/git_repo/inference_engine/datasets/physics"):
    if filename is None:
        filename = os.path.join(default_dir, "physics_dataset.json")
    
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")
        except OSError as e:
            print(f"Error creating directory {output_dir}: {e}")
            print("Falling back to current directory.")
            filename = "physics_dataset.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Dataset saved to {filename}")
    except (OSError, PermissionError) as e:
        print(f"Error saving to {filename}: {e}")
        print("Falling back to current directory.")
        fallback_filename = "physics_dataset.json"
        with open(fallback_filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Dataset saved to {fallback_filename}")

def main():
    print("Enter the full path to save the dataset (press Enter for default location): ")
    user_input = input("Path: ").strip()
    
    dataset = generate_dataset(20000)
    
    if user_input:
        save_dataset(dataset, filename=user_input)
    else:
        save_dataset(dataset)

if __name__ == "__main__":
    main()