"""Academic study-session dataset generator.

Creates examples that match the physics/STEM schema (opened tabs around one
focus, a newly opened tab, and an on-task score/label) and writes a TSV .txt
file that bert_finetune/main.py can load:

    text<TAB>label

Opened tabs share a single academic focus (a subfield). The new tab is either
on that focus or a distraction. Labels are assigned from the intended relation,
not keyword matching, so BERT can learn semantic on-task vs off-task.
"""

from __future__ import annotations

import argparse
import json
import os
import random
from pathlib import Path

HERE = Path(__file__).resolve().parent

# subject -> course codes, typical sources, and subfield -> topic -> subtopics
ACADEMIC = {
    "History": {
        "codes": ["HIST", "HIS", "HST"],
        "sources": ["JSTOR", "Library of Congress", "Archive.org", "Britannica", "American Historical Review"],
        "subfields": {
            "Ancient History": {
                "Ancient Egypt": ["Pyramids", "Pharaohs", "Hieroglyphs", "Nile Civilization", "Tutankhamun"],
                "Ancient Rome": ["Roman Republic", "Julius Caesar", "Punic Wars", "Roman Law", "Augustus"],
                "Ancient Greece": ["Athens and Sparta", "Peloponnesian War", "Alexander the Great", "Greek Democracy", "Hellenistic World"],
                "Mesopotamia": ["Sumer", "Hammurabi", "Cuneiform", "Babylon", "Assyrian Empire"],
            },
            "Medieval History": {
                "Medieval Europe": ["Feudalism", "Black Death", "Crusades", "Holy Roman Empire", "Manorialism"],
                "Byzantine Empire": ["Justinian", "Constantinople", "Eastern Orthodoxy", "Byzantine Law", "Iconoclasm"],
                "Islamic Golden Age": ["Abbasid Caliphate", "House of Wisdom", "Al-Andalus", "Trade Networks", "Islamic Scholarship"],
            },
            "Early Modern History": {
                "Renaissance": ["Humanism", "Italian City-States", "Medici Florence", "Printing Press", "Renaissance Diplomacy"],
                "Reformation": ["Martin Luther", "Calvinism", "Catholic Reformation", "Wars of Religion", "Council of Trent"],
                "Age of Exploration": ["Columbian Exchange", "Atlantic Trade", "Portuguese Voyages", "Spanish Empire", "Mercantilism"],
            },
            "United States History": {
                "American Revolution": ["Continental Congress", "Declaration of Independence", "Revolutionary War", "Constitutional Convention", "Federalists"],
                "Civil War Era": ["Slavery", "Abraham Lincoln", "Reconstruction", "Gettysburg", "Emancipation"],
                "Twentieth-Century America": ["New Deal", "Civil Rights Movement", "Cold War at Home", "Great Society", "Vietnam War"],
            },
            "Modern World History": {
                "World War I": ["Trench Warfare", "Treaty of Versailles", "Home Front", "Alliances", "Russian Revolution"],
                "World War II": ["Holocaust", "Pacific Theater", "D-Day", "Home Front Mobilization", "United Nations"],
                "Cold War": ["Iron Curtain", "Cuban Missile Crisis", "Decolonization", "Proxy Wars", "Fall of the Soviet Union"],
            },
        },
    },
    "Literature": {
        "codes": ["ENGL", "LIT", "ENG"],
        "sources": ["JSTOR", "MLA Commons", "Poetry Foundation", "Project Gutenberg", "Norton Anthology"],
        "subfields": {
            "American Literature": {
                "Nineteenth-Century American": ["Hawthorne", "Melville", "Dickinson", "Whitman", "Slave Narratives"],
                "Modern American Fiction": ["Hemingway", "Faulkner", "Fitzgerald", "Hurston", "Modernism"],
                "Contemporary American": ["Morrison", "Baldwin", "Postmodern Novel", "Short Story", "Creative Nonfiction"],
            },
            "British Literature": {
                "Shakespeare": ["Hamlet", "Macbeth", "Sonnets", "Elizabethan Stage", "King Lear"],
                "Romantic Poetry": ["Wordsworth", "Keats", "Byron", "Romantic Sublime", "Lyrical Ballads"],
                "Victorian Novel": ["Dickens", "Bronte", "Eliot", "Industrial Novel", "Gothic Fiction"],
            },
            "Literary Theory": {
                "Narrative Theory": ["Plot Structure", "Narration", "Free Indirect Discourse", "Focalization", "Genre"],
                "Critical Theory": ["Marxism", "Feminism", "Postcolonial Theory", "New Historicism", "Reader Response"],
                "Poetics": ["Meter", "Imagery", "Metaphor", "Form", "Close Reading"],
            },
            "World Literature": {
                "Classical Epic": ["Homer", "Virgil", "Epic Conventions", "Oral Tradition", "Odyssey"],
                "Postcolonial Literature": ["Achebe", "Rushdie", "Caribbean Writing", "National Allegory", "Hybridity"],
                "World Novel": ["Magical Realism", "Translation Studies", "Global Modernism", "Testimony", "Comparative Novel"],
            },
        },
    },
    "Philosophy": {
        "codes": ["PHIL", "PHI", "PHL"],
        "sources": ["Stanford Encyclopedia", "Internet Encyclopedia of Philosophy", "JSTOR", "PhilPapers", "Oxford Handbooks"],
        "subfields": {
            "Ethics": {
                "Normative Ethics": ["Utilitarianism", "Kantian Ethics", "Virtue Ethics", "Moral Particularism", "Contractualism"],
                "Applied Ethics": ["Bioethics", "Animal Ethics", "Just War Theory", "Environmental Ethics", "AI Ethics"],
                "Metaethics": ["Moral Realism", "Expressivism", "Error Theory", "Reasons", "Moral Motivation"],
            },
            "Metaphysics and Epistemology": {
                "Epistemology": ["Justification", "Skepticism", "Gettier Problems", "Internalism", "Testimony"],
                "Metaphysics": ["Causation", "Free Will", "Personal Identity", "Possible Worlds", "Universals"],
                "Philosophy of Science": ["Explanation", "Induction", "Scientific Realism", "Kuhn", "Falsification"],
            },
            "Political Philosophy": {
                "Social Contract": ["Hobbes", "Locke", "Rousseau", "Consent", "State of Nature"],
                "Justice": ["Rawls", "Nozick", "Equality", "Distributive Justice", "Capabilities"],
                "Power and Freedom": ["Liberty", "Republicanism", "Marx", "Foucault", "Civil Disobedience"],
            },
            "Philosophy of Mind": {
                "Consciousness": ["Qualia", "Hard Problem", "Physicalism", "Dualism", "Intentionality"],
                "Mental Content": ["Functionalism", "Representation", "Folk Psychology", "Mental Causation", "Self-Knowledge"],
            },
        },
    },
    "Economics": {
        "codes": ["ECON", "ECO", "ECN"],
        "sources": ["NBER", "JSTOR", "FRED", "Quarterly Journal of Economics", "Khan Academy"],
        "subfields": {
            "Microeconomics": {
                "Consumer Theory": ["Utility", "Demand Curves", "Elasticity", "Revealed Preference", "Income Effects"],
                "Market Structure": ["Perfect Competition", "Monopoly", "Oligopoly", "Game Theory", "Price Discrimination"],
                "Welfare and Public Goods": ["Externalities", "Public Goods", "Deadweight Loss", "Pigouvian Taxes", "Coase Theorem"],
            },
            "Macroeconomics": {
                "Growth": ["Solow Model", "Productivity", "Human Capital", "Convergence", "Endogenous Growth"],
                "Business Cycles": ["IS-LM", "AD-AS", "Unemployment", "Inflation", "Stabilization Policy"],
                "Monetary and Fiscal": ["Federal Reserve", "Interest Rates", "Government Spending", "Deficits", "Taylor Rule"],
            },
            "Econometrics": {
                "Regression": ["OLS", "Omitted Variable Bias", "Instrumental Variables", "Fixed Effects", "Standard Errors"],
                "Causal Inference": ["Difference in Differences", "RDD", "Experiments", "Selection Bias", "Matching"],
            },
            "Development Economics": {
                "Poverty": ["Poverty Traps", "Human Development", "Microfinance", "Health and Education", "Inequality"],
                "Institutions and Trade": ["Property Rights", "Colonial Origins", "Comparative Advantage", "Trade Policy", "Aid"],
            },
        },
    },
    "Political Science": {
        "codes": ["POLI", "PSCI", "GOVT", "POLS"],
        "sources": ["APSR", "JSTOR", "Brookings", "Congressional Research Service", "Foreign Affairs"],
        "subfields": {
            "American Politics": {
                "Congress": ["Committees", "Polarization", "Legislation", "Elections", "Representation"],
                "Presidency": ["Executive Power", "Vetoes", "Unilateral Action", "Public Opinion", "White House"],
                "Courts and Parties": ["Supreme Court", "Judicial Review", "Party Systems", "Interest Groups", "Campaigns"],
            },
            "Comparative Politics": {
                "Regimes": ["Democracy", "Authoritarianism", "Democratization", "Hybrid Regimes", "State Capacity"],
                "Institutions": ["Electoral Systems", "Federalism", "Parliamentary Systems", "Parties", "Constitutions"],
                "Political Economy": ["Welfare States", "Development", "Corruption", "Resource Curse", "Inequality"],
            },
            "Political Theory": {
                "Liberalism": ["Rights", "Pluralism", "Mill", "Public Reason", "Toleration"],
                "Democratic Theory": ["Deliberation", "Representation", "Populism", "Citizenship", "Participation"],
            },
            "Public Policy": {
                "Policy Process": ["Agenda Setting", "Implementation", "Evaluation", "Bureaucratic Politics", "Regulation"],
                "Domestic Policy": ["Health Policy", "Education Policy", "Immigration Policy", "Criminal Justice Policy", "Tax Policy"],
            },
        },
    },
    "Psychology": {
        "codes": ["PSYC", "PSY", "PSYCH"],
        "sources": ["APA PsycNet", "PubMed", "Psychological Review", "Annual Review of Psychology", "Simply Psychology"],
        "subfields": {
            "Cognitive Psychology": {
                "Memory": ["Working Memory", "Long-Term Memory", "Encoding", "Retrieval", "False Memory"],
                "Attention": ["Selective Attention", "Cognitive Load", "Dual Task", "Inattentional Blindness", "Executive Control"],
                "Thinking": ["Problem Solving", "Decision Making", "Heuristics", "Concepts", "Language Processing"],
            },
            "Developmental Psychology": {
                "Childhood": ["Attachment", "Piaget", "Theory of Mind", "Language Acquisition", "Play"],
                "Adolescence and Aging": ["Identity", "Peer Influence", "Cognitive Aging", "Socioemotional Development", "Lifespan"],
            },
            "Social Psychology": {
                "Attitudes": ["Persuasion", "Cognitive Dissonance", "Prejudice", "Stereotypes", "Implicit Bias"],
                "Social Influence": ["Conformity", "Obedience", "Group Behavior", "Helping", "Aggression"],
            },
            "Clinical Psychology": {
                "Psychopathology": ["Depression", "Anxiety Disorders", "Schizophrenia", "DSM", "Comorbidity"],
                "Treatment": ["CBT", "Psychotherapy", "Assessment", "Evidence-Based Practice", "Clinical Trials"],
            },
        },
    },
    "Sociology": {
        "codes": ["SOCI", "SOC", "SOCL"],
        "sources": ["ASR", "JSTOR", "Annual Review of Sociology", "Census Bureau", "Pew Research"],
        "subfields": {
            "Social Theory": {
                "Classical Theory": ["Marx", "Weber", "Durkheim", "Social Facts", "Rationalization"],
                "Contemporary Theory": ["Bourdieu", "Intersectionality", "Symbolic Interaction", "Foucault", "Habitus"],
            },
            "Inequality": {
                "Class and Stratification": ["Social Mobility", "Poverty", "Occupational Prestige", "Capital", "Labor Markets"],
                "Race and Gender": ["Racial Formation", "Gender Roles", "Discrimination", "Intersectionality", "Family Structure"],
            },
            "Institutions": {
                "Education and Family": ["Tracking", "Cultural Capital", "Schooling", "Marriage", "Households"],
                "Organizations": ["Bureaucracy", "Networks", "Work", "Professions", "Institutional Isomorphism"],
            },
            "Culture and Media": {
                "Culture": ["Cultural Sociology", "Taste", "Religion", "Collective Memory", "Ritual"],
                "Media": ["Public Sphere", "Social Media", "Framing", "Audience", "News Production"],
            },
        },
    },
    "Linguistics": {
        "codes": ["LING", "LIN", "CLNG"],
        "sources": ["Language Journal", "Glossa", "JSTOR", "WALS", "Linguistic Inquiry"],
        "subfields": {
            "Phonetics and Phonology": {
                "Phonetics": ["IPA", "Articulation", "Acoustic Phonetics", "Vowels", "Spectrograms"],
                "Phonology": ["Phonemes", "Distinctive Features", "Syllables", "Stress", "Optimality Theory"],
            },
            "Syntax and Semantics": {
                "Syntax": ["Phrase Structure", "Movement", "Agreement", "Constituency", "Generative Grammar"],
                "Semantics": ["Compositionality", "Quantifiers", "Truth Conditions", "Presupposition", "Lambda Calculus"],
            },
            "Sociolinguistics": {
                "Variation": ["Dialects", "Code Switching", "Register", "Language Attitudes", "Style"],
                "Language and Society": ["Language Policy", "Pidgins and Creoles", "Gendered Speech", "Multilingualism", "Standardization"],
            },
            "Historical Linguistics": {
                "Change": ["Sound Change", "Grammaticalization", "Cognates", "Reconstruction", "Language Families"],
                "Indo-European": ["Proto-Indo-European", "Comparative Method", "Latin to Romance", "Grimm's Law", "Etymology"],
            },
        },
    },
    "Law": {
        "codes": ["LAW", "JURI", "LEGL"],
        "sources": ["Cornell LII", "Oyez", "Westlaw", "Harvard Law Review", "SCOTUSblog"],
        "subfields": {
            "Constitutional Law": {
                "Structure": ["Separation of Powers", "Federalism", "Judicial Review", "Commerce Clause", "Executive Power"],
                "Rights": ["First Amendment", "Equal Protection", "Due Process", "Fourth Amendment", "Incorporation"],
            },
            "Criminal Law": {
                "Doctrine": ["Actus Reus", "Mens Rea", "Homicide", "Inchoate Offenses", "Defenses"],
                "Procedure": ["Search and Seizure", "Miranda", "Plea Bargaining", "Evidence", "Sentencing"],
            },
            "Private Law": {
                "Contracts": ["Offer and Acceptance", "Consideration", "Remedies", "Breach", "Parol Evidence"],
                "Torts": ["Negligence", "Strict Liability", "Defamation", "Damages", "Causation"],
            },
            "International Law": {
                "Public International": ["Treaties", "Sovereignty", "Human Rights Law", "Use of Force", "ICJ"],
                "International Institutions": ["UN Charter", "WTO", "International Criminal Court", "Customary Law", "State Responsibility"],
            },
        },
    },
    "Art History": {
        "codes": ["ARTH", "AHIS", "ART"],
        "sources": ["Grove Art", "Metropolitan Museum", "JSTOR", "Art Bulletin", "Smarthistory"],
        "subfields": {
            "Ancient and Medieval Art": {
                "Classical Art": ["Greek Sculpture", "Roman Architecture", "Parthenon", "Portraiture", "Mosaics"],
                "Medieval Art": ["Byzantine Icons", "Gothic Cathedrals", "Manuscript Illumination", "Romanesque", "Reliquaries"],
            },
            "Renaissance and Baroque": {
                "Italian Renaissance": ["Leonardo", "Michelangelo", "Perspective", "Patronage", "Florence"],
                "Baroque": ["Caravaggio", "Bernini", "Rembrandt", "Catholic Imagery", "Dutch Genre Painting"],
            },
            "Modern and Contemporary": {
                "Modernism": ["Impressionism", "Cubism", "Abstract Expressionism", "Ready-Mades", "Bauhaus"],
                "Contemporary Art": ["Installation", "Performance Art", "Conceptual Art", "Photography", "Global Biennials"],
            },
            "Architecture History": {
                "Western Architecture": ["Classical Orders", "Gothic Structure", "Modernist Architecture", "Urban Form", "Preservation"],
                "World Architecture": ["Islamic Architecture", "East Asian Temples", "Colonial Architecture", "Landscape Design", "Vernacular"],
            },
        },
    },
    "Anthropology": {
        "codes": ["ANTH", "ANT", "ANTHRO"],
        "sources": ["American Anthropologist", "JSTOR", "Annual Review of Anthropology", "Smithsonian", "Ethnography"],
        "subfields": {
            "Cultural Anthropology": {
                "Ethnography": ["Fieldwork", "Participant Observation", "Kinship", "Ritual", "Thick Description"],
                "Culture Theory": ["Cultural Relativism", "Exchange", "Identity", "Globalization", "Power"],
            },
            "Archaeology": {
                "Methods": ["Stratigraphy", "Dating", "Survey", "Excavation", "Material Culture"],
                "World Archaeology": ["Neolithic", "State Formation", "Collapse", "Mesoamerica", "Settlement Patterns"],
            },
            "Biological Anthropology": {
                "Human Evolution": ["Hominins", "Fossils", "Bipedalism", "Primates", "Out of Africa"],
                "Human Biology": ["Adaptation", "Genetics", "Forensic Anthropology", "Health", "Diet"],
            },
        },
    },
    "Education": {
        "codes": ["EDUC", "EDU", "EDFN"],
        "sources": ["ERIC", "AERJ", "EdWeek", "JSTOR", "What Works Clearinghouse"],
        "subfields": {
            "Learning Theory": {
                "Cognition and Learning": ["Constructivism", "Working Memory", "Transfer", "Metacognition", "Motivation"],
                "Instruction": ["Scaffolding", "Formative Assessment", "Direct Instruction", "Inquiry Learning", "Feedback"],
            },
            "Curriculum": {
                "Curriculum Design": ["Standards", "Scope and Sequence", "Hidden Curriculum", "Literacy", "STEM Education"],
                "Assessment": ["Validity", "Standardized Tests", "Rubrics", "Equity in Testing", "Classroom Assessment"],
            },
            "Education Policy": {
                "School Systems": ["School Choice", "Funding", "Accountability", "Teacher Labor", "Desegregation"],
                "Higher Education": ["Access", "College Completion", "Admissions", "Student Affairs", "Community Colleges"],
            },
        },
    },
    "Classics": {
        "codes": ["CLAS", "LATN", "GREK", "CLST"],
        "sources": ["Perseus", "Loeb Classical Library", "JSTOR", "Bryn Mawr Classical Review", "Oxford Classical Dictionary"],
        "subfields": {
            "Greek Literature": {
                "Greek Epic and Drama": ["Homer", "Sophocles", "Euripides", "Tragedy", "Chorus"],
                "Greek Prose": ["Plato", "Thucydides", "Herodotus", "Rhetoric", "Attic Oratory"],
            },
            "Latin Literature": {
                "Latin Poetry": ["Virgil", "Ovid", "Horace", "Elegy", "Epic"],
                "Latin Prose": ["Cicero", "Livy", "Tacitus", "Roman Historiography", "Letters"],
            },
            "Ancient Culture": {
                "Greek Culture": ["Polis", "Myth", "Religion", "Athletics", "Slavery in Greece"],
                "Roman Culture": ["Roman Religion", "Patronage", "Roman Family", "Imperial Cult", "Daily Life"],
            },
        },
    },
    "International Relations": {
        "codes": ["INTL", "IR", "INRL", "POLI"],
        "sources": ["International Organization", "Foreign Affairs", "CFR", "UN Documents", "World Politics"],
        "subfields": {
            "IR Theory": {
                "Core Theories": ["Realism", "Liberalism", "Constructivism", "Anarchy", "Balance of Power"],
                "Critical Approaches": ["Feminism in IR", "Postcolonial IR", "English School", "Securitization", "Norms"],
            },
            "Security Studies": {
                "War and Peace": ["Causes of War", "Deterrence", "Alliances", "Civil Wars", "Nuclear Strategy"],
                "Contemporary Security": ["Terrorism", "Cybersecurity", "Humanitarian Intervention", "Peacekeeping", "Intelligence"],
            },
            "Global Governance": {
                "Institutions": ["United Nations", "International Law", "WTO", "IMF", "NGOs"],
                "IPE": ["Trade", "Finance", "Development", "Sanctions", "Globalization"],
            },
        },
    },
    "Religious Studies": {
        "codes": ["RELS", "REL", "THEO"],
        "sources": ["JSTOR", "Journal of the American Academy of Religion", "Oxford Handbooks", "Sacred Texts", "ATLA"],
        "subfields": {
            "Comparative Religion": {
                "World Religions": ["Buddhism", "Hinduism", "Islam", "Judaism", "Christianity"],
                "Method": ["Ritual Studies", "Myth", "Pilgrimage", "Sacred Space", "Comparative Method"],
            },
            "Biblical Studies": {
                "Hebrew Bible": ["Torah", "Prophets", "Covenant", "Ancient Israel", "Exegesis"],
                "New Testament": ["Gospels", "Paul", "Early Christianity", "Historical Jesus", "Canon"],
            },
            "Religion and Society": {
                "Religion in Public Life": ["Secularization", "Fundamentalism", "Religion and Politics", "Pluralism", "Lived Religion"],
                "Philosophy of Religion": ["Arguments for God", "Problem of Evil", "Religious Experience", "Faith and Reason", "Miracles"],
            },
        },
    },
    "Geography": {
        "codes": ["GEOG", "GEOS", "GEO"],
        "sources": ["Annals of the AAG", "JSTOR", "National Geographic Education", "USGS", "Census TIGER"],
        "subfields": {
            "Human Geography": {
                "Population and Culture": ["Migration", "Urbanization", "Cultural Landscapes", "Diaspora", "Place"],
                "Political and Economic Geography": ["Geopolitics", "Borders", "Development", "Globalization", "Uneven Development"],
            },
            "Physical Geography": {
                "Landforms": ["Geomorphology", "Rivers", "Glaciers", "Coasts", "Soils"],
                "Climate": ["Climate Systems", "Biomes", "Weather", "Paleoclimate", "Water Cycle"],
            },
            "GIS": {
                "Spatial Analysis": ["Map Projections", "Remote Sensing", "Geocoding", "Raster and Vector", "Cartography"],
                "Applications": ["Urban GIS", "Environmental GIS", "Census Mapping", "GPS", "Spatial Statistics"],
            },
        },
    },
    "Environmental Studies": {
        "codes": ["ENVS", "ENV", "ENST"],
        "sources": ["Nature Climate Change", "EPA", "IPCC", "JSTOR", "Environmental Science and Technology"],
        "subfields": {
            "Climate Change": {
                "Science": ["Greenhouse Gases", "Carbon Cycle", "Climate Models", "Sea Level Rise", "Extreme Weather"],
                "Impacts": ["Adaptation", "Mitigation", "Climate Justice", "Energy Transition", "Carbon Pricing"],
            },
            "Conservation": {
                "Biodiversity": ["Endangered Species", "Habitat Loss", "Protected Areas", "Invasive Species", "Ecosystem Services"],
                "Resources": ["Forests", "Oceans", "Freshwater", "Soil Degradation", "Restoration"],
            },
            "Environmental Policy": {
                "Regulation": ["Clean Air Act", "NEPA", "International Agreements", "Environmental Justice", "Land Use"],
                "Sustainability": ["Circular Economy", "Life Cycle Assessment", "Sustainable Cities", "Renewable Energy", "Consumption"],
            },
        },
    },
    "Business": {
        "codes": ["BUS", "MGMT", "FINA", "ACCT"],
        "sources": ["Harvard Business Review", "SSRN", "JSTOR", "Wall Street Journal", "Academy of Management"],
        "subfields": {
            "Management": {
                "Organizations": ["Organizational Behavior", "Leadership", "Culture", "Motivation", "Teams"],
                "Strategy": ["Competitive Advantage", "Porter", "Corporate Strategy", "Innovation", "Resources"],
            },
            "Marketing": {
                "Consumer Behavior": ["Segmentation", "Branding", "Decision Making", "Pricing", "Advertising"],
                "Market Research": ["Surveys", "Positioning", "Digital Marketing", "A/B Testing", "Customer Analytics"],
            },
            "Finance": {
                "Corporate Finance": ["Valuation", "Capital Structure", "NPV", "Risk", "Dividends"],
                "Markets": ["Portfolio Theory", "Efficient Markets", "Bonds", "Derivatives", "Behavioral Finance"],
            },
            "Accounting": {
                "Financial Accounting": ["Balance Sheet", "Income Statement", "GAAP", "Revenue Recognition", "Audit"],
                "Managerial Accounting": ["Costing", "Budgets", "Variance Analysis", "Performance Metrics", "Internal Controls"],
            },
        },
    },
    "Computer Science": {
        "codes": ["CSCI", "CS", "COMP"],
        "sources": ["arXiv", "ACM DL", "IEEE Xplore", "GitHub", "MIT OCW"],
        "subfields": {
            "Algorithms": {
                "Core Algorithms": ["Sorting", "Graph Algorithms", "Dynamic Programming", "Greedy Algorithms", "Complexity"],
                "Data Structures": ["Trees", "Hash Tables", "Heaps", "Graphs", "Balanced Trees"],
            },
            "Machine Learning": {
                "Supervised Learning": ["Linear Models", "Neural Networks", "Decision Trees", "Regularization", "Cross Validation"],
                "Deep Learning": ["Backpropagation", "CNNs", "Transformers", "Optimization", "Representation Learning"],
            },
            "Systems": {
                "Operating Systems": ["Processes", "Memory Management", "Concurrency", "File Systems", "Scheduling"],
                "Networks": ["TCP/IP", "Routing", "Distributed Systems", "Consensus", "Cloud Computing"],
            },
            "Theory": {
                "Computability": ["Turing Machines", "Decidability", "NP-Completeness", "Reductions", "Automata"],
                "Programming Languages": ["Type Systems", "Compilers", "Semantics", "Functional Programming", "Interpreters"],
            },
        },
    },
    "Biology": {
        "codes": ["BIOL", "BIO", "BISC"],
        "sources": ["Nature", "PubMed", "Cell", "Khan Academy", "HHMI BioInteractive"],
        "subfields": {
            "Cell and Molecular Biology": {
                "Cell Biology": ["Membranes", "Organelles", "Cell Cycle", "Signaling", "Cytoskeleton"],
                "Molecular Biology": ["DNA Replication", "Transcription", "Translation", "PCR", "Gene Regulation"],
            },
            "Genetics and Evolution": {
                "Genetics": ["Mendelian Inheritance", "Mutations", "Population Genetics", "GWAS", "CRISPR"],
                "Evolution": ["Natural Selection", "Speciation", "Phylogeny", "Molecular Evolution", "Fossil Record"],
            },
            "Ecology": {
                "Populations": ["Population Growth", "Food Webs", "Niche", "Competition", "Life History"],
                "Ecosystems": ["Biomes", "Nutrient Cycles", "Biodiversity", "Conservation Biology", "Climate Ecology"],
            },
            "Physiology": {
                "Animal Physiology": ["Homeostasis", "Circulation", "Respiration", "Neurophysiology", "Endocrinology"],
                "Plant Physiology": ["Photosynthesis", "Transpiration", "Plant Hormones", "Water Relations", "Reproduction"],
            },
        },
    },
    "Chemistry": {
        "codes": ["CHEM", "CHM", "CHE"],
        "sources": ["JACS", "PubChem", "Nature Chemistry", "Khan Academy", "ACS Publications"],
        "subfields": {
            "Organic Chemistry": {
                "Structure": ["Functional Groups", "Stereochemistry", "Aromaticity", "Nomenclature", "Resonance"],
                "Reactions": ["Substitution", "Elimination", "Addition", "Mechanisms", "Synthesis"],
            },
            "Inorganic Chemistry": {
                "Bonding": ["Periodic Trends", "Crystal Field Theory", "Coordination Compounds", "Main Group", "Transition Metals"],
                "Materials": ["Solid State", "Organometallics", "Catalysis", "Nanomaterials", "Bioinorganic"],
            },
            "Physical Chemistry": {
                "Thermo and Kinetics": ["Thermodynamics", "Rate Laws", "Equilibrium", "Activation Energy", "Statistical Mechanics"],
                "Quantum Chemistry": ["Molecular Orbitals", "Spectroscopy", "DFT", "Wavefunctions", "Electronic Structure"],
            },
        },
    },
    "Physics": {
        "codes": ["PHYS", "PHY", "PHYS"],
        "sources": ["arXiv", "Physical Review", "MIT OCW", "HyperPhysics", "APS"],
        "subfields": {
            "Classical Physics": {
                "Mechanics": ["Newton's Laws", "Energy", "Momentum", "Oscillations", "Gravitation"],
                "Electromagnetism": ["Maxwell's Equations", "Circuits", "Magnetic Fields", "Waves", "Optics"],
            },
            "Modern Physics": {
                "Quantum Mechanics": ["Wavefunctions", "Uncertainty", "Operators", "Spin", "Entanglement"],
                "Relativity": ["Time Dilation", "Lorentz Transformations", "E=mc2", "Spacetime", "General Relativity"],
            },
            "Thermal and Statistical": {
                "Thermodynamics": ["Entropy", "Heat Engines", "Laws of Thermodynamics", "Phase Transitions", "Free Energy"],
                "Statistical Physics": ["Ensembles", "Partition Function", "Boltzmann", "Fluctuations", "Kinetic Theory"],
            },
        },
    },
    "Mathematics": {
        "codes": ["MATH", "MAT", "MTH"],
        "sources": ["arXiv", "AMS", "MathWorld", "Khan Academy", "MIT OCW"],
        "subfields": {
            "Analysis": {
                "Calculus": ["Limits", "Derivatives", "Integrals", "Series", "Multivariable Calculus"],
                "Real Analysis": ["Sequences", "Continuity", "Metric Spaces", "Lebesgue Integration", "Uniform Convergence"],
            },
            "Algebra": {
                "Linear Algebra": ["Vector Spaces", "Eigenvalues", "Matrices", "Linear Maps", "Inner Products"],
                "Abstract Algebra": ["Groups", "Rings", "Fields", "Homomorphisms", "Galois Theory"],
            },
            "Probability and Statistics": {
                "Probability": ["Random Variables", "Distributions", "Conditional Probability", "Limit Theorems", "Markov Chains"],
                "Statistics": ["Estimation", "Hypothesis Testing", "Regression", "Confidence Intervals", "Bayesian Inference"],
            },
            "Discrete Mathematics": {
                "Combinatorics": ["Counting", "Generating Functions", "Graph Theory", "Recurrence", "Pigeonhole"],
                "Logic and Proof": ["Proof Techniques", "Set Theory", "Predicates", "Induction", "Number Theory"],
            },
        },
    },
    "Public Health": {
        "codes": ["PUBH", "EPI", "PH"],
        "sources": ["CDC", "WHO", "PubMed", "Lancet", "American Journal of Public Health"],
        "subfields": {
            "Epidemiology": {
                "Study Design": ["Cohort Studies", "Case Control", "Randomized Trials", "Bias", "Confounding"],
                "Measures": ["Incidence", "Prevalence", "Risk Ratios", "Outbreak Investigation", "Surveillance"],
            },
            "Health Policy": {
                "Systems": ["Health Insurance", "Access to Care", "Medicaid", "Health Equity", "Quality of Care"],
                "Prevention": ["Vaccination", "Screening", "Health Behavior", "Occupational Health", "Injury Prevention"],
            },
            "Global Health": {
                "Infectious Disease": ["Malaria", "HIV", "Tuberculosis", "Pandemic Preparedness", "Neglected Diseases"],
                "Determinants": ["Social Determinants", "Nutrition", "Maternal Health", "Water and Sanitation", "Health Systems"],
            },
        },
    },
}

