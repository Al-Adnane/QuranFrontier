# Quranic Narrative Structure and Story Arc Algorithm

## Source
- **Source Material**: The Study Quran (narrative surahs and commentaries), Classical Islamic narrative studies
- **Methodology**: Narratology, story structure analysis, Quranic literary analysis
- **Framework**: Joseph Campbell's monomyth adapted to Islamic narrative tradition

## Principle
The Quran employs sophisticated narrative structures to convey theological and moral principles. These can be formalized as story graphs with defined story elements (setup, conflict, resolution, lesson), character arcs, and thematic development that can be algorithmically extracted and analyzed.

## Mathematical Formulation

### 1. Story Structure Graph
```
NarrativeStructure = (Scenes, Transitions, Themes, LessonArc)

where:
  Scenes = {scene₁, scene₂, ..., sceneₙ}
  Transitions = {(sceneᵢ, sceneⱼ) | narrative flow}
  Themes = {theme₁, theme₂, ..., themeₘ}
  LessonArc = progression of theological/moral lesson

Example: Story of Prophet Yusuf (Joseph)
  Scenes: {Family_Harmony, Brothers_Treachery, Egypt_Service,
           Temptation, Prison, Elevation, Reconciliation}
  Themes: {Trust_in_God, Patience, Chastity, Divine_Justice}
```

### 2. Scene Composition
```
Scene = {
  setting: {location, temporal_context},
  characters: {protagonist, supporting, antagonist},
  action: sequence of events,
  dialogue: character_interactions,
  conflict: type ∈ {internal, external, cosmic},
  resolution: outcome,
  moral_weight: significance ∈ [0,1]
}

Conflict_Type:
  Internal (nafs): Struggle with self/desire (Yusuf resisting seduction)
  External (antagonist): Struggle with others (Joseph vs. Potiphar's wife)
  Cosmic (divine): Struggle with fate/divine will (Pharaoh vs. Moses)
```

### 3. Story Arc Equation
```
NarrativeArc(surah) = ∫[exposition, rising_action, climax, falling_action, resolution]

Exposition = Setup of situation, character introduction
Rising_Action = Increasingly significant events, tension increase
Climax = Peak of conflict, moment of highest stakes
Falling_Action = Consequences unfold, tension decreases
Resolution = Final outcome, lesson emerges

Arc_Intensity = Σ conflict_weight(sceneᵢ) weighted by narrative_position
```

### 4. Character Development
```
Character = {
  name: protagonist_name,
  initial_state: starting_condition,
  trials: [trial₁, trial₂, ..., trialₙ],
  transformation: initial_state → final_state,
  agency: measure of character control in narrative ∈ [0,1],
  moral_arc: moral_development ∈ [-1, 1] (corruption to virtue)
}

Agency(character) = decisions_made / total_events_involving_character
Moral_Transformation(c) = (final_virtue - initial_virtue) / max_possible_change
```

### 5. Thematic Saturation Analysis
```
ThemeSaturation(theme, surah) =
  (direct_mentions + metaphorical_references + exemplified_instances) / surah_length

Thematic_Coherence = correlation(scene_themes, overall_surah_theme)

Lesson_Emergence = clarity with which theme emerges through narrative
  High: Theme explicitly drawn from events
  Medium: Theme implied through consequences
  Low: Lesson requires interpretation
```

### 6. Intertextual Narrative Connections
```
NarrativeNetwork = {
  Nodes: all Quranic stories
  Edges: {(story₁, story₂) | share characters, themes, or lessons}
  Edge_Strength: similarity_score ∈ [0,1]
}

Story_Similarity(s₁, s₂) = θ_character + θ_theme + θ_lesson + θ_structure
  where θ parameters measure different similarity dimensions
```

## Algorithm: Narrative Structure Extraction

