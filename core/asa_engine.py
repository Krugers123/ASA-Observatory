
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .state_machine import ASA3StateMachine, StateSnapshot
from .listening_threshold import ListeningThresholdAnalyzer, ThresholdSnapshot
from .coherence_engine import CoherenceEngine, CoherenceSnapshot
from .complementarity_core import ComplementarityCore, ComplementaritySnapshot


@dataclass
class DialogueTurn:
    role: str
    content: str
    timestamp: Optional[float] = None
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class ASA3Session:
    session_id: str
    anchor_text: str
    constraints: List[str] = field(default_factory=list)
    turns: List[DialogueTurn] = field(default_factory=list)
    signal_history: List[float] = field(default_factory=list)
    predictability_history: List[float] = field(default_factory=list)
    semantic_similarity_history: List[float] = field(default_factory=list)
    turn_latency_history: List[float] = field(default_factory=list)
    emergent_concept_history: List[float] = field(default_factory=list)
    human_signal_history: List[float] = field(default_factory=list)
    ai_signal_history: List[float] = field(default_factory=list)
    snapshots: List[Dict[str, object]] = field(default_factory=list)


@dataclass
class ASA3UnifiedSnapshot:
    session_id: str
    turn_index: int
    drift_score: float
    drift_profile: Dict[str, object]
    semantic_possibility: Dict[str, object]
    threshold: ThresholdSnapshot
    coherence: CoherenceSnapshot
    complementarity: ComplementaritySnapshot
    state: StateSnapshot
    notes: List[str] = field(default_factory=list)