ADJACENT = {
    "History": ["Political Science", "Art History", "Classics", "International Relations", "Religious Studies"],
    "Literature": ["Linguistics", "Philosophy", "Classics", "Journalism"],
    "Philosophy": ["Religious Studies", "Political Science", "Literature", "Law", "Classics"],
    "Economics": ["Political Science", "Business", "International Relations", "Sociology", "Mathematics"],
    "Political Science": ["History", "Law", "International Relations", "Economics", "Philosophy"],
    "Psychology": ["Sociology", "Education", "Public Health", "Biology"],
    "Sociology": ["Anthropology", "Psychology", "Education", "Political Science"],
    "Linguistics": ["Literature", "Anthropology", "Education", "Classics"],
    "Law": ["Political Science", "Philosophy", "History", "Business"],
    "Art History": ["History", "Classics", "Anthropology"],
    "Anthropology": ["Sociology", "History", "Linguistics", "Religious Studies"],
    "Education": ["Psychology", "Sociology", "Linguistics"],
    "Classics": ["History", "Literature", "Art History", "Philosophy", "Linguistics"],
    "International Relations": ["Political Science", "History", "Economics", "Law"],
    "Religious Studies": ["Philosophy", "History", "Anthropology"],
    "Geography": ["Environmental Studies", "International Relations", "History", "Anthropology"],
    "Environmental Studies": ["Geography", "Public Health", "Biology", "Chemistry"],
    "Business": ["Economics", "Law", "Psychology"],
    "Computer Science": ["Mathematics", "Physics", "Education"],
    "Biology": ["Chemistry", "Public Health", "Psychology", "Environmental Studies"],
    "Chemistry": ["Biology", "Physics", "Public Health"],
    "Physics": ["Mathematics", "Chemistry", "Computer Science"],
    "Mathematics": ["Physics", "Computer Science", "Economics"],
    "Public Health": ["Biology", "Psychology", "Environmental Studies", "Sociology"],
}

