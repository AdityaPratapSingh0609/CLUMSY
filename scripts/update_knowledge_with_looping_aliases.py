import sys
import os
import json
import re

sys.path.append('scripts')
import build_1000_prompts_math_science_code as b

def clean_key(text):
    return ' '.join(re.sub(r'[^a-z0-9]', ' ', text.lower()).split())

# Read existing knowledge_math_science.js
km_path = os.path.join('dashboard', 'knowledge_math_science.js')
with open(km_path, 'r', encoding='utf-8') as f:
    raw = f.read()

# Extract JSON
m = re.search(r'const KNOWLEDGE_MATH_SCIENCE_400 = ({[\s\S]*?});\n\nif', raw)
if not m:
    print("Could not extract KNOWLEDGE_MATH_SCIENCE_400 JSON")
    sys.exit(1)

knowledge_map = json.loads(m.group(1))
print(f"Existing keys in knowledge_map: {len(knowledge_map)}")

# Key aliases & conversational looping synonyms
aliases = {
    # Physics
    "law of inertia": "what is Newton's first law of motion",
    "first law of motion": "what is Newton's first law of motion",
    "newtons first law": "what is Newton's first law of motion",
    "newtons 1st law": "what is Newton's first law of motion",
    "f equals ma": "what is Newton's second law of motion",
    "f ma": "what is Newton's second law of motion",
    "second law of motion": "what is Newton's second law of motion",
    "newtons second law": "what is Newton's second law of motion",
    "newtons 2nd law": "what is Newton's second law of motion",
    "action and reaction": "what is Newton's third law of motion",
    "action reaction law": "what is Newton's third law of motion",
    "third law of motion": "what is Newton's third law of motion",
    "newtons third law": "what is Newton's third law of motion",
    "newtons 3rd law": "what is Newton's third law of motion",
    "speed of light": "what is the speed of light in vacuum",
    "speed of light in a vacuum": "what is the speed of light in vacuum",
    "c in physics": "what is the speed of light in vacuum",
    "escape velocity": "what is the formula for escape velocity",
    "escape velocity of earth": "what is the formula for escape velocity",
    "formula for escape velocity": "what is the formula for escape velocity",
    "heisenberg uncertainty": "what is the Heisenberg uncertainty principle",
    "uncertainty principle": "what is the Heisenberg uncertainty principle",
    "heisenberg uncertainty principle": "what is the Heisenberg uncertainty principle",
    "schrodingers cat": "what is the Schrödinger wave equation",
    "schrodinger cat": "what is the Schrödinger wave equation",

    # Chemistry
    "atomic number": "what is atomic number",
    "definition of atomic number": "what is atomic number",
    "mass number": "what is mass number",
    "isotopes": "what are isotopes",
    "definition of isotopes": "what are isotopes",
    "avogadros number": "what is Avogadro's number",
    "avogadro constant": "what is Avogadro's number",
    "ph of pure water": "what is the pH of pure water at 25°C",
    "ph of water": "what is the pH of pure water at 25°C",
    "le chatelier": "what is Le Chatelier's principle",
    "le chateliers principle": "what is Le Chatelier's principle",
    "ideal gas law": "what is the ideal gas law formula",
    "pv nrt": "what is the ideal gas law formula",

    # Biology
    "central dogma": "what is the central dogma of molecular biology",
    "central dogma of biology": "what is the central dogma of molecular biology",
    "flow of genetic information": "what is the central dogma of molecular biology",
    "dna base pairs": "what are the base pairs in dna",
    "base pairs in dna": "what are the base pairs in dna",
    "dna base pairing": "what are the base pairs in dna",
    "rna base pairs": "what are the base pairs in rna",
    "base pairs in rna": "what are the base pairs in rna",
    "powerhouse of the cell": "what is the structure and function of mitochondria",
    "function of mitochondria": "what is the structure and function of mitochondria",
    "mitochondria": "what is the structure and function of mitochondria",
    "stages of mitosis": "what are the four stages of mitosis",
    "mitosis stages": "what are the four stages of mitosis",
    "four stages of mitosis": "what are the four stages of mitosis",
    "dna helicase": "what is the role of DNA helicase",
    "role of helicase": "what is the role of DNA helicase",
    "dna polymerase": "what is the role of DNA polymerase",
    "role of polymerase": "what is the role of DNA polymerase",
    "dna ligase": "what is the role of DNA ligase",
    "role of ligase": "what is the role of DNA ligase",

    # Mathematics
    "quadratic formula": "what is the quadratic formula",
    "quadratic equation formula": "what is the quadratic formula",
    "discriminant": "what is the discriminant of a quadratic equation",
    "eulers identity": "what is Euler's identity formula",
    "euler identity": "what is Euler's identity formula",
    "eulers formula": "what is Euler's identity formula",
    "euler formula": "what is Euler's identity formula",
    "taylor series of e x": "what is the Taylor series of e^x",
    "derivative of sin x": "what is the derivative of sin(x)",
    "derivative of cos x": "what is the derivative of cos(x)",
    "derivative of e x": "what is the derivative of e^x",
    "derivative of ln x": "what is the derivative of ln(x)",
    "integral of x 2": "what is the integral of x^2 dx",
    "integral of sin x": "what is the integral of sin(x) dx",
    "integral of cos x": "what is the integral of cos(x) dx",
    "integral of e x": "what is the integral of e^x dx",
    "integral of 1 x": "what is the integral of 1/x dx",

    # Science Extra Loops
    "mass energy equivalence": "what is mass energy equivalence",
    "einstein mass energy equivalence": "what is mass energy equivalence",
    "e mc 2": "what is mass energy equivalence",
    "e mc2": "what is mass energy equivalence",
    "explain e mc 2": "what is mass energy equivalence",
    "chemical formula of glucose": "what is the chemical formula for glucose",
    "formula of glucose": "what is the chemical formula for glucose",
    "c6h12o6": "what is the chemical formula for glucose",
    "chemical formula of water": "what is the chemical formula for water",
    "photosynthesis equation": "what is the chemical equation for photosynthesis",
    "chemical equation of photosynthesis": "what is the chemical equation for photosynthesis",
    "photosynthesis formula": "what is the chemical equation for photosynthesis",
    "value of avogadro number": "what is Avogadro's number",
    "value of avogadro s number": "what is Avogadro's number",
    "what are the dna base pairs": "what are the base pairs in dna",
    "what is atp": "what is the role of ATP in cellular energy",
    "atp in cellular energy": "what is the role of ATP in cellular energy",
    "atp": "what is the role of ATP in cellular energy",
    "integral of 1 x": "what is the integral of 1/x dx",
    "integral of e x": "what is the integral of e^x dx"
}

