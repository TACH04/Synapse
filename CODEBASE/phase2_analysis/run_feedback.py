from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from modules.behavior_classifier import BehaviorClassifier
from modules.data_models import Conversation, PipelineArtifacts, SpeakerMap, export_json
from modules.dynamics_analyzer import ConversationalDynamicsAnalyzer
from modules.feedback_generator import FeedbackGenerator
from modules.key_moment_analyzer import KeyMomentAnalyzer
from modules.speaker_classifier import SpeakerRoleClassifier

app = typer.Typer(add_completion=False)
console = Console()

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "data" / "outputs"
PROMPTS_DIR = PROJECT_ROOT / "prompts"

DEFAULT_CONFIG: Dict[str, Any] = {
    "ollama": {
        "speaker_role_model": "llama3:8b",
        "key_moment_model": "llama3:8b",
        "feedback_model": "mistral-nemo",
        "timeout_seconds": 180,
    },
    "behavior_classifier": {
        "model_dir": str(PROJECT_ROOT / "models" / "ccae-behavior-classifier-v1"),
        "labels_file": str(
            PROJECT_ROOT / "models" / "ccae-behavior-classifier-v1" / "labels.json"
        ),
        "thresholds_file": str(
            PROJECT_ROOT / "models" / "ccae-behavior-classifier-v1" / "thresholds.json"
        ),
        "batch_size": 8,
        "device": "auto",
    },
}


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s :: %(message)s",
    )


def load_conversation(path: Path) -> Conversation:
    data = json.loads(path.read_text(encoding="utf-8"))
    return Conversation.model_validate(data)


def load_config(config_path: Optional[Path]) -> Dict[str, Any]:
    if not config_path:
        return DEFAULT_CONFIG
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    merged = DEFAULT_CONFIG.copy()
    for key, value in data.items():
        if isinstance(value, dict) and key in merged:
            merged[key] = {**merged[key], **value}
        else:
            merged[key] = value
    return merged


def build_output_paths(base_dir: Path, stem: str) -> Dict[str, Path]:
    conversation_dir = base_dir / stem
    conversation_dir.mkdir(parents=True, exist_ok=True)
    return {
        "root": conversation_dir,
        "speaker_map": conversation_dir / "speaker_map.json",
        "dynamics": conversation_dir / "dynamics.json",
        "behaviors": conversation_dir / "behaviors.json",
        "key_events": conversation_dir / "key_events.json",
        "report": conversation_dir / f"feedback_report_{stem}.md",
    }


@app.command()
def run(
    input: Path = typer.Option(..., exists=True, help="Path to conversation.json"),
    output_dir: Path = typer.Option(DEFAULT_OUTPUT_DIR, help="Directory for pipeline artifacts"),
    clinician: Optional[str] = typer.Option(None, help="Override clinician speaker id"),
    models_config: Optional[Path] = typer.Option(
        None, exists=True, help="Optional YAML file overriding model paths/settings"
    ),
    skip_key_moments: bool = typer.Option(False, help="Disable Module 4"),
    dry_run: bool = typer.Option(False, help="Skip LLM calls and use heuristic fallbacks"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable debug logging"),
) -> None:
    """Run the full Phase 2 pipeline end-to-end."""

    configure_logging(verbose)
    config = load_config(models_config)
    conversation = load_conversation(input)
    paths = build_output_paths(output_dir, input.stem)

    speaker_classifier = SpeakerRoleClassifier(
        prompt_path=PROMPTS_DIR / "speaker_role_prompt.txt",
        model_name=config["ollama"]["speaker_role_model"],
        timeout=config["ollama"]["timeout_seconds"],
    )
    dynamics_analyzer = ConversationalDynamicsAnalyzer()
    behavior_classifier = BehaviorClassifier(
        model_dir=Path(config["behavior_classifier"]["model_dir"]),
        labels_file=Path(config["behavior_classifier"]["labels_file"]),
        thresholds_file=Path(config["behavior_classifier"]["thresholds_file"]),
        batch_size=config["behavior_classifier"]["batch_size"],
        device=config["behavior_classifier"]["device"],
    )
    key_moment_analyzer = KeyMomentAnalyzer(
        prompt_path=PROMPTS_DIR / "key_moment_prompt.txt",
        model_name=config["ollama"]["key_moment_model"],
        timeout=config["ollama"]["timeout_seconds"],
        enabled=not skip_key_moments and not dry_run,
    )
    feedback_generator = FeedbackGenerator(
        prompt_path=PROMPTS_DIR / "feedback_prompt.txt",
        model_name=config["ollama"]["feedback_model"],
        timeout=config["ollama"]["timeout_seconds"],
    )

    steps = ["Speaker role", "Dynamics", "Behavior", "Feedback"]
    if not skip_key_moments and not dry_run:
        steps.insert(3, "Key moments")

    progress = Progress(SpinnerColumn(), TextColumn("[bold blue]{task.description}"), transient=True)

    with progress:
        progress_task = progress.add_task("Running Phase 2 pipeline", total=len(steps))

        # Module 1
        speaker_map = speaker_classifier.classify(
            conversation, clinician_override=clinician, use_model=not dry_run
        )
        export_json(paths["speaker_map"], speaker_map.as_dict())
        progress.advance(progress_task)

        # Module 2
        dynamics = dynamics_analyzer.analyze(conversation, speaker_map)
        export_json(paths["dynamics"], dynamics.as_dict())
        progress.advance(progress_task)

        # Module 3
        behaviors = behavior_classifier.classify(conversation, speaker_map)
        export_json(paths["behaviors"], behaviors.as_dict())
        progress.advance(progress_task)

        # Module 4
        key_events = None
        if not skip_key_moments and not dry_run:
            key_events = key_moment_analyzer.analyze(conversation, behaviors)
            if key_events:
                export_json(paths["key_events"], key_events.as_dict())
            progress.advance(progress_task)

        # Module 5
        artifacts = PipelineArtifacts(
            conversation=conversation,
            speaker_map=speaker_map,
            dynamics=dynamics,
            behaviors=behaviors,
            key_events=key_events,
        )
        report = feedback_generator.generate(artifacts, use_model=not dry_run)
        paths["report"].write_text(report, encoding="utf-8")
        progress.advance(progress_task)

    console.print(
        f"[green]Success![/green] Report generated at [bold]{paths['report']}[/bold]. Intermediate JSON saved in {paths['root']}."
    )


if __name__ == "__main__":
    app()