# Journalism is adjacent to Literature but not a full catalog subject; map it away.
for key, vals in list(ADJACENT.items()):
    ADJACENT[key] = [s for s in vals if s in ACADEMIC]

NON_ACADEMIC_TITLES = [
    "YouTube - Lo-fi Hip Hop Radio - Beats to Relax/Study To",
    "YouTube - Funny Cat Compilation 2026",
    "Reddit - r/memes",
    "Reddit - r/gaming",
    "Reddit - r/AmItheAsshole",
    "Instagram",
    "TikTok",
    "X / Home",
    "Twitter / Home",
    "Facebook",
    "Netflix - Home",
    "Netflix - Stranger Things",
    "Hulu - Watch TV and Movies",
    "Disney+ | Movies and Shows",
    "Spotify - Web Player",
    "Amazon.com: Online Shopping",
    "Amazon.com: Wireless Headphones",
    "eBay: Electronics",
    "Newegg - PC Parts",
    "ESPN: NBA Scores",
    "ESPN: NFL Draft",
    "Bleacher Report - MLB",
    "Steam Store",
    "Twitch",
    "Discord | Friends",
    "Gmail",
    "Outlook - Inbox",
    "Google Calendar",
    "Weather.com - Local Forecast",
    "NYT Cooking: Weeknight Pasta",
    "AllRecipes: Easy Chicken Dinners",
    "Tasty - 5-Ingredient Meals",
    "IKEA: Bookshelves",
    "Zillow: Homes for Sale",
    "Kayak: Cheap Flights",
    "Airbnb: Cabins",
    "Tripadvisor: Best Beaches",
    "Pinterest: Room Decor",
    "BuzzFeed: Quizzes",
    "TMZ: Celebrity News",
    "People Magazine: Red Carpet",
    "IMDb: Top 250 Movies",
    "Rotten Tomatoes: New Releases",
    "Wikipedia: List of Marvel movies",
    "Wikipedia: List of Pokémon",
    "Fandom: Harry Potter Wiki",
    "Chess.com - Play Chess",
    "Wordle - The New York Times",
    "NYT Games: Connections",
    "Hacker News",
    "Product Hunt",
    "LinkedIn",
    "Indeed: Job Search",
    "Craigslist",
    "Uber Eats",
    "DoorDash: Food Delivery",
    "Sephora: Makeup",
    "Nike.com: Shoes",
    "GOAT: Sneakers",
    "YouTube - MrBeast",
    "YouTube - Sports Highlights",
    "Reddit - r/soccer",
    "Fantasy Football Rankings",
    "Coinbase: Bitcoin Price",
    "Robinhood",
    "WebMD: Sore Throat",
    "Healthline: Best Sleep Tips",
    "WikiHow: How to Tie a Tie",
    "Lifehacker: Morning Routines",
]

