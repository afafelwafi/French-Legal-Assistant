# main.py
import argparse
import asyncio
import uvicorn
from api.server import app
from ui.app import launch_ui
from data.loader import LegalDataLoader
from models.vectorstore import VectorstoreManager


async def build_indices(law_codes=None):
    """
    Build indices for the specified law codes or all available ones.

    Args:
        law_codes: Optional list of law code names
    """
    # If no law codes specified, get all available ones
    if law_codes is None or len(law_codes) == 0:
        law_codes = LegalDataLoader.list_available_law_codes()
        print(f"Building indices for all available law codes: {law_codes}")

    for law_code in law_codes:
        print(f"Building index for {law_code}...")

        try:
            # Load documents
            loader = LegalDataLoader(law_code)
            documents = await loader.load()

            # Create vectorstore
            vectorstore_manager = VectorstoreManager(law_code)
            vectorstore = vectorstore_manager.create_vectorstore(documents)

            print(f"Index built for {law_code} with {len(documents)} documents.")
        except FileNotFoundError as e:
            print(f"Error: {str(e)}")
            continue


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="French Legal Assistant")
    parser.add_argument(
        "--mode",
        choices=["api", "ui", "build-indices", "list-codes"],
        default="ui",
        help="Run mode (api, ui, build-indices, or list-codes)",
    )
    parser.add_argument(
        "--law-codes",
        nargs="+",
        default=[],
        help="Law codes to build indices for (if empty, all available codes will be used)",
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Host to bind the API server to"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to bind the API server to"
    )

    args = parser.parse_args()

    if args.mode == "list-codes":
        codes = LegalDataLoader.list_available_law_codes()
        print("Available law codes:")
        for code in codes:
            print(f"- {code}")
    elif args.mode == "build-indices":
        asyncio.run(build_indices(args.law_codes))
    elif args.mode == "api":
        uvicorn.run(app, host=args.host, port=args.port)
    elif args.mode == "ui":
        launch_ui()


if __name__ == "__main__":
    main()
