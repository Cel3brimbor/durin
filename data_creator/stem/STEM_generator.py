# Credit: some tab titles are generated with Gemini 2.0, 2025, https://gemini.google.com/

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

physics_subfields = {
    "Quantum Physics": [
        "Quantum Mechanics", "Quantum Field Theory", "Quantum Computing",
        "Quantum Tunneling", "Quantum Entanglement", "Relativistic Quantum Mechanics"
    ],
    "Relativity": [
        "General Relativity", "Special Relativity", "Black Hole Physics",
        "Gravitational Waves", "Gravitational Physics"
    ],
    "Mechanics": [
        "Classical Mechanics", "Fluid Dynamics", "Mechanics of Materials",
        "Wave Mechanics", "Chaos Theory"
    ],
    "Thermodynamics": [
        "Thermodynamics", "Statistical Physics", "Thermal Radiation", "Nuclear Fusion"
    ],
    "Astrophysics": [
        "Astrophysics", "Cosmology", "Astrodynamics", "Dark Matter Studies",
        "Cosmic Microwave Background"
    ],
    "Particle Physics": [
        "Particle Physics", "High-Energy Physics", "Neutrino Physics", "Supersymmetry"
    ],
    "Condensed Matter": [
        "Solid State Physics", "Condensed Matter Physics", "Superconductivity",
        "Topological Insulators"
    ],
    "Electromagnetism": [
        "Electromagnetism", "Optics", "Photonics", "Plasma Physics"
    ],
    "Nuclear Physics": [
        "Nuclear Physics", "Nuclear Fusion"
    ]
}

