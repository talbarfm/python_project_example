"""A submodule inside a regular package."""

print("hey im the inenr mopdule")
def package_message() -> str:
    # DEMO: This function is imported through package_with_init.__init__.
    return "Imported a regular package: package_with_init"
