import sys

import ollama
import psycopg

DATABASE = "dbname=chatbot"
MODEL = "llama3.2"
HISTORY_LIMIT = 20
SYSTEM_PROMPT = (
    "You are a patient cybersecurity tutor helping a student prepare for "
    "CompTIA Security+. Explain concepts clearly, use short examples, and "
    "say when you are unsure instead of guessing."
)


def create_conversation(conn: psycopg.Connection) -> int:
    row = conn.execute(
        "INSERT INTO conversations DEFAULT VALUES RETURNING id"
    ).fetchone()
    return row[0]


def get_latest_conversation(conn: psycopg.Connection) -> int | None:
    row = conn.execute(
        "SELECT id FROM conversations ORDER BY id DESC LIMIT 1"
    ).fetchone()
    return row[0] if row else None


def save_message(
    conn: psycopg.Connection, conversation_id: int, role: str, content: str
) -> None:
    conn.execute(
        "INSERT INTO messages (conversation_id, role, content) VALUES (%s, %s, %s)",
        (conversation_id, role, content),
    )


def load_history(
    conn: psycopg.Connection, conversation_id: int
) -> list[dict[str, str]]:
    rows = conn.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = %s
        ORDER BY id DESC
        LIMIT %s
        """,
        (conversation_id, HISTORY_LIMIT),
    ).fetchall()
    return [{"role": role, "content": content} for role, content in reversed(rows)]


def ask_model(history: list[dict[str, str]]) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, *history]
    response = ollama.chat(model=MODEL, messages=messages)
    return response.message.content


def main() -> None:
    with psycopg.connect(DATABASE, autocommit=True) as conn:
        conversation_id = None
        if "--new" not in sys.argv:
            conversation_id = get_latest_conversation(conn)
        if conversation_id is None:
            conversation_id = create_conversation(conn)

        print(f"Conversation {conversation_id}. Type 'quit' to exit.\n")

        while True:
            try:
                user_message = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if user_message.lower() == "quit":
                break
            if not user_message:
                continue

            save_message(conn, conversation_id, "user", user_message)
            history = load_history(conn, conversation_id)

            try:
                reply = ask_model(history)
            except (ollama.ResponseError, ConnectionError) as error:
                print(f"Could not reach the model: {error}\n")
                continue

            save_message(conn, conversation_id, "assistant", reply)
            print(f"\nTutor: {reply}\n")


if __name__ == "__main__":
    main()