physics_subtopics = {
    "Quantum Mechanics": ["Entanglement", "Superposition", "Heisenberg Uncertainty", "Wave-Particle Duality", "Schrödinger Equation", "Wave Functions"],
    "General Relativity": ["Black Holes", "Gravitational Waves", "Spacetime Curvature", "Einstein Field Equations", "Geodesics", "Energy-Momentum"],
    "Special Relativity": ["Time Dilation", "Length Contraction", "Lorentz Transformations", "Relativistic Energy", "Minkowski Spacetime", "Energy"],
    "Thermodynamics": ["Entropy", "Heat Transfer", "Carnot Cycle", "Thermal Equilibrium", "Gibbs Free Energy", "Energy"],
    "Particle Physics": ["Quarks", "Leptons", "Higgs Boson", "Standard Model", "Neutrinos", "Energy"],
    "Astrophysics": ["Stellar Evolution", "Galactic Dynamics", "Cosmic Rays", "Exoplanets", "Pulsars", "Cosmic Expansion"],
    "Electromagnetism": ["Maxwell’s Equations", "Electromagnetic Waves", "Coulomb’s Law", "Magnetic Fields", "Waves"],
    "Classical Mechanics": ["Newton’s Laws", "Lagrangian Mechanics", "Hamiltonian Mechanics", "Orbital Dynamics", "Mechanics"],
    "Optics": ["Refraction", "Diffraction", "Polarization", "Interference", "Lasers", "Waves"],
    "Solid State Physics": ["Crystal Structures", "Band Theory", "Semiconductors", "Phonons", "Energy Bands"],
    "Nuclear Physics": ["Nuclear Decay", "Fission", "Fusion Reactions", "Isotopes", "Nuclear Energy"],
    "Plasma Physics": ["Plasma Dynamics", "Magnetohydrodynamics", "Fusion Plasmas", "Debye Shielding", "Plasma Waves"],
    "Quantum Field Theory": ["Feynman Diagrams", "Gauge Theory", "Renormalization", "Path Integrals", "Fields"],
    "Chaos Theory": ["Nonlinear Dynamics", "Bifurcations", "Attractors", "Lyapunov Exponents", "Chaos"],
    "String Theory": ["M-Theory", "Branes", "Extra Dimensions", "String Vibrations", "Quantum Gravity"],
    "Fluid Dynamics": ["Navier-Stokes Equations", "Turbulence", "Viscosity", "Bernoulli’s Principle", "Wave Mechanics"],
    "Cosmology": ["Big Bang", "Inflation", "Dark Energy", "Cosmic Expansion", "Cosmic Structure"],
    "Quantum Computing": ["Qubits", "Quantum Gates", "Superposition", "Quantum Algorithms", "Quantum Circuits"],
    "Statistical Physics": ["Partition Functions", "Boltzmann Distribution", "Phase Transitions", "Statistical Mechanics"],
    "Astrodynamics": ["Orbital Mechanics", "Kepler’s Laws", "Spacecraft Trajectories", "Orbital Energy"],
    "Black Hole Physics": ["Event Horizon", "Hawking Radiation", "Schwarzschild Metric", "Black Hole Entropy"],
    "Quantum Tunneling": ["Tunneling Effect", "Barrier Penetration", "Quantum Wells", "Tunneling"],
    "Condensed Matter Physics": ["Superfluidity", "Bose-Einstein Condensates", "Quantum Phase Transitions", "Condensed Matter"],
    "High-Energy Physics": ["Collider Experiments", "Particle Accelerators", "Dark Matter Detection", "High Energy"],
    "Relativistic Quantum Mechanics": ["Dirac Equation", "Klein-Gordon Equation", "Spinors", "Relativistic Fields"],
    "Thermal Radiation": ["Blackbody Radiation", "Planck’s Law", "Stefan-Boltzmann Law", "Radiation Energy"],
    "Mechanics of Materials": ["Stress-Strain", "Elasticity", "Fracture Mechanics", "Material Mechanics"],
    "Wave Mechanics": ["Wave Functions", "Harmonic Oscillators", "Wave Propagation", "Waves"],
    "Nuclear Fusion": ["Fusion Reactors", "Tokamaks", "Inertial Confinement", "Fusion Energy"],
    "Gravitational Physics": ["Gravitational Lensing", "Frame Dragging", "Equivalence Principle", "Gravitation"],
    "Superconductivity": ["Meissner Effect", "Cooper Pairs", "High-Tc Superconductors", "Superconducting States"],
    "Dark Matter Studies": ["WIMPs", "Dark Matter Halos", "Indirect Detection", "Dark Matter"],
    "Neutrino Physics": ["Neutrino Oscillations", "Solar Neutrinos", "Neutrino Masses", "Neutrinos"],
    "Holographic Principle": ["AdS/CFT Correspondence", "Holographic Entropy", "Information Paradox", "Holography"],
    "Quantum Entanglement": ["Bell States", "Nonlocality", "EPR Paradox", "Entangled Systems"],
    "Cosmic Microwave Background": ["CMB Anisotropies", "Planck Satellite", "Cosmic Inflation", "CMB Radiation"],
    "Supersymmetry": ["SUSY Particles", "Superpartners", "MSSM", "Supersymmetric Fields"],
    "Topological Insulators": ["Edge States", "Topological Order", "Quantum Spin Hall Effect", "Topology"],
    "Gravitational Waves": ["LIGO Observations", "Waveform Analysis", "Binary Mergers", "Gravitational Signals"],
    "Photonics": ["Photonic Crystals", "Optical Waveguides", "Nonlinear Optics", "Photonic Systems"]
}

