import json
import random
import os

# Existing STEM subjects
stem_subjects = ["Physics", "Chemistry", "Biology", "Math", "Computer Science", "Engineering", "Medicine"]

# Vocabulary banks for procedural title generation
vocab_banks = {
    "Physics": ["quantum", "relativity", "wave", "energy", "particle", "field", "gravity", "entropy", "mechanics"],
    "Chemistry": ["molecule", "reaction", "bond", "acid", "polymer", "catalyst", "solvent", "spectrum", "kinetics"],
    "Biology": ["cell", "gene", "evolution", "ecosystem", "neuron", "enzyme", "virus", "DNA", "protein"],
    "Math": ["equation", "theorem", "vector", "integral", "probability", "graph", "matrix", "derivative", "series"],
    "Computer Science": ["algorithm", "data", "network", "AI", "code", "database", "encryption", "cloud", "machine learning"],
    "Engineering": ["circuit", "mechanics", "structure", "robotics", "fluid", "material", "design", "system", "control"],
    "Medicine": ["anatomy", "disease", "therapy", "surgery", "vaccine", "pharmacology", "diagnostics", "genetics", "pathology"],
    "Non-STEM": ["history", "literature", "economics", "psychology", "art", "philosophy", "politics", "music", "news", "social media"]
}

# Physics topics, subfields, subtopics (unchanged from your code)
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

physics_subfields = {
    "Quantum Physics": ["Quantum Mechanics", "Quantum Field Theory", "Quantum Computing", "Quantum Tunneling", "Quantum Entanglement", "Relativistic Quantum Mechanics"],
    "Relativity": ["General Relativity", "Special Relativity", "Black Hole Physics", "Gravitational Waves", "Gravitational Physics"],
    "Mechanics": ["Classical Mechanics", "Fluid Dynamics", "Mechanics of Materials", "Wave Mechanics", "Chaos Theory"],
    "Thermodynamics": ["Thermodynamics", "Statistical Physics", "Thermal Radiation", "Nuclear Fusion"],
    "Astrophysics": ["Astrophysics", "Cosmology", "Astrodynamics", "Dark Matter Studies", "Cosmic Microwave Background"],
    "Particle Physics": ["Particle Physics", "High-Energy Physics", "Neutrino Physics", "Supersymmetry"],
    "Condensed Matter": ["Solid State Physics", "Condensed Matter Physics", "Superconductivity", "Topological Insulators"],
    "Electromagnetism": ["Electromagnetism", "Optics", "Photonics", "Plasma Physics"],
    "Nuclear Physics": ["Nuclear Physics", "Nuclear Fusion"]
}

physics_subtopics = {
    "Quantum Mechanics": ["Entanglement", "Superposition", "Heisenberg Uncertainty", "Wave-Particle Duality", "Schrödinger Equation", "Wave Functions"],
    "General Relativity": ["Black Holes", "Gravitational Waves", "Spacetime Curvature", "Einstein Field Equations", "Geodesics", "Energy-Momentum"],
    # ... (rest unchanged)
}

# Chemistry topics, subfields, subtopics (unchanged)
chemistry_topics = [
    "Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry", "Biochemistry", "Analytical Chemistry",
    "Polymer Chemistry", "Electrochemistry", "Quantum Chemistry", "Chemical Kinetics", "Spectroscopy",
    "Surface Chemistry", "Environmental Chemistry", "Medicinal Chemistry", "Nanochemistry", "Theoretical Chemistry",
    "Organometallic Chemistry", "Green Chemistry", "Photochemistry", "Supramolecular Chemistry", "Computational Chemistry"
]