### Pseudocode
```
function EXTRACT_NARRATIVE_STRUCTURE(surah_text):
  INPUT: surah_text (full Quranic surah)
  OUTPUT: narrative_structure (dict with scenes, arc, themes, lessons)

  // Step 1: Identify narrative boundaries
  narrative_sections = SEGMENT_NARRATIVE(surah_text)
    // Identifies connected story passages

  scenes = []
  for each section in narrative_sections:

    // Step 2: Extract scene components
    setting = EXTRACT_SETTING(section)
      // Time, place references

    characters = EXTRACT_CHARACTERS(section)
      // Named/implied actors

    dialogue = EXTRACT_DIALOGUE(section)
      // Direct speech

    action = EXTRACT_ACTION_SEQUENCE(section)
      // Chronological events

    conflict = IDENTIFY_CONFLICT(action, dialogue, characters)
      // What opposes what?

    resolution = EXTRACT_SCENE_RESOLUTION(section)
      // How does tension resolve?

    scene = {
      number: len(scenes) + 1,
      setting: setting,
      characters: characters,
      dialogue: dialogue,
      action: action,
      conflict: conflict,
      resolution: resolution,
      text_span: section
    }

    scenes.append(scene)

  // Step 3: Build narrative continuity
  narrative_graph = INITIALIZE_GRAPH()
  for i in 0 to len(scenes)-2:
    curr_scene = scenes[i]
    next_scene = scenes[i+1]
    continuity = MEASURE_NARRATIVE_CONTINUITY(curr_scene, next_scene)
    narrative_graph.add_edge(curr_scene, next_scene, weight=continuity)

  // Step 4: Extract overall story arc
  arc_pattern = CLASSIFY_STORY_ARC(scenes)
    // Returns: monomyth, tragedy, redemption, etc.

  // Step 5: Identify character development
  characters_detailed = {}
  for each character in UNION_OF_CHARACTERS(scenes):
    first_appearance = FIND_FIRST_SCENE(character, scenes)
    last_appearance = FIND_LAST_SCENE(character, scenes)

    initial_state = EXTRACT_CHARACTER_STATE(first_appearance, character)
    final_state = EXTRACT_CHARACTER_STATE(last_appearance, character)
    trials = EXTRACT_CHARACTER_TRIALS(character, scenes)

    agency = COUNT_CHARACTER_DECISIONS(character, scenes) /
             COUNT_TOTAL_EVENTS(character, scenes)

    moral_change = MEASURE_MORAL_TRANSFORMATION(initial_state, final_state)

    characters_detailed[character] = {
      appearances: [s for s in scenes if character in s.characters],
      initial_state: initial_state,
      final_state: final_state,
      trials: trials,
      agency: agency,
      moral_transformation: moral_change,
      development_arc: BUILD_CHARACTER_ARC(character, scenes)
    }

  // Step 6: Extract thematic elements
  themes = SET()
  theme_instances = {}

  for each scene in scenes:
    // Direct thematic language
    explicit_themes = EXTRACT_KEYWORDS(scene.text_span)

    // Themes exemplified through action
    exemplified_themes = INFER_THEMES_FROM_ACTION(scene.action, scene.conflict)

    // Thematic metaphors and symbols
    symbolic_themes = EXTRACT_SYMBOLIC_MEANING(scene)

    for each theme in UNION(explicit_themes, exemplified_themes, symbolic_themes):
      themes.add(theme)
      if theme NOT IN theme_instances:
        theme_instances[theme] = []
      theme_instances[theme].append(scene.number)

  // Step 7: Calculate narrative arc intensity
  arc_intensity = 0
  for each scene in scenes:
    position_weight = (scene.number / len(scenes))  // Later scenes weighted higher
    conflict_weight = CALCULATE_CONFLICT_INTENSITY(scene.conflict)
    scene_intensity = position_weight * conflict_weight
    arc_intensity += scene_intensity

  arc_intensity = arc_intensity / len(scenes)

  // Step 8: Extract central lesson
  lesson_keywords = EXTRACT_LESSON_LANGUAGE(surah_text)
  lesson_explicit = GET_EXPLICIT_LESSON_STATEMENTS(surah_text)
  lesson_emergent = SYNTHESIZE_EMERGENT_LESSON(themes, characters_detailed, scenes)

  central_lesson = {
    explicit_statements: lesson_explicit,
    emergent_lesson: lesson_emergent,
    supporting_evidence: [
      {theme: theme, scenes: theme_instances[theme]}
      for theme in themes
    ],
    moral_principle: FORMULATE_MORAL_PRINCIPLE(lesson_emergent)
  }

  // Step 9: Identify narrative connections
  narrative_parallels = FIND_INTERTEXTUAL_PARALLELS(characters_detailed, themes)

  return {
    surah_reference: surah_text.surah_number,
    surah_name: surah_text.name,
    narrative_type: arc_pattern,
    scenes: scenes,
    narrative_graph: narrative_graph,
    characters: characters_detailed,
    themes: {
      primary_themes: [t for t in themes if theme_instances[t] >= 3],
      secondary_themes: [t for t in themes if theme_instances[t] == 2],
      minor_themes: [t for t in themes if theme_instances[t] == 1],
      theme_distribution: theme_instances
    },
    story_arc: {
      arc_type: arc_pattern,
      intensity: arc_intensity,
      climax_scene: IDENTIFY_CLIMAX_SCENE(scenes),
      rising_action_scenes: IDENTIFY_RISING_ACTION(scenes),
      resolution_type: CLASSIFY_RESOLUTION(scenes[-1])
    },
    central_lesson: central_lesson,
    narrative_parallels: narrative_parallels,
    literary_features: ANALYZE_LITERARY_FEATURES(surah_text, scenes),
    summary: GENERATE_NARRATIVE_SUMMARY(scenes, central_lesson)
  }
```