# Chemistry topics and structures
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
    "Inorganic Chemistry": ["Periodic Table", "Coordination Complexes", "Transition Metals", "Main Group Elements", "Crystal Field Theory"],
    "Physical Chemistry": ["Thermodynamics", "Quantum Mechanics", "Statistical Mechanics", "Kinetics", "Equilibrium"],
    "Biochemistry": ["Proteins", "Carbohydrates", "Lipids", "Nucleic Acids", "Enzymes", "Metabolism"],
    "Analytical Chemistry": ["Titration", "Spectrometry", "Electroanalysis", "Separation Techniques", "Qualitative Analysis"],
    "Polymer Chemistry": ["Polymerization", "Polymers", "Copolymers", "Polymer Properties", "Biodegradable Polymers"],
    "Electrochemistry": ["Redox Reactions", "Electrodes", "Batteries", "Corrosion", "Electrolytes"],
    "Quantum Chemistry": ["Molecular Orbitals", "Hartree-Fock", "Density Functional Theory", "Ab Initio Methods", "Basis Sets"],
    "Chemical Kinetics": ["Rate Laws", "Activation Energy", "Catalysis", "Reaction Orders", "Integrated Rate Laws"],
    "Spectroscopy": ["UV-Vis", "IR Spectroscopy", "NMR", "Mass Spec", "Raman Spectroscopy"],
    "Surface Chemistry": ["Adsorption", "Catalysis", "Colloids", "Interfaces", "Surfactants"],
    "Environmental Chemistry": ["Pollution", "Water Treatment", "Atmospheric Chemistry", "Soil Chemistry", "Green Solvents"],
    "Medicinal Chemistry": ["Drug Design", "Pharmacokinetics", "SAR", "Bioactive Compounds", "Antibiotics"],
    "Nanochemistry": ["Nanoparticles", "Nanotubes", "Quantum Dots", "Self-Assembly", "Nanomaterials"],
    "Theoretical Chemistry": ["Molecular Dynamics", "Monte Carlo Simulations", "Potential Energy Surfaces", "Reaction Paths"],
    "Organometallic Chemistry": ["Metal-Carbon Bonds", "Catalysts", "Grignard Reagents", "Ferrocene", "Ziegler-Natta"],
    "Green Chemistry": ["Sustainable Synthesis", "Atom Economy", "Renewable Feedstocks", "Biocatalysis", "Solvent-Free"],
    "Photochemistry": ["Photons", "Excited States", "Fluorescence", "Photosynthesis", "Photocatalysis"],
    "Supramolecular Chemistry": ["Host-Guest", "Molecular Recognition", "Self-Assembly", "Crown Ethers", "Cyclodextrins"],
    "Computational Chemistry": ["DFT", "Molecular Modeling", "QM/MM", "Solvation Models", "Energy Calculations"]
}

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
    "Genetics": ["DNA Structure", "Gene Expression", "Mutations", "Inheritance Patterns", "Genetic Engineering", "Chromosomes"],
    "Evolution": ["Darwinism", "Natural Selection", "Fossils", "Adaptive Radiation", "Molecular Evolution", "Speciation"],
    "Ecology": ["Food Webs", "Biomes", "Succession", "Population Growth", "Symbiosis", "Biodiversity"],
    "Microbiology": ["Bacteria", "Viruses", "Fungi", "Protists", "Microbial Genetics", "Antibiotics"],
    "Botany": ["Photosynthesis", "Plant Anatomy", "Plant Reproduction", "Hormones", "Plant Ecology", "Roots"],
    "Zoology": ["Animal Behavior", "Animal Physiology", "Invertebrates", "Vertebrates", "Animal Development", "Migration"],
    "Neuroscience": ["Neurons", "Synapses", "Brain Structure", "Neurotransmitters", "Neural Circuits", "Memory"],
    "Molecular Biology": ["Replication", "Transcription", "Translation", "PCR", "Cloning", "Sequencing"],
    "Physiology": ["Homeostasis", "Circulation", "Respiration", "Digestion", "Excretion", "Muscle Contraction"],
    "Immunology": ["Antibodies", "T Cells", "B Cells", "Vaccines", "Autoimmunity", "Allergies"],
    "Biotechnology": ["GMOs", "CRISPR", "Cloning", "Stem Cells", "Biofuels", "Bioremediation"],
    "Developmental Biology": ["Embryogenesis", "Morphogenesis", "Differentiation", "Apoptosis", "Regeneration"],
    "Bioinformatics": ["Sequence Alignment", "Genomics", "Proteomics", "Databases", "Phylogenetics"],
    "Endocrinology": ["Hormones", "Glands", "Feedback Loops", "Thyroid", "Adrenal", "Insulin"],
    "Virology": ["Viral Replication", "HIV", "Influenza", "Viral Vectors", "Antivirals"],
    "Parasitology": ["Parasites", "Life Cycles", "Malaria", "Helminths", "Protozoa"],
    "Mycology": ["Fungi", "Mycorrhizae", "Yeasts", "Molds", "Pathogenic Fungi"],
    "Marine Biology": ["Ocean Ecosystems", "Coral Reefs", "Marine Mammals", "Plankton", "Deep Sea"],
    "Conservation Biology": ["Endangered Species", "Habitat Loss", "Protected Areas", "Restoration", "Invasive Species"]
}

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
    "Calculus": ["Derivatives", "Integrals", "Limits", "Series", "Multivariable", "Applications"],
    "Geometry": ["Shapes", "Theorems", "Coordinate Geometry", "Trigonometry", "Conic Sections", "Proofs"],
    "Probability": ["Random Variables", "Distributions", "Expected Value", "Bayes Theorem", "Markov Chains", "Variance"],
    "Statistics": ["Hypothesis Testing", "Regression", "Confidence Intervals", "ANOVA", "Data Analysis", "Sampling"],
    "Number Theory": ["Primes", "Modular Arithmetic", "Fermat's Theorem", "RSA Cryptography", "Divisibility"],
    "Topology": ["Open Sets", "Continuous Functions", "Compactness", "Connectedness", "Manifolds", "Homotopy"],
    "Differential Equations": ["First Order", "Second Order", "Laplace Transforms", "Systems of DEs", "Boundary Value"],
    "Linear Algebra": ["Vector Spaces", "Eigenvalues", "Determinants", "Linear Transformations", "Inner Products"],
    "Abstract Algebra": ["Rings", "Fields", "Groups", "Homomorphisms", "Ideals"],
    "Real Analysis": ["Sequences", "Series", "Continuity", "Differentiability", "Integration"],
    "Complex Analysis": ["Analytic Functions", "Contour Integrals", "Residues", "Conformal Mapping", "Laurent Series"],
    "Discrete Mathematics": ["Sets", "Relations", "Functions", "Logic", "Proof Techniques"],
    "Graph Theory": ["Vertices", "Edges", "Paths", "Cycles", "Trees", "Coloring"],
    "Combinatorics": ["Permutations", "Combinations", "Binomial Coefficients", "Pigeonhole Principle", "Generating Functions"],
    "Mathematical Logic": ["Propositions", "Predicates", "Quantifiers", "Proof Systems", "Gödel's Theorem"],
    "Game Theory": ["Nash Equilibrium", "Zero-Sum Games", "Prisoner's Dilemma", "Strategies", "Payoffs"],
    "Numerical Analysis": ["Interpolation", "Root Finding", "Numerical Integration", "Error Analysis", "Approximations"],
    "Optimization": ["Linear Programming", "Nonlinear Optimization", "Gradient Descent", "Constraints", "Lagrange Multipliers"],
    "Fourier Analysis": ["Fourier Series", "Transforms", "FFT", "Wavelets", "Signal Processing"]
}