NON_ACADEMIC_TEMPLATES = [
    "YouTube: {}",
    "Reddit - r/{}",
    "Amazon.com: {}",
    "TikTok - {}",
    "Instagram: {}",
    "Netflix - {}",
    "ESPN: {}",
    "{} Recipe",
    "Best {} 2026",
    "How to {} - WikiHow",
    "Cheap {}",
    "{} Unboxing",
    "{} Highlights",
    "{} Memes",
    "Buy {} Online",
]

NON_ACADEMIC_FILLERS = [
    "funny cats", "gaming setup", "nba finals", "sourdough starter", "wireless earbuds",
    "celebrity gossip", "beach vacation", "skincare haul", "fantasy football", "standup comedy",
    "hiking boots", "dating app", "crypto crash", "new sneaker drop", "true crime podcast",
    "home workout", "meal prep", "concert tickets", "used cars", "apartment hunting",
    "coffee gadgets", "camping gear", "movie trailers", "reality tv", "street food",
]

ACADEMIC_PATTERNS = [
    "{v} Lecture Notes",
    "{v} Study Guide",
    "{v} Reading Notes",
    "{v} Seminar Notes",
    "{v} Discussion Questions",
    "{v} Essay Outline",
    "{v} Midterm Review",
    "{v} Final Exam Review",
    "{v} Annotated Bibliography",
    "{v} Primary Sources",
    "{v} Problem Set",
    "{v} Course Syllabus",
    "{v} Office Hours Notes",
    "{v} Textbook Chapter",
    "{v} Research Paper",
    "{v} Lit Review",
    "Week {n} Reading - {v}",
    "{v} - Week {n} Slides",
    "{code} {num}: {v}",
    "{code} {num} Lecture {n} - {v}",
    "Canvas: {v} Assignment",
    "Canvas: {v} Discussion Board",
    "Quizlet: {v} Flashcards",
    "Google Scholar - {v}",
    "Google Search: {v} lecture notes",
    "Wikipedia: {v}",
    "Britannica: {v}",
    "Khan Academy: {v}",
    "{src}: {v}",
    "{src} - {v}",
    "Library Catalog: {v}",
    "PDF: {v}.pdf",
    "{v}.pdf",
    "Oxford Handbook of {v}",
    "Cambridge Companion to {v}",
    "JSTOR: {v}",
    "Overview of {v}",
    "Intro to {v}",
    "Notes on {v}",
    "Guide to {v}",
    "{v} Fundamentals",
    "{v} Advanced Topics",
    "{v} Case Study",
    "{v} Theory",
    "{v} Analysis",
]