class ASA3Engine:
    """
    ASA 3.0 proper engine.

    This engine orchestrates:
    - dialogue turn ingestion
    - precursor signal tracking
    - listening threshold detection
    - coherence estimation
    - complementarity evaluation
    - state machine decision

    It is intentionally modular so later we can replace heuristics
    with graph-based or embedding-based logic without breaking the API.
    """

    def __init__(self) -> None:
        self.sessions: Dict[str, ASA3Session] = {}
        self.state_machine = ASA3StateMachine()
        self.threshold_analyzer = ListeningThresholdAnalyzer()
        self.coherence_engine = CoherenceEngine()
        self.complementarity_core = ComplementarityCore()

    # ---------------------------------------------------------
    # Session lifecycle
    # ---------------------------------------------------------
    def create_session(
        self,
        session_id: str,
        anchor_text: str,
        constraints: Optional[List[str]] = None,
    ) -> ASA3Session:
        if session_id in self.sessions:
            raise ValueError(f"Session already exists: {session_id}")

        session = ASA3Session(
            session_id=session_id,
            anchor_text=anchor_text,
            constraints=constraints or [],
        )
        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> ASA3Session:
        if session_id not in self.sessions:
            raise ValueError(f"Unknown session_id: {session_id}")
        return self.sessions[session_id]

    # ---------------------------------------------------------
    # Turn ingestion
    # ---------------------------------------------------------
    def add_user_turn(
        self,
        session_id: str,
        content: str,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> None:
        session = self.get_session(session_id)
        session.turns.append(
            DialogueTurn(
                role="user",
                content=content,
                timestamp=timestamp,
                metadata=metadata or {},
            )
        )
        session.human_signal_history.append(self._human_agency_signal(content))

    def add_assistant_turn(
        self,
        session_id: str,
        content: str,
        timestamp: Optional[float] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> ASA3UnifiedSnapshot:
        session = self.get_session(session_id)
        session.turns.append(
            DialogueTurn(
                role="assistant",
                content=content,
                timestamp=timestamp,
                metadata=metadata or {},
            )
        )
        session.ai_signal_history.append(self._ai_support_signal(content))

        self._update_precursor_histories(session)

        drift_score = self._drift_score(session)
        threshold_snapshot = self.threshold_analyzer.analyze(
            signal_history=session.signal_history,
            predictability_history=session.predictability_history,
        )
        coherence_snapshot = self.coherence_engine.analyze(
            semantic_similarity_history=session.semantic_similarity_history,
            turn_latency_history=session.turn_latency_history,
            emergent_concept_history=session.emergent_concept_history,
        )
        complementarity_snapshot = self.complementarity_core.analyze(
            human_signal_history=session.human_signal_history,
            ai_signal_history=session.ai_signal_history,
        )
        drift_profile = self._drift_typology(
            session=session,
            drift_score=drift_score,
            coherence_score=coherence_snapshot.coherence_score,
            complementarity_score=complementarity_snapshot.complementarity_score,
            listening_score=threshold_snapshot.insistence_coefficient,
        )
        semantic_possibility = self._semantic_possibility_profile(
            session=session,
            drift_score=drift_score,
            coherence_score=coherence_snapshot.coherence_score,
            complementarity_score=complementarity_snapshot.complementarity_score,
            listening_score=threshold_snapshot.insistence_coefficient,
        )

        state_snapshot = self.state_machine.decide(
            drift_score=drift_score,
            listening_score=threshold_snapshot.insistence_coefficient,
            coherence_score=coherence_snapshot.coherence_score,
            complementarity_score=complementarity_snapshot.complementarity_score,
            human_agency_score=complementarity_snapshot.human_agency_score,
            ai_support_score=complementarity_snapshot.ai_support_score,
            semantic_envelope_state=str(semantic_possibility.get("semantic_envelope_state", "unknown")),
            sps=float(semantic_possibility.get("sps", 0.0)),
            cmr=float(semantic_possibility.get("cmr", 0.0)),
        )

        notes: List[str] = []
        notes.extend(threshold_snapshot.notes)
        notes.extend(coherence_snapshot.notes)
        notes.extend(complementarity_snapshot.notes)
        notes.extend(state_snapshot.notes)

        unified = ASA3UnifiedSnapshot(
            session_id=session_id,
            turn_index=len(session.turns),
            drift_score=round(drift_score, 4),
            drift_profile=drift_profile,
            semantic_possibility=semantic_possibility,
            threshold=threshold_snapshot,
            coherence=coherence_snapshot,
            complementarity=complementarity_snapshot,
            state=state_snapshot,
            notes=self._dedupe(notes),
        )

        session.snapshots.append(self._serialize_snapshot(unified))
        return unified

    # ---------------------------------------------------------
    # Internal signal logic
    # ---------------------------------------------------------
    def _update_precursor_histories(self, session: ASA3Session) -> None:
        # Signal history approximates "structuredness" of current dialogue step.
        session.signal_history.append(self._structured_signal(session))

        # Predictability approximates how stable the dialogue becomes across turns.
        session.predictability_history.append(self._predictability_signal(session))

        # Semantic convergence precursor:
        # for coherence we care not only about direct anchor overlap, but about
        # whether the dialogue keeps building a shared frame across nearby turns.
        session.semantic_similarity_history.append(self._coherence_similarity(session))

        # Turn rhythm placeholder:
        # until we have real latency capture, infer stability from turn length change.
        session.turn_latency_history.append(self._pseudo_turn_latency(session))

        # Emergent concepts placeholder:
        # higher when both sides introduce new tokens while staying near anchor.
        session.emergent_concept_history.append(self._emergent_concept_signal(session))

    def _drift_score(self, session: ASA3Session) -> float:
        if not session.turns:
            return 0.0
        anchor_similarity = self._semantic_similarity_to_anchor(session)
        local_similarity = self._local_context_similarity(session)
        rolling_similarity = self._rolling_context_similarity(session)

        # Drift should reflect both deviation from the declared anchor and
        # rupture of local conversational continuity. Stable elaboration often
        # rephrases the anchor, so we do not treat low direct anchor overlap as
        # drift when the exchange remains locally coherent.
        similarity = (
            0.45 * anchor_similarity
            + 0.35 * local_similarity
            + 0.20 * rolling_similarity
        )
        return max(0.0, min(1.0, 1.0 - similarity))

    def _structured_signal(self, session: ASA3Session) -> float:
        if len(session.turns) < 2:
            return 0.0
        anchor_similarity = self._semantic_similarity_to_anchor(session)
        pair_similarity = self._last_pair_similarity(session)
        return max(0.0, min(1.0, 0.5 * anchor_similarity + 0.5 * pair_similarity))

    def _predictability_signal(self, session: ASA3Session) -> float:
        if len(session.turns) < 3:
            return 0.0
        pair_similarity = self._last_pair_similarity(session)
        rhythm = 1.0 - abs(self._pseudo_turn_latency(session) - 1.0)
        return max(0.0, min(1.0, 0.7 * pair_similarity + 0.3 * max(0.0, rhythm)))

    def _semantic_similarity_to_anchor(self, session: ASA3Session) -> float:
        if not session.turns:
            return 0.0
        current = session.turns[-1].content
        return self._token_overlap_similarity(session.anchor_text, current)

    def _last_pair_similarity(self, session: ASA3Session) -> float:
        if len(session.turns) < 2:
            return 0.0
        a = session.turns[-2].content
        b = session.turns[-1].content
        return self._token_overlap_similarity(a, b)

    def _local_context_similarity(self, session: ASA3Session) -> float:
        if len(session.turns) < 2:
            return self._semantic_similarity_to_anchor(session)
        return self._last_pair_similarity(session)

    def _rolling_context_similarity(self, session: ASA3Session, window: int = 3) -> float:
        if len(session.turns) < 2:
            return self._semantic_similarity_to_anchor(session)

        current = session.turns[-1].content
        previous_turns = session.turns[max(0, len(session.turns) - 1 - window) : -1]
        if not previous_turns:
            return self._last_pair_similarity(session)

        similarities = [
            self._token_overlap_similarity(current, turn.content)
            for turn in previous_turns
        ]
        return sum(similarities) / max(1, len(similarities))

    def _coherence_similarity(self, session: ASA3Session) -> float:
        anchor_similarity = self._semantic_similarity_to_anchor(session)
        local_similarity = self._local_context_similarity(session)
        rolling_similarity = self._rolling_context_similarity(session)

        # Coherence needs to reward shared-frame continuity more than direct
        # lexical loyalty to the anchor. Stable dialogue often elaborates the
        # anchor through paraphrase instead of repeating it verbatim.
        return max(
            0.0,
            min(
                1.0,
                (0.30 * anchor_similarity)
                + (0.45 * local_similarity)
                + (0.25 * rolling_similarity),
            ),
        )

    def _pseudo_turn_latency(self, session: ASA3Session) -> float:
        if len(session.turns) < 2:
            return 1.0
        prev_len = max(1, len(session.turns[-2].content.split()))
        cur_len = max(1, len(session.turns[-1].content.split()))
        ratio = min(prev_len, cur_len) / max(prev_len, cur_len)
        return max(0.0, min(1.0, ratio))

    def _emergent_concept_signal(self, session: ASA3Session) -> float:
        if len(session.turns) < 2:
            return 0.0

        last = self._tokenize(session.turns[-1].content)
        prev = self._tokenize(session.turns[-2].content)
        anchor = self._tokenize(session.anchor_text)

        novel = len((last - prev) - anchor)
        anchor_overlap = len(last & anchor) / max(1, len(anchor))

        novelty_score = min(1.0, novel / 8.0)
        return max(0.0, min(1.0, 0.5 * novelty_score + 0.5 * anchor_overlap))

    def _drift_typology(
        self,
        session: ASA3Session,
        drift_score: float,
        coherence_score: float,
        complementarity_score: float,
        listening_score: float,
    ) -> Dict[str, object]:
        anchor_similarity = self._semantic_similarity_to_anchor(session)
        local_similarity = self._local_context_similarity(session)
        rolling_similarity = self._rolling_context_similarity(session)
        predictability = session.predictability_history[-1] if session.predictability_history else 0.0
        emergent = session.emergent_concept_history[-1] if session.emergent_concept_history else 0.0

        current_text = session.turns[-1].content if session.turns else ""
        current_tokens = self._tokenize(current_text)
        narrowing_tokens = {
            "only", "must", "exactly", "strict", "narrow", "just", "single"
        }
        correction_tokens = {
            "keep", "stay", "still", "focus", "anchor", "narrow", "only"
        }
        has_narrowing_language = bool(current_tokens & narrowing_tokens)
        recent_user_text = ""
        if len(session.turns) >= 2 and session.turns[-2].role == "user":
            recent_user_text = session.turns[-2].content.lower()
        user_is_correcting = any(
            token in recent_user_text for token in correction_tokens
        )

        labels: List[str] = []

        if drift_score >= 0.72 and anchor_similarity < 0.22 and local_similarity >= 0.30:
            labels.append("anchor_substitution")
        if drift_score >= 0.68 and local_similarity < 0.22 and rolling_similarity < 0.24:
            labels.append("context_fracture")
        if (
            drift_score >= 0.60
            and predictability >= 0.48
            and coherence_score < 0.52
            and listening_score < 0.60
        ):
            labels.append("narrative_lock_in")
        if (
            drift_score >= 0.62
            and rolling_similarity >= 0.26
            and anchor_similarity < 0.28
            and emergent >= 0.45
        ):
            labels.append("recursive_reinterpretation")
        if (
            drift_score >= 0.58
            and (has_narrowing_language or user_is_correcting)
            and complementarity_score < 0.82
        ):
            labels.append("compression_drift")
        if (
            len(session.signal_history) >= 2
            and session.signal_history[-1] < session.signal_history[-2]
            and drift_score < 0.72
            and coherence_score >= 0.45
        ):
            labels.append("recovery_in_progress")

        if not labels:
            if drift_score >= 0.72:
                labels.append("general_semantic_drift")
            else:
                labels.append("localized_instability")

        primary = labels[0]
        return {
            "primary_type": primary,
            "secondary_types": labels[1:],
            "signals": {
                "anchor_similarity": round(anchor_similarity, 4),
                "local_similarity": round(local_similarity, 4),
                "rolling_similarity": round(rolling_similarity, 4),
                "predictability": round(float(predictability), 4),
                "emergent_signal": round(float(emergent), 4),
            },
        }

    def _semantic_possibility_profile(
        self,
        session: ASA3Session,
        drift_score: float,
        coherence_score: float,
        complementarity_score: float,
        listening_score: float,
    ) -> Dict[str, object]:
        anchor_similarity = self._semantic_similarity_to_anchor(session)
        local_similarity = self._local_context_similarity(session)
        rolling_similarity = self._rolling_context_similarity(session)
        predictability = session.predictability_history[-1] if session.predictability_history else 0.0
        emergent = session.emergent_concept_history[-1] if session.emergent_concept_history else 0.0

        current_text = session.turns[-1].content if session.turns else ""
        current_tokens = self._tokenize(current_text)
        anchor_tokens = self._tokenize(session.anchor_text)
        lexical_diversity = len(current_tokens) / max(1, len(current_text.split()))

        narrowing_tokens = {
            "only", "must", "exactly", "strict", "narrow", "just", "single",
            "always", "never", "cannot",
        }
        expansive_tokens = {
            "can", "could", "may", "option", "options", "explore", "variant",
            "variants", "multiple", "alternative", "alternatives", "possible",
        }
        has_narrowing_language = bool(current_tokens & narrowing_tokens)
        has_expansive_language = bool(current_tokens & expansive_tokens)
        anchor_coverage = len(current_tokens & anchor_tokens) / max(1, len(anchor_tokens))
        shared_frame = (0.45 * local_similarity) + (0.30 * rolling_similarity) + (0.25 * coherence_score)
        resilience_bonus = 0.0
        if local_similarity >= 0.28 and coherence_score >= 0.44:
            resilience_bonus += 0.06
        if complementarity_score >= 0.78:
            resilience_bonus += 0.04
        if has_expansive_language and shared_frame >= 0.32:
            resilience_bonus += 0.03

        sps = (
            0.18 * anchor_similarity
            + 0.26 * local_similarity
            + 0.18 * rolling_similarity
            + 0.18 * coherence_score
            + 0.10 * complementarity_score
            + 0.08 * lexical_diversity
            + 0.02 * emergent
        )
        sps += resilience_bonus
        if has_expansive_language:
            sps += 0.04
        if has_narrowing_language:
            sps -= 0.06
        sps -= 0.07 * drift_score
        sps -= 0.04 * listening_score
        sps = max(0.0, min(1.0, sps))

        consistency_core = (
            0.24 * anchor_similarity
            + 0.24 * local_similarity
            + 0.16 * rolling_similarity
            + 0.18 * coherence_score
            + 0.12 * complementarity_score
            + 0.05 * predictability
        )
        consistency_core += resilience_bonus
        divergence_penalty = (
            0.28 * drift_score
            + 0.16 * abs(anchor_similarity - local_similarity)
            + 0.10 * max(0.0, 0.22 - lexical_diversity)
            + 0.08 * listening_score
        )
        if has_narrowing_language:
            divergence_penalty += 0.05
        if anchor_coverage < 0.18 and local_similarity >= 0.30:
            divergence_penalty += 0.03

        cmr = max(0.0, min(1.0, consistency_core - divergence_penalty + 0.35))

        if sps >= 0.54 and cmr >= 0.50:
            envelope_state = "healthy"
        elif sps >= 0.36 and cmr >= 0.34:
            envelope_state = "narrowing"
        elif sps >= 0.22 and cmr >= 0.22:
            envelope_state = "brittle"
        else:
            envelope_state = "collapsed"

        if envelope_state == "healthy":
            interpretation = "semantic_possibility_preserved"
        elif envelope_state == "narrowing":
            interpretation = "semantic_space_narrowing"
        elif envelope_state == "brittle":
            interpretation = "counterfactual_meaning_fragile"
        else:
            interpretation = "semantic_envelope_collapse"

        return {
            "sps": round(sps, 4),
            "cmr": round(cmr, 4),
            "semantic_envelope_state": envelope_state,
            "interpretation": interpretation,
            "signals": {
                "anchor_similarity": round(anchor_similarity, 4),
                "local_similarity": round(local_similarity, 4),
                "rolling_similarity": round(rolling_similarity, 4),
                "coherence_score": round(coherence_score, 4),
                "complementarity_score": round(complementarity_score, 4),
                "predictability": round(float(predictability), 4),
                "emergent_signal": round(float(emergent), 4),
                "lexical_diversity": round(lexical_diversity, 4),
                "anchor_coverage": round(anchor_coverage, 4),
            },
        }

    def _human_agency_signal(self, text: str) -> float:
        tokens = self._tokenize(text)
        directive_words = {"want", "need", "focus", "change", "keep", "now", "why", "how"}
        matches = len(tokens & directive_words)
        return max(0.0, min(1.0, 0.4 + (matches / 6.0)))

    def _ai_support_signal(self, text: str) -> float:
        tokens = self._tokenize(text)
        structural_words = {"because", "therefore", "structure", "stability", "signal", "state", "layer"}
        matches = len(tokens & structural_words)
        return max(0.0, min(1.0, 0.4 + (matches / 6.0)))

    # ---------------------------------------------------------
    # Utilities
    # ---------------------------------------------------------
    def _token_overlap_similarity(self, a: str, b: str) -> float:
        ta = self._tokenize(a)
        tb = self._tokenize(b)
        if not ta or not tb:
            return 0.0
        inter = len(ta & tb)
        union = len(ta | tb)
        jaccard = inter / max(1, union)
        overlap = inter / max(1, min(len(ta), len(tb)))
        dice = (2 * inter) / max(1, len(ta) + len(tb))
        return (0.25 * jaccard) + (0.35 * overlap) + (0.40 * dice)

    def _tokenize(self, text: str) -> set[str]:
        stopwords = {
            "the", "and", "for", "with", "that", "this", "into", "from", "your",
            "will", "when", "what", "how", "why", "can", "now", "yet", "only",
            "without", "across", "between", "toward", "while", "also", "same",
        }
        return {
            self._normalize_token(t)
            for raw in text.replace("-", " ").replace("/", " ").split()
            for t in [raw.strip(".,:;!?()[]{}\"'").lower()]
            if len(t) > 2 and t not in stopwords and self._normalize_token(t)
        }

    def _normalize_token(self, token: str) -> str:
        aliases = {
            "discussion": "dialogue",
            "conversation": "dialogue",
            "interactions": "interaction",
            "dialog": "dialogue",
            "maintain": "anchor",
            "keep": "anchor",
            "anchored": "anchor",
            "anchoring": "anchor",
            "reanchor": "anchor",
            "reanchoring": "anchor",
            "stable": "stability",
            "stabilize": "stability",
            "stabilizing": "stability",
            "meaning": "semantic",
            "meanings": "semantic",
            "structural": "structure",
            "steering": "steer",
            "preserved": "preserve",
            "preserving": "preserve",
            "supports": "support",
            "supporting": "support",
            "signals": "signal",
            "monitors": "monitor",
            "routes": "route",
        }

        normalized = aliases.get(token, token)

        for suffix in ("ing", "ed", "es", "s"):
            if normalized.endswith(suffix) and len(normalized) > len(suffix) + 3:
                normalized = normalized[: -len(suffix)]
                break

        return aliases.get(normalized, normalized)

    def _dedupe(self, notes: List[str]) -> List[str]:
        out: List[str] = []
        seen = set()
        for note in notes:
            if note not in seen:
                seen.add(note)
                out.append(note)
        return out

    def _serialize_snapshot(self, snapshot: ASA3UnifiedSnapshot) -> Dict[str, object]:
        return {
            "session_id": snapshot.session_id,
            "turn_index": snapshot.turn_index,
            "drift_score": snapshot.drift_score,
            "drift_profile": snapshot.drift_profile,
            "semantic_possibility": snapshot.semantic_possibility,
            "threshold": {
                "insistence_coefficient": snapshot.threshold.insistence_coefficient,
                "threshold_crossed": snapshot.threshold.threshold_crossed,
                "notes": snapshot.threshold.notes,
            },
            "coherence": {
                "rhythmic_alignment_score": snapshot.coherence.rhythmic_alignment_score,
                "semantic_convergence_score": snapshot.coherence.semantic_convergence_score,
                "third_layer_behavior_score": snapshot.coherence.third_layer_behavior_score,
                "coherence_score": snapshot.coherence.coherence_score,
                "threshold_crossed": snapshot.coherence.threshold_crossed,
                "notes": snapshot.coherence.notes,
            },
            "complementarity": {
                "human_agency_score": snapshot.complementarity.human_agency_score,
                "ai_support_score": snapshot.complementarity.ai_support_score,
                "complementarity_score": snapshot.complementarity.complementarity_score,
                "balance_index": snapshot.complementarity.balance_index,
                "notes": snapshot.complementarity.notes,
            },
            "state": {
                "state": snapshot.state.state,
                "action": snapshot.state.action,
                "confidence": snapshot.state.confidence,
                "trigger_reasons": snapshot.state.trigger_reasons,
                "notes": snapshot.state.notes,
            },
            "notes": snapshot.notes,
        }