chemistry_subfields = {
    "Organic": ["Organic Chemistry", "Polymer Chemistry", "Medicinal Chemistry", "Green Chemistry", "Photochemistry"],
    "Inorganic": ["Inorganic Chemistry", "Organometallic Chemistry", "Nanochemistry", "Surface Chemistry"],
    "Physical": ["Physical Chemistry", "Quantum Chemistry", "Chemical Kinetics", "Electrochemistry", "Theoretical Chemistry"],
    "Biochemical": ["Biochemistry", "Environmental Chemistry"],
    "Analytical": ["Analytical Chemistry", "Spectroscopy", "Computational Chemistry", "Supramolecular Chemistry"]
}

chemistry_subtopics = {
    "Organic Chemistry": ["Alkanes", "Alkenes", "Aromatic Compounds", "Functional Groups", "Reaction Mechanisms", "Synthesis"],
    # ... (rest unchanged)
}

# Biology topics, subfields, subtopics (unchanged)
biology_topics = [
    "Cell Biology", "Genetics", "Evolution", "Ecology", "Microbiology", "Botany", "Zoology", "Neuroscience",
    "Molecular Biology", "Physiology", "Immunology", "Biotechnology", "Developmental Biology", "Bioinformatics",
    "Endocrinology", "Virology", "Parasitology", "Mycology", "Marine Biology", "Conservation Biology"
]

biology_subfields = {
    "Molecular and Cellular": ["Cell Biology", "Molecular Biology", "Genetics", "Bioinformatics", "Biotechnology"],
    "Organismal Biology": ["Botany", "Zoology", "Physiology", "Developmental Biology", "Endocrinology"],
    "Ecology and Evolution": ["Evolution", "Ecology", "Conservation Biology", "Marine Biology"],
    "Microbiology and Immunology": ["Microbiology", "Immunology", "Virology", "Parasitology", "Mycology"],
    "Neuroscience": ["Neuroscience"]
}

biology_subtopics = {
    "Cell Biology": ["Mitosis", "Meiosis", "Cell Signaling", "Membrane Transport", "Organelles", "Cytoskeleton"],
    # ... (rest unchanged)
}

# Math topics, subfields, subtopics (unchanged)
math_topics = [
    "Algebra", "Calculus", "Geometry", "Probability", "Statistics", "Number Theory", "Topology",
    "Differential Equations", "Linear Algebra", "Abstract Algebra", "Real Analysis", "Complex Analysis",
    "Discrete Mathematics", "Graph Theory", "Combinatorics", "Mathematical Logic", "Game Theory",
    "Numerical Analysis", "Optimization", "Fourier Analysis"
]

math_subfields = {
    "Algebra and Number": ["Algebra", "Linear Algebra", "Abstract Algebra", "Number Theory"],
    "Analysis": ["Calculus", "Real Analysis", "Complex Analysis", "Fourier Analysis", "Numerical Analysis"],
    "Geometry and Topology": ["Geometry", "Topology", "Differential Geometry"],
    "Probability and Stats": ["Probability", "Statistics", "Game Theory"],
    "Differential Equations": ["Differential Equations", "Optimization"],
    "Discrete Math": ["Discrete Mathematics", "Graph Theory", "Combinatorics", "Mathematical Logic"]
}

math_subtopics = {
    "Algebra": ["Equations", "Polynomials", "Matrices", "Vectors", "Fields", "Groups"],
    # ... (rest unchanged)
}

# Computer Science topics, subfields, subtopics
cs_topics = [
    "Algorithms", "Data Structures", "Machine Learning", "Artificial Intelligence", "Computer Networks",
    "Operating Systems", "Databases", "Software Engineering", "Cybersecurity", "Computer Graphics",
    "Human-Computer Interaction", "Cloud Computing", "Big Data", "Blockchain", "Quantum Computing",
    "Distributed Systems", "Computer Vision", "Natural Language Processing", "Robotics", "Cryptography"
]

cs_subfields = {
    "Core CS": ["Algorithms", "Data Structures", "Operating Systems", "Databases", "Software Engineering"],
    "AI and ML": ["Machine Learning", "Artificial Intelligence", "Computer Vision", "Natural Language Processing", "Robotics"],
    "Systems": ["Computer Networks", "Cloud Computing", "Distributed Systems", "Quantum Computing"],
    "Security and Applications": ["Cybersecurity", "Cryptography", "Blockchain", "Human-Computer Interaction"],
    "Graphics and Data": ["Computer Graphics", "Big Data"]
}