added_aliases = 0
for alias, target_q in aliases.items():
    alias_clean = clean_key(alias)
    target_clean = clean_key(target_q)
    target_raw = target_q.lower().strip()

    ans = knowledge_map.get(target_clean) or knowledge_map.get(target_raw)
    if ans:
        knowledge_map[alias_clean] = ans
        knowledge_map[alias.lower()] = ans
        added_aliases += 1
    else:
        print(f"Warning: target query '{target_q}' not found in knowledge_map")

print(f"Added {added_aliases} alias mappings to knowledge_map.")
print(f"Total keys now in knowledge_map: {len(knowledge_map)}")

# Generate updated JavaScript file
js_content = [
    "/**",
    " * STAGE 53: 400 Expert Math & Science Comprehensive Knowledge Base",
    " * 100 Math + 100 Physics + 100 Chemistry + 100 Biology + Looping Aliases",
    " * 100% Offline-First Self-Contained Knowledge Engine",
    " */",
    "",
    "const KNOWLEDGE_MATH_SCIENCE_400 = " + json.dumps(knowledge_map, indent=2) + ";",
    "",
    "if (typeof module !== 'undefined' && module.exports) {",
    "  module.exports = { KNOWLEDGE_MATH_SCIENCE_400 };",
    "}",
    "if (typeof window !== 'undefined') {",
    "  window.KNOWLEDGE_MATH_SCIENCE_400 = KNOWLEDGE_MATH_SCIENCE_400;",
    "}",
    ""
]

with open(km_path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(js_content))

print(f"Updated {km_path} successfully ({os.path.getsize(km_path)} bytes).")