non_stem_topics = [
    "World History", "American Literature", "Microeconomics", "Cognitive Psychology", "Art History",
    "Philosophy of Mind", "Sociology of Education", "Political Theory", "Music Theory", "Linguistics",
    "Cultural Anthropology", "Human Geography", "Constitutional Law", "Business Management", "Journalism Ethics"
]

non_stem_subtopics = {
    "World History": ["WWII", "Renaissance", "Industrial Revolution", "Cold War", "Ancient Egypt", "Middle Ages"],
    "American Literature": ["Hemingway", "Faulkner", "Poetry", "Novels", "Literary Criticism", "Modernism"],
    "Microeconomics": ["Supply and Demand", "Market Structures", "Elasticity", "Consumer Behavior", "Production Costs"],
    "Cognitive Psychology": ["Memory", "Perception", "Learning", "Decision Making", "Intelligence", "Attention"],
    "Art History": ["Impressionism", "Baroque", "Modern Art", "Sculpture", "Architecture", "Renaissance Masters"],
    "Philosophy of Mind": ["Consciousness", "Dualism", "Materialism", "Intentionality", "Qualia"],
    "Sociology of Education": ["Social Mobility", "Inequality", "School Systems", "Cultural Capital", "Tracking"],
    "Political Theory": ["Democracy", "Liberalism", "Marxism", "Feminism", "Social Contract"],
    "Music Theory": ["Harmony", "Scales", "Rhythm", "Composition", "Notation"],
    "Linguistics": ["Phonetics", "Syntax", "Semantics", "Morphology", "Pragmatics"],
    "Cultural Anthropology": ["Ethnography", "Kinship", "Rituals", "Cultural Relativism", "Globalization"],
    "Human Geography": ["Urbanization", "Migration", "Cultural Landscapes", "Population Distribution", "Geopolitics"],
    "Constitutional Law": ["Bill of Rights", "Judicial Review", "Federalism", "Amendments", "Supreme Court Cases"],
    "Business Management": ["Leadership", "Organizational Behavior", "Strategy", "HR Management", "Operations"],
    "Journalism Ethics": ["Objectivity", "Freedom of Press", "Privacy", "Sensationalism", "Fact-Checking"]
}