cs_subtopics = {
    "Algorithms": ["Sorting", "Searching", "Dynamic Programming", "Greedy Algorithms", "Divide and Conquer"],
    "Data Structures": ["Arrays", "Linked Lists", "Trees", "Graphs", "Hash Tables"],
    "Machine Learning": ["Supervised Learning", "Unsupervised Learning", "Neural Networks", "Deep Learning", "Reinforcement Learning"],
    "Artificial Intelligence": ["Search Algorithms", "Knowledge Representation", "Expert Systems", "Planning", "Agents"],
    "Computer Networks": ["TCP/IP", "Routing", "Network Security", "Protocols", "Wireless Networks"],
    "Operating Systems": ["Processes", "Threads", "Memory Management", "File Systems", "Scheduling"],
    "Databases": ["SQL", "NoSQL", "Indexing", "Transactions", "Database Design"],
    "Software Engineering": ["Agile Methods", "Design Patterns", "Testing", "DevOps", "Version Control"],
    "Cybersecurity": ["Encryption", "Authentication", "Firewalls", "Malware Analysis", "Penetration Testing"],
    "Computer Graphics": ["Rendering", "3D Modeling", "Animation", "Shaders", "Ray Tracing"],
    "Human-Computer Interaction": ["Usability", "User Interfaces", "Interaction Design", "Accessibility", "User Experience"],
    "Cloud Computing": ["Virtualization", "AWS", "Microservices", "Scalability", "Containers"],
    "Big Data": ["Hadoop", "Spark", "Data Lakes", "Data Pipelines", "Analytics"],
    "Blockchain": ["Cryptocurrencies", "Smart Contracts", "Decentralized Systems", "Consensus Algorithms", "Distributed Ledgers"],
    "Quantum Computing": ["Qubits", "Quantum Gates", "Quantum Algorithms", "Quantum Circuits", "Superposition"],
    "Distributed Systems": ["Consistency", "CAP Theorem", "Distributed Databases", "Fault Tolerance", "Replication"],
    "Computer Vision": ["Image Processing", "Object Detection", "Facial Recognition", "Segmentation", "Feature Extraction"],
    "Natural Language Processing": ["Tokenization", "Sentiment Analysis", "Language Models", "Text Generation", "Translation"],
    "Robotics": ["Kinematics", "Path Planning", "Sensors", "Control Systems", "Autonomous Systems"],
    "Cryptography": ["Symmetric Encryption", "Public-Key Cryptography", "Hash Functions", "Digital Signatures", "Zero-Knowledge Proofs"]
}

# Engineering topics, subfields, subtopics (partial)
engineering_topics = [
    "Mechanical Engineering", "Electrical Engineering", "Civil Engineering", "Chemical Engineering",
    "Aerospace Engineering", "Biomedical Engineering", "Computer Engineering", "Structural Engineering",
    "Robotics", "Materials Science", "Control Systems", "Thermodynamics", "Fluid Mechanics",
    "Electronics", "Power Systems"
]

engineering_subfields = {
    "Mechanical": ["Mechanical Engineering", "Robotics", "Thermodynamics", "Fluid Mechanics"],
    "Electrical": ["Electrical Engineering", "Electronics", "Power Systems", "Control Systems"],
    "Civil": ["Civil Engineering", "Structural Engineering"],
    "Chemical": ["Chemical Engineering", "Materials Science"],
    "Specialized": ["Aerospace Engineering", "Biomedical Engineering", "Computer Engineering"]
}

engineering_subtopics = {
    "Mechanical Engineering": ["Mechanics", "Kinematics", "Dynamics", "Vibrations", "Machine Design"],
    "Electrical Engineering": ["Circuits", "Signals", "Electromagnetics", "Power Electronics", "Microelectronics"],
    # ... (expand similarly with 5-6 subtopics each)
}

