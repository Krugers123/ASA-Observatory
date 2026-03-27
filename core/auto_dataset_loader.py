import json
from pathlib import Path

def load_dataset_folder(engine, folder="conversation"):
    folder_path = Path(folder)

    if not folder_path.exists():
        print(f"[ASA] dataset folder not found: {folder}")
        return

    files = list(folder_path.glob("*.json"))

    if not files:
        print("[ASA] no dataset files found")
        return

    print(f"[ASA] loading dataset: {len(files)} files")

    for file in files:
        try:
            payload = json.loads(file.read_text())

            session_id = payload.get("session_id", file.stem)

            anchor = (
                payload.get("anchor_text")
                or payload.get("user_intent")
                or "Maintain semantic stability across the dialogue trajectory."
            )

            constraints = payload.get("constraints", [])

            engine.create_session(session_id, anchor, constraints)

            for turn in payload["turns"]:
                if turn["role"] == "user":
                    engine.add_user_turn(session_id, turn["content"])
                else:
                    engine.add_assistant_turn(session_id, turn["content"])

            print(f"[ASA] loaded session: {session_id}")

        except Exception as e:
            print(f"[ASA] error loading {file.name}: {e}")