stem_subjects = ["Physics", "Chemistry", "Biology", "Math"]

all_subfields = {
    "Physics": physics_subfields,
    "Chemistry": chemistry_subfields,
    "Biology": biology_subfields,
    "Math": math_subfields
}

all_subtopics = {
    "Physics": physics_subtopics,
    "Chemistry": chemistry_subtopics,
    "Biology": biology_subtopics,
    "Math": math_subtopics,
    "Non-STEM": non_stem_subtopics
}

all_topics = {
    "Physics": physics_topics,
    "Chemistry": chemistry_topics,
    "Biology": biology_topics,
    "Math": math_topics,
    "Non-STEM": non_stem_topics
}

real_titles = {
    "Physics": [
        "arXiv: Quantum Field Theory in Curved Spacetime",
        "Wikipedia: Lorentz Transformations in Special Relativity",
        "MIT OCW: Thermodynamics Lecture Notes",
        "Nature: Gravitational Wave Detection by LIGO",
        "APS: Advances in Superconductivity Research",
        "arXiv: Neutrino Oscillations in Dense Matter",
        "SciAm: The Physics of Black Holes",
        "PRL: Quantum Entanglement in Many-Body Systems",
        "JCAP: Dark Matter Constraints from CMB Data",
        "PhysRevD: Relativistic Hydrodynamics in Heavy-Ion Collisions",
        "arXiv: AdS/CFT Correspondence and Holography",
        "PRB: Topological Insulators in Condensed Matter",
        "JHEP: Supersymmetry in High-Energy Physics",
        "ApJ: Stellar Dynamics in Galactic Nuclei",
        "PhysRevLett: Quantum Tunneling in Nanostructures"
    ],
    "Chemistry": [
        "arXiv: Advances in Quantum Chemistry Methods",
        "Wikipedia: Chemical Bonding",
        "ACS: Review of Organic Synthesis",
        "Nature Chemistry: Nanomaterials and Catalysis",
        "JACS: Recent Advances in Photocatalysis",
        "ChemRev: Electrochemistry Fundamentals",
        "SciAm: Green Chemistry Principles",
        "PCCP: Surface Chemistry Simulations",
        "Angewandte: Supramolecular Assemblies",
        "arXiv: Computational Modeling of Reactions"
    ],
    "Biology": [
        "Wikipedia: DNA Replication",
        "Nature: CRISPR-Cas9 Gene Editing",
        "Cell: Molecular Mechanisms of Cancer",
        "PNAS: Evolutionary Dynamics",
        "Science: Ecology of Climate Change",
        "PLoS: Neuroscience of Learning",
        "BioRxiv: Bioinformatics Tools",
        "Trends in Ecology: Conservation Strategies",
        "JMB: Protein Structure Prediction",
        "arXiv: Virology of Emerging Pathogens"
    ],
    "Math": [
        "arXiv: Recent Advances in Algebraic Geometry",
        "Wikipedia: Fundamental Theorem of Calculus",
        "AMS: Probability Theory and Applications",
        "MathWorld: Topology Basics",
        "SIAM: Numerical Methods for ODEs",
        "arXiv: Graph Theory Algorithms",
        "JMP: Statistical Modeling",
        "Annals: Real Analysis Proofs",
        "Combinatorica: Combinatorial Optimization",
        "arXiv: Game Theory in Economics"
    ],
    "Non-STEM": [
        "Wikipedia: History of the Roman Empire",
        "Britannica: Works of William Shakespeare",
        "Khan Academy: Basics of Microeconomics",
        "Psychology Today: Cognitive Biases",
        "Wikipedia: Renaissance Art",
        "Stanford Encyclopedia: Philosophy of Mind",
        "Wikipedia: Sociological Theories",
        "Britannica: Political Ideologies",
        "Wikipedia: Elements of Music Theory",
        "Khan Academy: Introduction to Linguistics"
    ]
}

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