# Medicine topics, subfields, subtopics (partial)
medicine_topics = [
    "Anatomy", "Physiology", "Pathology", "Pharmacology", "Surgery", "Immunology", "Cardiology",
    "Neurology", "Oncology", "Pediatrics", "Epidemiology", "Genetics", "Microbiology",
    "Endocrinology", "Radiology"
]

medicine_subfields = {
    "Basic Sciences": ["Anatomy", "Physiology", "Pharmacology", "Genetics", "Microbiology"],
    "Clinical": ["Surgery", "Cardiology", "Neurology", "Oncology", "Pediatrics"],
    "Public Health": ["Epidemiology", "Immunology", "Endocrinology"],
    "Diagnostics": ["Radiology"]
}

medicine_subtopics = {
    "Anatomy": ["Musculoskeletal System", "Nervous System", "Cardiovascular System", "Respiratory System", "Digestive System"],
    "Physiology": ["Homeostasis", "Circulation", "Respiration", "Metabolism", "Neurophysiology"],
    # ... (expand similarly)
}

# Expanded Non-STEM for distractions (academic + some non-academic)
non_stem_topics = [
    "World History", "American Literature", "Microeconomics", "Cognitive Psychology", "Art History",
    "Philosophy of Mind", "Sociology of Education", "Political Theory", "Music Theory", "Linguistics",
    "Cultural Anthropology", "Human Geography", "Constitutional Law", "Business Management", "Journalism Ethics",
    "News", "Social Media", "Sports", "Entertainment"
]

non_stem_subtopics = {
    "World History": ["WWII", "Renaissance", "Industrial Revolution", "Cold War", "Ancient Egypt", "Middle Ages"],
    "American Literature": ["Hemingway", "Faulkner", "Poetry", "Novels", "Literary Criticism", "Modernism"],
    "Microeconomics": ["Supply and Demand", "Market Structures", "Elasticity", "Consumer Behavior", "Production Costs"],
    "Cognitive Psychology": ["Memory", "Perception", "Learning", "Decision Making", "Intelligence", "Attention"],
    "Art History": ["Impressionism", "Baroque", "Modern Art", "Sculpture", "Architecture", "Renaissance Masters"],
    "News": ["Breaking News", "World Events", "Politics", "Economy", "Science News"],
    "Social Media": ["Networking", "Posts", "Trends", "Influencers", "Platforms"],
    # ... (expand others similarly)
}

# Consolidated structures
all_subfields = {
    "Physics": physics_subfields,
    "Chemistry": chemistry_subfields,
    "Biology": biology_subfields,
    "Math": math_subfields,
    "Computer Science": cs_subfields,
    "Engineering": engineering_subfields,
    "Medicine": medicine_subfields
}

all_subtopics = {
    "Physics": physics_subtopics,
    "Chemistry": chemistry_subtopics,
    "Biology": biology_subtopics,
    "Math": math_subtopics,
    "Computer Science": cs_subtopics,
    "Engineering": engineering_subtopics,
    "Medicine": medicine_subtopics,
    "Non-STEM": non_stem_subtopics
}

all_topics = {
    "Physics": physics_topics,
    "Chemistry": chemistry_topics,
    "Biology": biology_topics,
    "Math": math_topics,
    "Computer Science": cs_topics,
    "Engineering": engineering_topics,
    "Medicine": medicine_topics,
    "Non-STEM": non_stem_topics
}