LIGHT_PREFIXES = ["Intro to", "Overview of", "Notes on", "Guide to", "Basics of"]

# Relation mix: 50/50 on-task vs off-task, with hard negatives so BERT cannot
# just separate "academic" from "YouTube".
RELATION_WEIGHTS = {
    "same_topic": 0.30,
    "same_subfield": 0.20,
    "other_subfield": 0.15,
    "adjacent_subject": 0.12,
    "other_academic": 0.08,
    "non_academic": 0.15,
}

SCORE_RANGES = {
    "same_topic": (0.90, 1.00),
    "same_subfield": (0.72, 0.90),
    "other_subfield": (0.18, 0.42),
    "adjacent_subject": (0.10, 0.32),
    "other_academic": (0.02, 0.16),
    "non_academic": (0.00, 0.06),
}


def clean_text(text: str) -> str:
    return " ".join(text.replace("\t", " ").replace("\n", " ").replace("\r", " ").split())


def pick_subject() -> str:
    return random.choice(list(ACADEMIC.keys()))


def pick_subfield(subject: str) -> str:
    return random.choice(list(ACADEMIC[subject]["subfields"].keys()))


def pick_topic(subject: str, subfield: str) -> str:
    return random.choice(list(ACADEMIC[subject]["subfields"][subfield].keys()))


