import os


def load_markdown() -> str:
    """Reads the provided markdown files and loads it all into a string

    Returns:
        str: All text of all markdown files.
    """
    all_text = ""
    DIRECTORY = "policies"
    for filename in os.listdir(DIRECTORY):
        with open(os.path.join(DIRECTORY, filename), "rt") as f:
            all_text += f.read() + '\n'

    # print("all_text:")
    # print(all_text)

    return all_text