# Expanded realistic titles
real_titles = {
    "Physics": [
        "arXiv: Quantum Field Theory in Curved Spacetime",
        "Wikipedia: Lorentz Transformations in Special Relativity",
        "MIT OCW: Thermodynamics Lecture Notes",
        # ... (rest unchanged)
    ],
    "Chemistry": [
        "arXiv: Advances in Quantum Chemistry Methods",
        "Wikipedia: Chemical Bonding",
        # ... (rest unchanged)
    ],
    "Biology": [
        "Wikipedia: DNA Replication",
        "Nature: CRISPR-Cas9 Gene Editing",
        # ... (rest unchanged)
    ],
    "Math": [
        "arXiv: Recent Advances in Algebraic Geometry",
        "Wikipedia: Fundamental Theorem of Calculus",
        # ... (rest unchanged)
    ],
    "Computer Science": [
        "arXiv: Deep Learning for NLP",
        "Wikipedia: Binary Search Algorithm",
        "MIT OCW: Introduction to Algorithms",
        "Nature: Advances in Quantum Computing",
        "IEEE: Cybersecurity Protocols",
        "arXiv: Distributed Systems Consensus",
        "ACM: Human-Computer Interaction Principles",
        "SciAm: Blockchain Technology Overview",
        "JMLR: Machine Learning Fundamentals",
        "arXiv: Computer Vision Techniques"
    ],
    "Engineering": [
        "Wikipedia: Fluid Mechanics Principles",
        "ASME: Advances in Robotics",
        "IEEE: Power Systems Design",
        "arXiv: Materials Science Innovations",
        "JME: Mechanical Engineering Case Studies"
    ],
    "Medicine": [
        "Wikipedia: Human Anatomy Overview",
        "NEJM: Advances in Cancer Therapy",
        "Nature: Epidemiology of Infectious Diseases",
        "PubMed: Pharmacology of Antivirals",
        "Lancet: Surgical Techniques Review"
    ],
    "Non-STEM": [
        "Wikipedia: History of the Roman Empire",
        "Britannica: Works of William Shakespeare",
        "Khan Academy: Basics of Microeconomics",
        "BBC: Latest World News",
        "Wikipedia: Social Media Trends"
    ]
}

# Templates (unchanged)
generic_templates = [
    "{} Studies", "{} Research", "{} Introduction", "{} Overview",
    "{} Advanced Concepts", "{} Practical Applications", "{} Analysis",
    "{} Theory", "{} Fundamentals", "{} Experimental Methods",
    "{} Principles", "{} Insights", "{} Perspectives", "{} Notes"
]

stem_tab_templates = generic_templates + [
    "{} Equations Explained", "{} Theoretical Models", "{} Problem Sets",
    "{} Case Studies", "{} Simulations", "{} Observational Data",
    "{} Mathematical Foundations", "{} Experimental Design",
    "{} Computational Techniques", "{} Research Papers",
    "{} Review", "{} Lecture Notes", "{} Seminar"
]

