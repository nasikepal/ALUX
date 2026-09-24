"""
Music and Score Direction Engine.
Maps script narrative emotional trajectory into musical pacing, BPM, key, and instrumentation.
"""

from typing import Dict, List, Any, Optional
from core.models import VisualUnit, MediaAsset
from providers.local_media import local_media_provider


class MusicScoreEngine:
    EMOTIONAL_MUSIC_PROFILES = {
        "scale": {
            "tempo_bpm": "80-95 BPM",
            "key": "D Minor / C Major",
            "mood": "Monumental, vast, technological awe",
            "instrumentation": "Deep analog sub-bass, expansive cinematic brass, modular synth arpeggio",
            "reference_style": "Hans Zimmer (Interstellar / Blade Runner 2049), Max Richter"
        },
        "urgency": {
            "tempo_bpm": "115-130 BPM",
            "key": "F Minor",
            "mood": "Relentless, competitive, pressurized",
            "instrumentation": "High-frequency ticking percussion, distorted 808 bass, staccato cello pulses",
            "reference_style": "Ludwig Göransson (Oppenheimer), Trent Reznor & Atticus Ross"
        },
        "growth": {
            "tempo_bpm": "95-108 BPM",
            "key": "A Major",
            "mood": "Ascending, industrial momentum, building triumph",
            "instrumentation": "Driving acoustic drums, electric guitar ambient swell, bright analog synths",
            "reference_style": "Jóhann Jóhannsson (The Theory of Everything), Olafur Arnalds"
        },
        "uncertainty": {
            "tempo_bpm": "65-78 BPM",
            "key": "E-Flat Minor",
            "mood": "Suspenseful, fragile, epistemic friction",
            "instrumentation": "Dissonant string glissando, bowed metallic textures, sub-audible drone",
            "reference_style": "Mica Levi (Under the Skin), Colin Stetson"
        },
        "precision": {
            "tempo_bpm": "90-100 BPM",
            "key": "G Minor",
            "mood": "Mathematical clarity, clockwork discipline",
            "instrumentation": "Crisp electronic percussion, glass marimba, cyclical sequencing",
            "reference_style": "Steve Reich, Philip Glass, Nils Frahm"
        },
        "power": {
            "tempo_bpm": "85-100 BPM",
            "key": "C Minor",
            "mood": "Authoritative, heavy, industrial sovereign control",
            "instrumentation": "Taiko drums, brass braams, distorted synth bass lead",
            "reference_style": "Junkie XL (Mad Max), Geoff Barrow & Ben Salisbury"
        },
        "wealth_capital": {
            "tempo_bpm": "72-85 BPM",
            "key": "B Minor / F# Major",
            "mood": "Opulent, restrained, sovereign, quiet luxury",
            "instrumentation": "Solo acoustic grand piano, delicate chamber strings, warm sub-bass, subtle vinyl texture",
            "reference_style": "Max Richter, Jóhann Jóhannsson (Succession / The Crown aesthetic)"
        },
        "financial_asymmetry": {
            "tempo_bpm": "95-110 BPM",
            "key": "D Minor",
            "mood": "Calculated risk, strategic tension, market dominance",
            "instrumentation": "Fast muted cello arpeggios, analog clockwork percussion, sub-bass riser",
            "reference_style": "Cliff Martinez (The Lincoln Lawyer), Trent Reznor (The Social Network)"
        },
        "mental_focus": {
            "tempo_bpm": "80-92 BPM",
            "key": "A Minor",
            "mood": "Monastic clarity, unbroken concentration, cognitive momentum",
            "instrumentation": "Repetitive acoustic guitar ostinato, muted glass marimba, rhythmic analog synth pulse",
            "reference_style": "Nils Frahm, Ólafur Arnalds, Dustin O'Halloran"
        },
        "mental_burnout": {
            "tempo_bpm": "60-72 BPM",
            "key": "C Minor",
            "mood": "Claustrophobic, exhausted, sensory overwhelm",
            "instrumentation": "Detuned felt piano, tape saturation flutter, sub-harmonic rumble",
            "reference_style": "Hauschka, Hildur Guðnadóttir (Chernobyl / Joker)"
        },
        "stoic_clarity": {
            "tempo_bpm": "60-75 BPM",
            "key": "D Major / F# Minor",
            "mood": "Serene, immovable, transcendent stillness",
            "instrumentation": "Warm ambient pads, bowing glass, gentle acoustic cello, spacious silence",
            "reference_style": "Brian Eno, Stars of the Lid, Arvo Pärt"
        },
        "wellness_vitality": {
            "tempo_bpm": "100-115 BPM",
            "key": "E Major",
            "mood": "Invigorating, primal, physical resilience",
            "instrumentation": "Organic percussion, breath textures, soaring harmonic strings, bright acoustic resonance",
            "reference_style": "Ludovico Einaudi, Jon Hopkins (Singularity)"
        },
        "recovery_restoration": {
            "tempo_bpm": "55-68 BPM",
            "key": "G Major",
            "mood": "Profound restorative ease, parasympathetic warmth, peaceful twilight",
            "instrumentation": "Warm analog synth drone, muted upright piano with felt dampers, singing bowl decay",
            "reference_style": "Marconi Union (Weightless), Harold Budd"
        }
    }

    def analyze_score_trajectory(self, units: List[VisualUnit]) -> List[Dict[str, Any]]:
        """
        Calculates score transitions across the script narrative timeline.
        """
        score_cues = []
        cumulative_time = 0

        for idx, u in enumerate(units):
            start_sec = cumulative_time
            end_sec = cumulative_time + u.duration_sec
            cumulative_time = end_sec

            motif = u.visual_strategy.get("motif", "scale") if hasattr(u, "visual_strategy") else "scale"
            profile = self.EMOTIONAL_MUSIC_PROFILES.get(motif, self.EMOTIONAL_MUSIC_PROFILES["scale"])

            # Search local studio music library first
            local_matches = local_media_provider.search(motif, asset_type="music", limit=1)
            if not local_matches:
                local_matches = local_media_provider.search("ambient", asset_type="music", limit=1)

            if local_matches:
                matched_asset = MediaAsset(
                    title=local_matches[0]["title"],
                    asset_type="music",
                    source="Local Studio Music Vault",
                    url=local_matches[0]["url"],
                    local_path=local_matches[0].get("local_path"),
                    duration=f"{u.duration_sec}s",
                    license="Internal Master",
                    relevance_score=0.95,
                    why_reason=f"Studio theme matching {motif} arc."
                )
            else:
                matched_asset = MediaAsset(
                    title=f"Score Cue: {motif.title()} Atmosphere",
                    asset_type="music",
                    source="Production Music Library",
                    url=f"https://freemusicarchive.org/search?quicksearch={motif}",
                    duration=f"{u.duration_sec}s",
                    license="Royalty-Free / CC",
                    relevance_score=0.88,
                    why_reason=f"Thematic acoustic bed for {profile['mood']}."
                )

            cue = {
                "cue_id": f"CUE-{idx+1:02d}",
                "unit_id": u.id,
                "section": u.script_section,
                "timecode_range": f"{start_sec//60:02d}:{start_sec%60:02d} — {end_sec//60:02d}:{end_sec%60:02d}",
                "start_sec": start_sec,
                "end_sec": end_sec,
                "thematic_motif": motif,
                "tempo": profile["tempo_bpm"],
                "musical_key": profile["key"],
                "emotional_mood": profile["mood"],
                "instrumentation": profile["instrumentation"],
                "reference_style": profile["reference_style"],
                "matched_asset": matched_asset
            }
            score_cues.append(cue)

        return score_cues


music_score_engine = MusicScoreEngine()