def pick_subtopic(subject: str, subfield: str, topic: str) -> str:
    return random.choice(ACADEMIC[subject]["subfields"][subfield][topic])


def variation_for(subject: str, subfield: str, topic: str | None = None) -> tuple[str, str]:
    if topic is None:
        topic = pick_topic(subject, subfield)
    subtopic = pick_subtopic(subject, subfield, topic)
    choice = random.random()
    if choice < 0.45:
        variation = subtopic
    elif choice < 0.75:
        variation = topic
    elif choice < 0.90:
        variation = f"{subtopic} in {topic}"
    else:
        variation = f"{topic}: {subtopic}"
    return topic, variation


SKIP_PREFIX_STARTS = (
    "intro to ",
    "overview of ",
    "notes on ",
    "guide to ",
    "basics of ",
    "wikipedia:",
    "canvas:",
    "google ",
    "quizlet:",
    "jstor:",
    "pdf:",
    "khan academy",
    "britannica:",
    "library catalog",
)


def academic_title(subject: str, subfield: str, topic: str | None = None) -> str:
    meta = ACADEMIC[subject]
    topic, variation = variation_for(subject, subfield, topic)
    pattern = random.choice(ACADEMIC_PATTERNS)
    title = pattern.format(
        v=variation,
        n=random.randint(1, 14),
        code=random.choice(meta["codes"]),
        num=random.choice([101, 102, 201, 210, 220, 301, 310, 350, 401, 410, 420]),
        src=random.choice(meta["sources"]),
    )
    lowered = title.lower()
    if random.random() < 0.12 and not lowered.startswith(SKIP_PREFIX_STARTS):
        title = f"{random.choice(LIGHT_PREFIXES)} {title}"
    words = title.split()
    if random.random() < 0.06 and len(words) >= 7:
        title = " ".join(words[:-1])
    return clean_text(title)