## Implementation Approach

### Python Skeleton
```python
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple
from enum import Enum

class ConflictType(Enum):
    INTERNAL = "Internal struggle (nafs)"
    EXTERNAL = "External antagonist"
    COSMIC = "Cosmic/divine will"
    MORAL = "Moral dilemma"

class StoryArcType(Enum):
    MONOMYTH = "Hero's Journey"
    TRAGEDY = "Fall from grace"
    REDEMPTION = "Transformation"
    QUEST = "Journey toward goal"
    REVELATION = "Divine disclosure"

@dataclass
class Scene:
    number: int
    setting: Dict
    characters: Set[str]
    dialogue: List[Tuple[str, str]]  # (speaker, text)
    action: List[str]  # Chronological events
    conflict: Dict
    resolution: Optional[str]
    text_span: str
    moral_weight: float

@dataclass
class CharacterDevelopment:
    name: str
    first_appearance: int  # Scene number
    last_appearance: int
    initial_state: Dict
    final_state: Dict
    trials: List[str]
    agency: float  # 0-1
    moral_transformation: float  # -1 to 1
    development_arc: List[Dict]

@dataclass
class NarrativeStructure:
    surah_number: int
    surah_name: str
    scenes: List[Scene]
    characters: Dict[str, CharacterDevelopment]
    themes: Dict
    story_arc: Dict
    central_lesson: Dict
    narrative_parallels: List[str]

class QuranicNarrativeAnalyzer:
    def __init__(self):
        self.character_database = {}  # Store Quranic characters
        self.theme_keywords = {}  # Map themes to keywords
        self.narrative_patterns = {}  # Store story patterns

    def segment_narrative(self, surah_text: str) -> List[str]:
        """Identify connected narrative passages"""
        # Implementation: identify narrative boundaries
        # Use scene shifts, character changes, temporal markers
        pass

    def extract_setting(self, scene_text: str) -> Dict:
        """Extract time and place information"""
        location = self._extract_location(scene_text)
        temporal = self._extract_temporal_context(scene_text)
        return {'location': location, 'temporal': temporal}

    def extract_characters(self, scene_text: str) -> Set[str]:
        """Identify characters in scene"""
        # Implementation: NER for character names
        pass

    def identify_conflict(self, action: List[str],
                         dialogue: List[Tuple],
                         characters: Set[str]) -> Dict:
        """Determine conflict type and intensity"""
        conflict_indicators = {
            'internal': ['nafs', 'qalb', 'taqwa'],
            'external': ['antagonist', 'opposition', 'refuse'],
            'cosmic': ['Allah', 'divine', 'qadar']
        }

        conflict_type = None
        intensity = 0

        for action_item in action:
            for ctype, indicators in conflict_indicators.items():
                if any(ind in action_item for ind in indicators):
                    conflict_type = ctype
                    intensity += 1

        return {
            'type': conflict_type or 'none',
            'intensity': min(1.0, intensity / 5.0),
            'resolution_status': self._determine_resolution(action)
        }

    def extract_character_development(self, character: str,
                                    scenes: List[Scene]) -> CharacterDevelopment:
        """Build character arc"""
        relevant_scenes = [s for s in scenes if character in s.characters]

        if not relevant_scenes:
            return None

        first = relevant_scenes[0]
        last = relevant_scenes[-1]

        initial_state = self._extract_state_at_scene(character, first)
        final_state = self._extract_state_at_scene(character, last)

        trials = self._extract_character_trials(character, relevant_scenes)
        agency = self._calculate_agency(character, scenes)
        moral_change = self._measure_moral_transformation(initial_state,
                                                          final_state)

        return CharacterDevelopment(
            name=character,
            first_appearance=first.number,
            last_appearance=last.number,
            initial_state=initial_state,
            final_state=final_state,
            trials=trials,
            agency=agency,
            moral_transformation=moral_change,
            development_arc=self._build_arc(character, relevant_scenes)
        )

    def classify_story_arc(self, scenes: List[Scene]) -> StoryArcType:
        """Determine overall narrative arc type"""
        # Analyze scene progression to classify story type
        # Implementation uses conflict evolution and resolution
        pass

    def extract_themes(self, scenes: List[Scene]) -> Dict[str, List[int]]:
        """Extract and localize themes"""
        theme_instances = {}

        for scene in scenes:
            themes = self._infer_themes(scene.action, scene.conflict)
            for theme in themes:
                if theme not in theme_instances:
                    theme_instances[theme] = []
                theme_instances[theme].append(scene.number)

        return theme_instances

    def extract_central_lesson(self, surah_text: str,
                             scenes: List[Scene],
                             themes: Dict) -> Dict:
        """Extract the moral/theological lesson"""
        # Extract explicit lesson statements
        explicit = self._find_lesson_statements(surah_text)

        # Synthesize emergent lesson from narrative
        emergent = self._synthesize_from_narrative(scenes, themes)

        return {
            'explicit_statements': explicit,
            'emergent_lesson': emergent,
            'moral_principle': self._formulate_principle(emergent),
            'supporting_scenes': [s.number for s in scenes
                                 if s.moral_weight > 0.5]
        }

    def analyze(self, surah_text: str) -> NarrativeStructure:
        """Complete narrative analysis"""
        sections = self.segment_narrative(surah_text)

        scenes = []
        for i, section in enumerate(sections):
            scene = Scene(
                number=i+1,
                setting=self.extract_setting(section),
                characters=self.extract_characters(section),
                dialogue=self._extract_dialogue(section),
                action=self._extract_actions(section),
                conflict=self.identify_conflict(*self._get_conflict_elements(section)),
                resolution=self._extract_resolution(section),
                text_span=section,
                moral_weight=self._calculate_moral_weight(section)
            )
            scenes.append(scene)

        # Extract characters
        characters = {}
        for char in self._get_all_characters(scenes):
            characters[char] = self.extract_character_development(char, scenes)

        # Extract themes
        themes_dict = self.extract_themes(scenes)

        # Classify arc
        arc_type = self.classify_story_arc(scenes)

        # Extract lesson
        lesson = self.extract_central_lesson(surah_text, scenes, themes_dict)

        return NarrativeStructure(
            surah_number=surah_text.surah_number,
            surah_name=surah_text.name,
            scenes=scenes,
            characters=characters,
            themes=themes_dict,
            story_arc={
                'type': arc_type,
                'intensity': self._calculate_arc_intensity(scenes),
                'climax': self._find_climax(scenes)
            },
            central_lesson=lesson,
            narrative_parallels=self._find_parallels(characters)
        )
```

