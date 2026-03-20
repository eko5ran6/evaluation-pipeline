"""
Legacy entrypoint removed from module import side effects.

Use from the repository root:

    python -m backend.run --gt datasets/Groundtruth_Summary.json \\
        -p datasets/JarvisMD_Summary.json -p path/to/other_model.json --out results

Programmatic use:

    from backend.run import run_evaluation
    from pathlib import Path

    run_evaluation(
        Path("datasets/Groundtruth_Summary.json"),
        [Path("datasets/JarvisMD_Summary.json")],
        Path("results"),
        ("entity_recall", "rouge_l"),
    )
"""