def non_academic_title() -> str:
    if random.random() < 0.55:
        return clean_text(random.choice(NON_ACADEMIC_TITLES))
    return clean_text(random.choice(NON_ACADEMIC_TEMPLATES).format(random.choice(NON_ACADEMIC_FILLERS)))


def generate_focus_tabs(subject: str, subfield: str, num_tabs: int) -> tuple[list[str], list[str]]:
    """Similar tabs around one academic subfield, with topic variety inside it."""
    titles = []
    used_topics = []
    topics = list(ACADEMIC[subject]["subfields"][subfield].keys())
    seen = set()
    for _ in range(num_tabs):
        available = [t for t in topics if t not in seen] or topics
        topic = random.choice(available)
        seen.add(topic)
        title = academic_title(subject, subfield, topic)
        attempts = 0
        while title in titles and attempts < 8:
            title = academic_title(subject, subfield, topic)
            attempts += 1
        titles.append(title)
        used_topics.append(topic)
    return titles, used_topics


def choose_relation() -> str:
    names, weights = zip(*RELATION_WEIGHTS.items())
    return random.choices(names, weights=weights, k=1)[0]


def make_new_tab(subject: str, subfield: str, relation: str, used_topics: list[str] | None = None) -> str:
    used_topics = used_topics or []
    if relation == "same_topic":
        topic = random.choice(used_topics) if used_topics else pick_topic(subject, subfield)
        return academic_title(subject, subfield, topic)
    if relation == "same_subfield":
        other_topics = [t for t in ACADEMIC[subject]["subfields"][subfield] if t not in set(used_topics)]
        topic = random.choice(other_topics) if other_topics else pick_topic(subject, subfield)
        return academic_title(subject, subfield, topic)
    if relation == "other_subfield":
        others = [sf for sf in ACADEMIC[subject]["subfields"] if sf != subfield]
        new_sf = random.choice(others) if others else subfield
        return academic_title(subject, new_sf)
    if relation == "adjacent_subject":
        neighbors = ADJACENT.get(subject) or [s for s in ACADEMIC if s != subject]
        new_subject = random.choice(neighbors)
        new_sf = pick_subfield(new_subject)
        return academic_title(new_subject, new_sf)
    if relation == "other_academic":
        far = [s for s in ACADEMIC if s != subject and s not in ADJACENT.get(subject, [])]
        if not far:
            far = [s for s in ACADEMIC if s != subject]
        new_subject = random.choice(far)
        return academic_title(new_subject, pick_subfield(new_subject))
    return non_academic_title()