## Validation Method

### Test Cases
1. **Story of Yusuf (Joseph)**: Complete narrative analysis
   - Expected: Identify 7 major scenes, character arc from innocence to wisdom

2. **Story of Musa (Moses)**: Complex multi-scene narrative
   - Expected: Identify conflict types (internal/external/cosmic)

3. **Short Narrative**: Single-scene story
   - Expected: Correctly handle non-complex structures

4. **Theme Extraction**: Verify theme consistency
   - Expected: Central themes (patience, justice, etc.) recur across scenes

### Quality Metrics
- Scene segmentation accuracy
- Theme extraction completeness
- Character development coherence
- Lesson emergence clarity

## Applications

1. **Story Analysis**: Understanding Quranic narratives systematically
2. **Comparative Narratology**: Comparing narrative techniques across surahs
3. **Educational Mapping**: Organizing Quranic stories by structure and lesson
4. **Thematic Teaching**: Using narrative structure to teach theological principles
5. **Literary Analysis**: Studying Quranic literary features
6. **Character Studies**: Analyzing prophetic character development
7. **Intertextual Analysis**: Finding narrative connections across surahs

## Related Algorithms
- Semantic Field Extraction Algorithm (identifies thematic vocabulary)
- Character Network Analysis Algorithm
- Symbolic Meaning Extraction Algorithm
- Temporal Sequence Analysis Algorithm