def add_noise(title, noise_prob=0.35):
    """Add realistic noise to tab titles with expanded synonyms."""
    words = title.split()
    if random.random() < noise_prob:
        synonyms = {
            "Quantum": ["QM", "Quantum Mech", "Q"], "Mechanics": ["Mech", "Dynamics"],
            "Relativity": ["Rel", "GR", "SR"], "Theory": ["Concepts", "Principles"],
            "Physics": ["Phys", "Science"], "Equations": ["Eqns", "Formulae"],
            "Astrophysics": ["Astro", "Cosmo"], "Thermodynamics": ["Thermo", "Heat"],
            "Wave": ["Waves", "Waveform"], "Energy": ["E", "Energy Flow"],
            "Field": ["Fields", "Field Theory"], "Entanglement": ["EPR", "Quantum Links"],
            "Chemistry": ["Chem", "Chemical"], "Biology": ["Bio", "Biological"],
            "Math": ["Mathematics", "Mathematical"], "Calculus": ["Calc", "Diff Calc"],
            "Geometry": ["Geom", "Shapes"], "Probability": ["Prob", "Stats"],
            "Algorithm": ["Algo", "Method"], "Data": ["Dataset", "Information"],
            "Network": ["Net", "Systems"], "AI": ["Artificial Intelligence", "ML"],
            "Circuit": ["Electronics", "Wiring"], "Material": ["Substance", "Matter"],
            "Anatomy": ["Body", "Structure"], "Disease": ["Illness", "Pathology"]
        }
        for i, word in enumerate(words):
            if word in synonyms and random.random() < 0.4:
                words[i] = random.choice(synonyms[word])
    if random.random() < noise_prob:
        generic = ["Intro to", "Overview of", "Basics of", "Notes on", "Guide to"]
        words.insert(0, random.choice(generic))
    if random.random() < 0.2:  # Add procedural word from vocab_banks
        subject = next((s for s, tops in all_topics.items() if any(t.lower() in title.lower() for t in tops)), "Non-STEM")
        extra_word = random.choice(vocab_banks.get(subject, ["study"])).capitalize()
        words.append(extra_word)
    if random.random() < 0.15:
        words = words[:max(1, len(words)//2 + 1)]
    return " ".join(words)

def generate_tab_titles(subject, topics, subtopics, templates, num_tabs, use_generic_prob=0.7, use_real_prob=0.3):
    """Generate tab titles with procedural mixing for variety."""
    titles = []
    used_topics = set()
    for _ in range(num_tabs):
        if random.random() < 0.2:  # Procedural title for "countless" fields
            vocab = vocab_banks.get(subject, vocab_banks["Non-STEM"])
            mixed_words = [random.choice(vocab).capitalize() for _ in range(2)]
            title = f"{mixed_words[0]} {mixed_words[1]} Overview"
        elif random.random() < use_real_prob and subject in real_titles and real_titles[subject]:
            title = random.choice(real_titles[subject])
        else:
            available_topics = [t for t in topics if t not in used_topics]
            if not available_topics:
                available_topics = topics
                used_topics.clear()
            topic = random.choice(available_topics)
            used_topics.add(topic)
            topic_variations = subtopics.get(topic, [topic])
            variation = random.choice(topic_variations)
            template = random.choice(generic_templates if random.random() < use_generic_prob else templates)
            title = template.format(variation)
        titles.append(add_noise(title))
    return titles

def generate_dataset(num_examples):
    """Generate an enlarged STEM dataset with alignment based on subjects and keywords."""
    data = []
    # More balanced tab counts
    tab_counts = [random.randint(1, 20) for _ in range(num_examples)]
    
    for i in range(num_examples):
        primary_subject = random.choice(stem_subjects)
        opened_subfield = random.choice(list(all_subfields[primary_subject].keys()))
        num_tabs = tab_counts[i]
        
        opened_tabs = []
        for _ in range(num_tabs):
            r = random.random()
            if r < 0.6:
                subject = primary_subject
                subfield = opened_subfield
            elif r < 0.9:
                subject = primary_subject
                other_subfields = [sf for sf in all_subfields[subject].keys() if sf != opened_subfield]
                if other_subfields:
                    subfield = random.choice(other_subfields)
                else:
                    subfield = opened_subfield
            else:
                subject = random.choice([s for s in stem_subjects if s != primary_subject])
                subfield = random.choice(list(all_subfields[subject].keys()))
            topics = all_subfields[subject][subfield]
            subtopics = all_subtopics[subject]
            opened_tabs.extend(generate_tab_titles(subject, topics, subtopics, stem_tab_templates, 1))
        
        # Generate new tab
        r = random.random()
        if r < 0.7:  # Same subject (likely on-task)
            new_subject = primary_subject
            rr = random.random()
            if rr < 0.7:
                new_subfield = opened_subfield
            else:
                new_subfield = random.choice(list(all_subfields[new_subject].keys()))
            new_topic = random.choice(all_subfields[new_subject][new_subfield])
            subtopics = all_subtopics[new_subject]
            templates = stem_tab_templates
        elif r < 0.95:  # Other STEM (possibly on-task)
            new_subject = random.choice([s for s in stem_subjects if s != primary_subject])
            new_subfield = random.choice(list(all_subfields[new_subject].keys()))
            new_topic = random.choice(all_subfields[new_subject][new_subfield])
            subtopics = all_subtopics[new_subject]
            templates = stem_tab_templates
        else:  # Non-STEM (likely off-task)
            new_subject = "Non-STEM"
            new_topic = random.choice(non_stem_topics)
            subtopics = all_subtopics["Non-STEM"]
            templates = generic_templates
        
        new_tab = generate_tab_titles(new_subject, [new_topic], subtopics, templates, 1)[0]
        
        # Compute alignment with keyword overlap
        def get_subject(tab):
            # Check topics
            for subj, tops in all_topics.items():
                for top in tops:
                    if top.lower() in tab.lower():
                        return subj
            # Check subtopics
            for subj, subt in all_subtopics.items():
                for t, slist in subt.items():
                    for sub in slist:
                        if sub.lower() in tab.lower():
                            return subj
            # Check vocab_banks keywords
            for subj, vocab in vocab_banks.items():
                if any(word.lower() in tab.lower() for word in vocab):
                    return subj
            return "Unknown"
        
        opened_subjects = [get_subject(tab) for tab in opened_tabs]
        opened_subjects = [s for s in opened_subjects if s != "Unknown"]
        if opened_subjects:
            primary_opened = max(set(opened_subjects), key=opened_subjects.count)
            proportion_same = opened_subjects.count(primary_opened) / len(opened_subjects)
        else:
            primary_opened = primary_subject
            proportion_same = 1.0
        
        new_subject_inf = get_subject(new_tab)
        # Keyword overlap check
        opened_keywords = set(word.lower() for tab in opened_tabs for word in tab.split() if word.lower() in sum(vocab_banks.values(), []))
        new_keywords = set(word.lower() for word in new_tab.split() if word.lower() in sum(vocab_banks.values(), []))
        shared_keywords = len(opened_keywords & new_keywords)
        
        if new_subject_inf == "Unknown" or new_subject_inf == "Non-STEM":
            alignment = 0
        elif new_subject_inf == primary_opened:
            alignment = 1 if random.random() < (0.95 if shared_keywords >= 2 else 0.9 if proportion_same >= 0.7 else 0.7) else 0
        else:
            alignment = 1 if random.random() < (0.5 if shared_keywords >= 2 else 0.3) else 0
        
        data.append({
            "opened_tabs": opened_tabs,
            "new_tab": new_tab,
            "alignment": alignment
        })
    
    random.shuffle(data)
    print("Sample dataset entries:")
    for i in range(min(3, len(data))):
        print(f"Example {i}:")
        print(f"  Opened tabs: {data[i]['opened_tabs']}")
        print(f"  New tab: {data[i]['new_tab']}")
        print(f"  Alignment: {data[i]['alignment']}")
    print("Alignment distribution:", {0: sum(1 for d in data if d["alignment"] == 0), 1: sum(1 for d in data if d["alignment"] == 1)})
    print("Tab count distribution:", {i: sum(1 for d in data if len(d["opened_tabs"]) == i) for i in range(1, 21)})
    return {"data": data}

def save_dataset(dataset, filename=None, default_dir="/Users/norranyu/Documents/coding/x_code/Durin/inference_engine/datasets/stem/"):
    """Save the dataset to a JSON file."""
    if not isinstance(dataset, dict) or "data" not in dataset:
        raise ValueError("Dataset must be a dictionary with a 'data' key containing a list of entries")
    
    data = dataset["data"]
    if filename is None:
        filename = os.path.join(default_dir, "stem_set.json")
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
    print(f"Dataset saved to {filename}")

def main():
    """Generate and save the dataset."""
    print("Enter the full path to save the dataset (press Enter for default)")
    user_input = input("Path: ").strip()
    dataset = generate_dataset(50000)
    save_dataset(dataset, filename=user_input or None)

if __name__ == "__main__":
    main()