def score_for(relation: str) -> float:
    low, high = SCORE_RANGES[relation]
    return round(random.uniform(low, high), 3)


def serialize_for_bert(opened_tabs: list[str], new_tab: str, max_words: int = 90) -> str:
    """Put the new tab first so truncation cannot drop the candidate."""
    new_part = f"New: {clean_text(new_tab)}"
    budget = max_words - len(new_part.split())
    kept = []
    for tab in reversed(opened_tabs):
        text = clean_text(tab)
        cost = len(text.split()) + 1
        if kept and budget - cost < 0:
            break
        kept.append(text)
        budget -= cost
    kept.reverse()
    return f"{new_part} || " + " | ".join(kept)


def generate_dataset(num_examples: int) -> dict:
    data = []
    # Variety of session sizes, peaked toward a realistic 3-7 tabs, all short
    # enough to fit DistilBERT's 128-token training window.
    tab_counts = random.choices(
        range(2, 10),
        weights=[0.10, 0.16, 0.18, 0.18, 0.16, 0.12, 0.07, 0.03],
        k=num_examples,
    )

    for num_tabs in tab_counts:
        subject = pick_subject()
        subfield = pick_subfield(subject)
        opened_tabs, used_topics = generate_focus_tabs(subject, subfield, num_tabs)
        relation = choose_relation()
        new_tab = make_new_tab(subject, subfield, relation, used_topics)
        attempts = 0
        while new_tab in opened_tabs and attempts < 10:
            new_tab = make_new_tab(subject, subfield, relation, used_topics)
            attempts += 1

        score = score_for(relation)
        alignment = 1 if score >= 0.5 else 0
        data.append(
            {
                "opened_tabs": opened_tabs,
                "new_tab": new_tab,
                "alignment": alignment,
                "score": score,
            }
        )

    random.shuffle(data)
    print("Sample dataset entries:")
    for i, row in enumerate(data[:3]):
        print(f"Example {i}:")
        print(f"  Opened tabs: {row['opened_tabs']}")
        print(f"  New tab: {row['new_tab']}")
        print(f"  Alignment: {row['alignment']}")
        print(f"  Score: {row['score']}")
    print(
        "Alignment distribution:",
        {0: sum(1 for d in data if d["alignment"] == 0), 1: sum(1 for d in data if d["alignment"] == 1)},
    )
    print(
        "Tab count distribution:",
        {i: sum(1 for d in data if len(d["opened_tabs"]) == i) for i in range(2, 10)},
    )
    return {"data": data}


def save_txt(dataset: dict, filename: str) -> None:
    output_dir = os.path.dirname(filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as handle:
        for row in dataset["data"]:
            text = serialize_for_bert(row["opened_tabs"], row["new_tab"])
            handle.write(f"{text}\t{row['alignment']}\n")
    print(f"BERT TSV saved to {filename}")


def sample_quality_check(data: list[dict], fraction: float, seed: int) -> list[dict]:
    """Keep a stratified ~2% slice so both labels show up in the QA file."""
    rng = random.Random(seed)
    by_label = {0: [], 1: []}
    for row in data:
        by_label[int(row["alignment"])].append(row)
    sample = []
    for group in by_label.values():
        if not group:
            continue
        k = max(1, int(round(len(group) * fraction)))
        sample.extend(rng.sample(group, min(k, len(group))))
    rng.shuffle(sample)
    return sample


def save_quality_check(dataset: dict, filename: str, fraction: float, seed: int) -> None:
    output_dir = os.path.dirname(filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    rows = []
    for row in sample_quality_check(dataset["data"], fraction=fraction, seed=seed):
        item = dict(row)
        item["text"] = serialize_for_bert(row["opened_tabs"], row["new_tab"])
        rows.append(item)
    payload = {"fraction": fraction, "count": len(rows), "data": rows}
    with open(filename, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    print(f"Quality-check JSON saved to {filename} ({len(rows)} examples, {fraction:.0%} sample)")


def parse_tsv_line(line: str) -> dict:
    text, label = line.rstrip("\n").split("\t", 1)
    new_part, tabs_part = text.split(" || ", 1)
    new_tab = new_part[len("New: "):] if new_part.startswith("New: ") else new_part
    opened_tabs = [tab for tab in tabs_part.split(" | ") if tab]
    return {
        "opened_tabs": opened_tabs,
        "new_tab": new_tab,
        "alignment": int(label),
        "text": text,
    }


def quality_check_from_txt(txt_path: str, json_path: str, fraction: float, seed: int) -> None:
    with open(txt_path, encoding="utf-8") as handle:
        data = [parse_tsv_line(line) for line in handle if line.strip()]
    save_quality_check({"data": data}, json_path, fraction=fraction, seed=seed)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a general academic on-task dataset.")
    parser.add_argument("-n", "--num-examples", type=int, default=25000, help="Number of examples to generate")
    parser.add_argument("--txt", default=str(HERE / "general_dataset.txt"), help="Output TSV path for BERT")
    parser.add_argument(
        "--quality-check",
        default=str(HERE / "quality_check.json"),
        help="Small JSON sample for manual inspection. Pass empty string to skip.",
    )
    parser.add_argument(
        "--quality-check-fraction",
        type=float,
        default=0.01,
        help="Fraction of examples to write into the quality-check JSON.",
    )
    parser.add_argument(
        "--from-txt",
        default="",
        help="If set, sample a quality-check JSON from an existing TSV instead of generating.",
    )
    parser.add_argument("--seed", type=int, default=42, help="RNG seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    if args.from_txt:
        if not args.quality_check:
            raise SystemExit("--quality-check path is required when using --from-txt")
        quality_check_from_txt(args.from_txt, args.quality_check, args.quality_check_fraction, args.seed)
        return
    dataset = generate_dataset(args.num_examples)
    save_txt(dataset, args.txt)
    if args.quality_check:
        save_quality_check(dataset, args.quality_check, args.quality_check_fraction, args.seed)


if __name__ == "__main__":
    main()