def add_noise(title, noise_prob=0.25):
    """add realistic noise to tab titles"""
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
            "Geometry": ["Geom", "Shapes"], "Probability": ["Prob", "Stats"]
        }
        for i, word in enumerate(words):
            if word in synonyms and random.random() < 0.4:
                words[i] = random.choice(synonyms[word])
    if random.random() < noise_prob:
        generic = ["Intro to", "Overview of", "Basics of", "Notes on", "Guide to"]
        words.insert(0, random.choice(generic))
    if random.random() < 0.15:  # 15% chance for partial title
        words = words[:max(1, len(words)//2 + 1)] #truncate
    return " ".join(words)

def generate_tab_titles(subject, topics, subtopics, templates, num_tabs, use_generic_prob=0.7, use_real_prob=0.3):
    """Generate a list of tab titles with variety and noise."""
    titles = []
    used_topics = set()
    for _ in range(num_tabs):
        if random.random() < use_real_prob and subject in real_titles and real_titles[subject]:
            title = random.choice(real_titles[subject])
            titles.append(add_noise(title))
            continue
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
    """generate an enlarged STEM dataset with alignment based on subjects"""
    data = []
    tab_counts = random.choices(
        range(1, 21), weights=[0.05, 0.1, 0.12, 0.15, 0.15, 0.12, 0.1, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01], k=num_examples
    )
    random.shuffle(tab_counts)
    
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
        
        r = random.random()
        if r < 0.7:  # strong: same subject
            new_subject = primary_subject
            rr = random.random()
            if rr < 0.7:
                new_subfield = opened_subfield
            else:
                new_subfield = random.choice(list(all_subfields[new_subject].keys()))
            new_topic = random.choice(all_subfields[new_subject][new_subfield])
            subtopics = all_subtopics[new_subject]
            templates = stem_tab_templates
        elif r < 0.95:  # medium: other STEM
            new_subject = random.choice([s for s in stem_subjects if s != primary_subject])
            new_subfield = random.choice(list(all_subfields[new_subject].keys()))
            new_topic = random.choice(all_subfields[new_subject][new_subfield])
            subtopics = all_subtopics[new_subject]
            templates = stem_tab_templates
        else:  #weak: non-STEM
            new_subject = "Non-STEM"
            new_topic = random.choice(non_stem_topics)
            subtopics = all_subtopics["Non-STEM"]
            templates = generic_templates
        
        new_tab = generate_tab_titles(new_subject, [new_topic], subtopics, templates, 1)[0]
        
        #compute alignment
        def get_subject(tab):
            for subj, tops in all_topics.items():
                for top in tops:
                    if top.lower() in tab.lower():
                        return subj
            for subj, subt in all_subtopics.items():
                for t, slist in subt.items():
                    for sub in slist:
                        if sub.lower() in tab.lower():
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
        if new_subject_inf == "Unknown":
            alignment = 0
        elif new_subject_inf == "Non-STEM":
            alignment = 0
        elif new_subject_inf == primary_opened:
            #strongest for same subject
            if proportion_same >= 0.7:
                alignment = 1 if random.random() < 0.9 else 0
            else:
                alignment = 1 if random.random() < 0.7 else 0
        else:
            #less strong for other STEM
            alignment = 1 if random.random() < 0.3 else 0
        
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

def save_dataset(dataset, filename=None, default_dir="/Users/norranyu/Documents/coding/x_code/git_repo/inference_engine/datasets/stem"):
    if not isinstance(dataset, dict) or "data" not in dataset:
        raise ValueError("Dataset must be a dictionary with a 'data' key containing a list of entries")
    
    data = dataset["data"]
    if filename is None:
        filename = os.path.join(default_dir, "stem_dataset1.json")
    output_dir = os.path.dirname(filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, indent=2)
    print(f"Dataset saved to {filename}")

def main():
    """Generate and save the dataset."""
    print("Enter the full path to save the dataset (or press enter for default): ")
    user_input = input("Path: ").strip()
    dataset = generate_dataset(50000)
    save_dataset(dataset, filename=user_input or None)

if __name__ == "__main__":
    main()