"""Interactive terminal client for the Personal Word Repository API."""

from __future__ import annotations

import os
from pathlib import Path

try:
    from .api_client import ApiError, WordRepositoryApiClient
    from .storage import StateStore
    from .study_pack_client import StudyPackClient, StudyPackError
except ImportError:
    from api_client import ApiError, WordRepositoryApiClient
    from storage import StateStore
    from study_pack_client import StudyPackClient, StudyPackError


DEFAULT_API_BASE_URL = os.getenv("WORDREPO_API_BASE_URL", "http://127.0.0.1:5000")
DEFAULT_AUX_SERVICE_BASE_URL = os.getenv(
    "WORDREPO_AUX_SERVICE_BASE_URL",
    "http://127.0.0.1:5050",
)
DEFAULT_STATE_PATH = Path(
    os.getenv("WORDREPO_CLIENT_STATE")
    or str(Path(__file__).with_name("client_state.json"))
)


class TerminalClient:
    """Menu-driven terminal client built on top of the REST API."""

    def __init__(self, api_base_url: str, aux_service_base_url: str, state_path: Path):
        self.api = WordRepositoryApiClient(api_base_url)
        self.study_packs = StudyPackClient(aux_service_base_url)
        self.store = StateStore(state_path)
        self.state = self.store.load()

    def run(self) -> None:
        """Start the main menu loop."""
        self.print_header("Word Repository Terminal Client")
        self.check_api_health()

        while True:
            print("\nMain Menu")
            print("1. Create or load user")
            print("2. Dashboard")
            print("3. Words")
            print("4. Categories")
            print("5. Translations")
            print("6. Parts of speech")
            print("7. Study packs")
            print("8. Quit")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.user_menu()
            elif choice == "2":
                self.dashboard_menu()
            elif choice == "3":
                self.words_menu()
            elif choice == "4":
                self.categories_menu()
            elif choice == "5":
                self.translations_menu()
            elif choice == "6":
                self.parts_of_speech_menu()
            elif choice == "7":
                self.study_packs_menu()
            elif choice == "8":
                print("Goodbye.")
                return
            else:
                print("Please enter a number from 1 to 8.")

    def check_api_health(self) -> None:
        """Verify that the API is reachable before the user starts interacting."""
        try:
            result = self.api.healthz()
            print(f"API health: {result['status']} ({self.api.base_url})")
        except ApiError as error:
            print(f"API check failed: {error}")

    def user_menu(self) -> None:
        """Create a new user or switch the active saved user."""
        while True:
            active_user = self.get_active_user()
            print("\nUser Menu")
            print(f"Active user: {active_user['email'] if active_user else 'None'}")
            print("1. Create new user")
            print("2. Load saved user")
            print("3. Show saved users")
            print("4. Back")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.create_user_flow()
            elif choice == "2":
                self.load_user_flow()
            elif choice == "3":
                self.print_saved_users()
            elif choice == "4":
                return
            else:
                print("Please enter a number from 1 to 4.")

    def dashboard_menu(self) -> None:
        """Display the tracked resource summary for the active user."""
        active_user = self.require_active_user()
        if not active_user:
            return

        words = self.fetch_tracked_words()
        categories = self.fetch_tracked_categories()
        translation_count = sum(len(self.safe_list_translations(word["id"])) for word in words)

        self.print_header("Dashboard")
        print(f"User: {active_user['email']}")
        print(f"Tracked words: {len(words)}")
        print(f"Tracked categories: {len(categories)}")
        print(f"Tracked translations: {translation_count}")

        try:
            pack = self.study_packs.missing_translations_pack(active_user["id"])
            print(f"Words missing translations: {pack['count']} (via study-pack service)")
        except StudyPackError as error:
            print(f"Study-pack service status: unavailable ({error})")

    def words_menu(self) -> None:
        """Create, inspect, update, or delete tracked words."""
        active_user = self.require_active_user()
        if not active_user:
            return

        while True:
            self.print_header("Words")
            self.print_words()
            print("1. Add word")
            print("2. Edit word")
            print("3. Delete word")
            print("4. Select word for translations")
            print("5. Back")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.create_word_flow(active_user["id"])
            elif choice == "2":
                self.edit_word_flow()
            elif choice == "3":
                self.delete_word_flow()
            elif choice == "4":
                self.select_word_flow()
            elif choice == "5":
                return
            else:
                print("Please enter a number from 1 to 5.")

    def categories_menu(self) -> None:
        """Create, inspect, update, or delete tracked categories."""
        active_user = self.require_active_user()
        if not active_user:
            return

        while True:
            self.print_header("Categories")
            self.print_categories()
            print("1. Add category")
            print("2. Edit category")
            print("3. Delete category")
            print("4. Back")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.create_category_flow(active_user["id"])
            elif choice == "2":
                self.edit_category_flow()
            elif choice == "3":
                self.delete_category_flow()
            elif choice == "4":
                return
            else:
                print("Please enter a number from 1 to 4.")

    def translations_menu(self) -> None:
        """Create, inspect, update, or delete translations for the active word."""
        active_word = self.require_active_word()
        if not active_word:
            return

        while True:
            self.print_header(f"Translations for {active_word['text']}")
            self.print_translations(active_word["id"])
            print("1. Add translation")
            print("2. Edit translation")
            print("3. Delete translation")
            print("4. Back")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.create_translation_flow(active_word["id"])
            elif choice == "2":
                self.edit_translation_flow(active_word["id"])
            elif choice == "3":
                self.delete_translation_flow(active_word["id"])
            elif choice == "4":
                return
            else:
                print("Please enter a number from 1 to 4.")

    def parts_of_speech_menu(self) -> None:
        """List the available parts of speech from the API."""
        self.print_header("Parts of Speech")
        try:
            for part in self.api.list_parts_of_speech():
                print(f"- {part['id']}: {part['name']} ({part['code']})")
        except ApiError as error:
            print(f"Could not load parts of speech: {error}")

    def study_packs_menu(self) -> None:
        """Open auxiliary study-pack workflows for the active user."""
        active_user = self.require_active_user()
        if not active_user:
            return

        while True:
            self.print_header("Study Packs")
            print("1. Random study pack")
            print("2. Words missing translations")
            print("3. Study pack by category")
            print("4. Back")

            choice = input("Select an option: ").strip()

            if choice == "1":
                self.show_random_study_pack(active_user["id"])
            elif choice == "2":
                self.show_missing_translations_pack(active_user["id"])
            elif choice == "3":
                self.show_category_study_pack(active_user["id"])
            elif choice == "4":
                return
            else:
                print("Please enter a number from 1 to 4.")

    def create_user_flow(self) -> None:
        email = input("Email: ").strip()
        password = input("Password: ").strip()

        try:
            user = self.api.create_user(email, password)
        except ApiError as error:
            print(f"Could not create user: {error}")
            return

        self.state.users = upsert_user(self.state.users, user)
        self.state.active_user_id = user["id"]
        self.save_state()
        print(f"Created and loaded user {user['email']}.")

    def load_user_flow(self) -> None:
        if not self.state.users:
            print("No saved users yet.")
            return

        self.print_saved_users()
        choice = input("Enter the number of the user to load: ").strip()
        try:
            index = int(choice) - 1
            user = self.state.users[index]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return

        self.state.active_user_id = user["id"]
        self.save_state()
        print(f"Loaded user {user['email']}.")

    def create_word_flow(self, user_id: str) -> None:
        parts = self.prompt_parts_of_speech()
        if not parts:
            return

        text = input("Word text: ").strip()
        language = input("Language code: ").strip()
        part_id = prompt_int("Part of speech ID: ")
        category_ids = self.prompt_category_ids()

        try:
            word = self.api.create_word(
                user_id,
                text,
                language,
                part_id,
                category_ids=category_ids,
            )
        except ApiError as error:
            print(f"Could not create word: {error}")
            return

        self.save_state()
        print(f"Created word {word['text']}.")

    def edit_word_flow(self) -> None:
        words = self.fetch_tracked_words()
        word = self.choose_resource(words, "word")
        if not word:
            return

        print("Leave a field empty to keep the current value.")
        text = input(f"Text [{word['text']}]: ").strip() or word["text"]
        language = input(f"Language [{word['language']}]: ").strip() or word["language"]

        self.prompt_parts_of_speech()
        part_id_input = input(f"Part of speech ID [{word['part_of_speech_id']}]: ").strip()
        part_of_speech_id = int(part_id_input) if part_id_input else word["part_of_speech_id"]

        category_ids = self.prompt_category_ids(allow_empty=True)
        if category_ids is None:
            category_ids = word["categories"]

        try:
            updated = self.api.update_word(
                word["id"],
                user_id=word["user_id"],
                text=text,
                language=language,
                part_of_speech_id=part_of_speech_id,
                category_ids=category_ids,
            )
        except ApiError as error:
            print(f"Could not update word: {error}")
            return

        print(f"Updated word {updated['text']}.")

    def delete_word_flow(self) -> None:
        words = self.fetch_tracked_words()
        word = self.choose_resource(words, "word")
        if not word:
            return

        confirm = input(f"Delete word '{word['text']}'? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Delete cancelled.")
            return

        try:
            self.api.delete_word(word["id"])
        except ApiError as error:
            print(f"Could not delete word: {error}")
            return

        if self.state.active_word_id == word["id"]:
            self.state.active_word_id = None
        self.save_state()
        print("Word deleted.")

    def select_word_flow(self) -> None:
        words = self.fetch_tracked_words()
        word = self.choose_resource(words, "word")
        if not word:
            return

        self.state.active_word_id = word["id"]
        self.save_state()
        print(f"Selected '{word['text']}' for the translations menu.")

    def create_category_flow(self, user_id: str) -> None:
        name = input("Category name: ").strip()
        try:
            category = self.api.create_category(user_id, name)
        except ApiError as error:
            print(f"Could not create category: {error}")
            return

        self.save_state()
        print(f"Created category {category['name']}.")

    def edit_category_flow(self) -> None:
        categories = self.fetch_tracked_categories()
        category = self.choose_resource(categories, "category")
        if not category:
            return

        name = input(f"Category name [{category['name']}]: ").strip() or category["name"]
        try:
            updated = self.api.update_category(
                category["id"],
                user_id=category["user_id"],
                name=name,
            )
        except ApiError as error:
            print(f"Could not update category: {error}")
            return

        print(f"Updated category to {updated['name']}.")

    def delete_category_flow(self) -> None:
        categories = self.fetch_tracked_categories()
        category = self.choose_resource(categories, "category")
        if not category:
            return

        confirm = input(f"Delete category '{category['name']}'? [y/N]: ").strip().lower()
        if confirm != "y":
            print("Delete cancelled.")
            return

        try:
            self.api.delete_category(category["id"])
        except ApiError as error:
            print(f"Could not delete category: {error}")
            return

        self.save_state()
        print("Category deleted.")

    def show_random_study_pack(self, user_id: str) -> None:
        count = prompt_optional_int("Study-pack size [5]: ", default=5)
        try:
            payload = self.study_packs.random_pack(user_id, count)
        except StudyPackError as error:
            print(f"Could not load random study pack: {error}")
            return

        self.print_study_pack(payload)

    def show_missing_translations_pack(self, user_id: str) -> None:
        try:
            payload = self.study_packs.missing_translations_pack(user_id)
        except StudyPackError as error:
            print(f"Could not load missing-translations pack: {error}")
            return

        self.print_study_pack(payload)

    def show_category_study_pack(self, user_id: str) -> None:
        categories = self.fetch_tracked_categories()
        category = self.choose_resource(categories, "category")
        if not category:
            return

        try:
            payload = self.study_packs.category_pack(user_id, category["id"])
        except StudyPackError as error:
            print(f"Could not load category study pack: {error}")
            return

        self.print_study_pack(payload)

    def create_translation_flow(self, word_id: str) -> None:
        text = input("Translation text: ").strip()
        language = input("Language code: ").strip()
        note = input("Note (optional): ").strip() or None

        try:
            translation = self.api.create_translation(word_id, text, language, note=note)
        except ApiError as error:
            print(f"Could not create translation: {error}")
            return

        print(f"Created translation {translation['text']}.")

    def edit_translation_flow(self, word_id: str) -> None:
        translations = self.safe_list_translations(word_id)
        translation = self.choose_resource(translations, "translation")
        if not translation:
            return

        text = input(f"Translation text [{translation['text']}]: ").strip() or translation["text"]
        language = input(f"Language [{translation['language']}]: ").strip() or translation["language"]
        note_prompt = translation["note"] if translation["note"] else ""
        note = input(f"Note [{note_prompt}]: ").strip()
        note_value = note if note else translation["note"]

        try:
            updated = self.api.update_translation(
                translation["id"],
                word_id=translation["word_id"],
                text=text,
                language=language,
                note=note_value,
            )
        except ApiError as error:
            print(f"Could not update translation: {error}")
            return

        print(f"Updated translation {updated['text']}.")

    def delete_translation_flow(self, word_id: str) -> None:
        translations = self.safe_list_translations(word_id)
        translation = self.choose_resource(translations, "translation")
        if not translation:
            return

        confirm = input(
            f"Delete translation '{translation['text']}'? [y/N]: "
        ).strip().lower()
        if confirm != "y":
            print("Delete cancelled.")
            return

        try:
            self.api.delete_translation(translation["id"])
        except ApiError as error:
            print(f"Could not delete translation: {error}")
            return

        print("Translation deleted.")

    def print_saved_users(self) -> None:
        if not self.state.users:
            print("No saved users.")
            return

        for index, user in enumerate(self.state.users, start=1):
            marker = "*" if user["id"] == self.state.active_user_id else " "
            print(f"{index}. [{marker}] {user['email']} ({user['id']})")

    def print_words(self) -> None:
        words = self.fetch_tracked_words()
        if not words:
            print("No tracked words yet.")
            return

        print("\nTracked words")
        for index, word in enumerate(words, start=1):
            marker = "*" if word["id"] == self.state.active_word_id else " "
            print(
                f"{index}. [{marker}] {word['text']} ({word['language']}) "
                f"id={word['id']} pos={word['part_of_speech_id']} "
                f"categories={', '.join(word['categories']) or 'none'}"
            )

    def print_categories(self) -> None:
        categories = self.fetch_tracked_categories()
        if not categories:
            print("No tracked categories yet.")
            return

        print("\nTracked categories")
        for index, category in enumerate(categories, start=1):
            print(
                f"{index}. {category['name']} "
                f"(id={category['id']}, linked words={len(category['words'])})"
            )

    def print_translations(self, word_id: str) -> None:
        translations = self.safe_list_translations(word_id)
        if not translations:
            print("No translations yet.")
            return

        for index, translation in enumerate(translations, start=1):
            note = f" note={translation['note']}" if translation["note"] else ""
            print(
                f"{index}. {translation['text']} ({translation['language']}) "
                f"id={translation['id']}{note}"
            )

    def prompt_parts_of_speech(self) -> list[dict]:
        try:
            parts = self.api.list_parts_of_speech()
        except ApiError as error:
            print(f"Could not load parts of speech: {error}")
            return []

        print("\nAvailable parts of speech")
        for part in parts:
            print(f"- {part['id']}: {part['name']} ({part['code']})")
        return parts

    def prompt_category_ids(self, allow_empty: bool = False) -> list[str] | None:
        categories = self.fetch_tracked_categories()
        if not categories:
            if not allow_empty:
                print("No tracked categories available. Continuing without categories.")
                return []
            return None

        print("\nAvailable categories")
        for category in categories:
            print(f"- {category['id']}: {category['name']}")

        raw_ids = input(
            "Category IDs (comma-separated, leave empty for none"
            f"{' / unchanged' if allow_empty else ''}): "
        ).strip()

        if not raw_ids:
            return None if allow_empty else []

        return [item.strip() for item in raw_ids.split(",") if item.strip()]

    def fetch_tracked_words(self) -> list[dict]:
        user_id = self.state.active_user_id
        if not user_id:
            return []

        try:
            return self.api.list_words(user_id=user_id)
        except ApiError as error:
            print(f"Could not load words: {error}")
            return []

    def fetch_tracked_categories(self) -> list[dict]:
        user_id = self.state.active_user_id
        if not user_id:
            return []

        try:
            return self.api.list_categories(user_id=user_id)
        except ApiError as error:
            print(f"Could not load categories: {error}")
            return []

    def safe_list_translations(self, word_id: str) -> list[dict]:
        try:
            return self.api.list_translations(word_id)
        except ApiError as error:
            print(f"Could not load translations: {error}")
            return []

    def require_active_user(self) -> dict | None:
        user = self.get_active_user()
        if not user:
            print("Create or load a user first.")
            return None
        return user

    def require_active_word(self) -> dict | None:
        if not self.state.active_word_id:
            print("Select a word in the Words menu first.")
            return None

        try:
            return self.api.get_word(self.state.active_word_id)
        except ApiError as error:
            print(f"Could not load the active word: {error}")
            self.state.active_word_id = None
            self.save_state()
            return None

    def get_active_user(self) -> dict | None:
        return next(
            (user for user in self.state.users if user["id"] == self.state.active_user_id),
            None,
        )

    def choose_resource(self, resources: list[dict], label: str) -> dict | None:
        if not resources:
            print(f"No tracked {label}s available.")
            return None

        for index, resource in enumerate(resources, start=1):
            name = resource.get("name") or resource.get("text") or resource["id"]
            print(f"{index}. {name}")

        choice = input(f"Choose a {label} by number: ").strip()
        try:
            return resources[int(choice) - 1]
        except (ValueError, IndexError):
            print("Invalid selection.")
            return None

    def save_state(self) -> None:
        self.store.save(self.state)

    @staticmethod
    def print_header(title: str) -> None:
        line = "=" * len(title)
        print(f"\n{title}\n{line}")

    @staticmethod
    def print_study_pack(payload: dict) -> None:
        """Render a study-pack response in a readable terminal format."""
        print(f"Pack type: {payload['type']}")
        if payload.get("category_name"):
            print(f"Category: {payload['category_name']} ({payload['category_id']})")
        print(f"Items returned: {payload['count']}")

        items = payload.get("items", [])
        if not items:
            print("No study items found.")
            return

        for index, item in enumerate(items, start=1):
            categories = ", ".join(item.get("categories", [])) or "none"
            print(
                f"{index}. {item['text']} ({item['language']}) "
                f"id={item['id']} pos={item['part_of_speech_id']} "
                f"categories={categories}"
            )
            translations = item.get("translations", [])
            if translations:
                rendered = ", ".join(
                    f"{translation['text']} ({translation['language']})"
                    for translation in translations
                )
                print(f"   translations: {rendered}")
            else:
                print("   translations: none")


def upsert_user(users: list[dict[str, str]], next_user: dict[str, str]) -> list[dict[str, str]]:
    """Replace a saved user with the same ID or append a new one."""
    remaining = [user for user in users if user["id"] != next_user["id"]]
    return sorted([*remaining, next_user], key=lambda user: user["email"])


def prompt_int(label: str) -> int:
    """Prompt until the user provides an integer."""
    while True:
        raw_value = input(label).strip()
        try:
            return int(raw_value)
        except ValueError:
            print("Please enter a valid integer.")


def prompt_optional_int(label: str, *, default: int) -> int:
    """Prompt for an integer while allowing an empty default value."""
    while True:
        raw_value = input(label).strip()
        if not raw_value:
            return default
        try:
            return int(raw_value)
        except ValueError:
            print("Please enter a valid integer.")


if __name__ == "__main__":
    client = TerminalClient(
        DEFAULT_API_BASE_URL,
        DEFAULT_AUX_SERVICE_BASE_URL,
        DEFAULT_STATE_PATH,
    )
    client.run()
