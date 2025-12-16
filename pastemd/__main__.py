"""Application main entry point."""

# When packaged by PyInstaller, this module is executed as a top-level script
# (no package context), so relative imports fail. Fall back to absolute import
# to keep both packaged and source runs working.
if __name__ == "__main__":
    try:
        from .app.app import main  # type: ignore
    except Exception:
        from pastemd.app.app import main  # pragma: no cover
    main()
